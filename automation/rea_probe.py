"""
Résume une analyse REA en bloc <observations> exploitable par F. Brooks.

REA (https://github.com/morluto/rea) produit un graphe d'application
volumineux (modules, chunks, IPC, add-ons natifs...). Ce module n'en garde
que les faits utiles aux niveaux C4 1 et 2 (SPEC.md §14.3) :

    processus Electron, fenêtres, workers   → conteneurs candidats
    endpoints, stockages                     → systèmes externes ou
                                               conteneurs candidats
    canaux IPC                               → relations entre conteneurs

Les modules, chunks, source maps et add-ons natifs relèvent des niveaux 3
et 4 : ils sont comptés, pas listés.

Usage :

    # lance REA puis résume
    python automation/rea_probe.py CHEMIN/app.asar --role STUDIED_SYSTEM

    # résume une sortie REA existante (rea ... --json > evidence.json)
    python automation/rea_probe.py --evidence evidence.json --role REFERENCE

Le bloc est affiché et enregistré dans results/rea/<cible>.txt, le résumé
structuré dans results/rea/<cible>.json.

Le contenu analysé n'est pas fiable : les libellés sont neutralisés et
F. Brooks traite le bloc comme une donnée (SYSTEM_PROMPT.md §27).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
REA_RESULTS_DIR = BASE_DIR / "results" / "rea"

REA_TIMEOUT = 600
ROLES = ("STUDIED_SYSTEM", "EXTERNAL_SYSTEM", "REFERENCE")
MAX_LABEL_LENGTH = 120
MAX_LIMITATIONS = 6

# kind REA → type d'observation affiché
CONTAINER_KINDS = {
    "browser-window": "browser-window",
    "worker": "worker",
    "service-worker": "service-worker",
    "endpoint": "endpoint",
    "storage": "storage",
}

# kinds comptés mais non listés (niveaux 3 et 4)
DETAIL_KINDS = {
    "javascript-module",
    "javascript-asset",
    "javascript-chunk",
    "javascript-expression",
    "source-map",
    "original-source-module",
    "asar-entry",
    "artifact",
    "native-addon",
    "native-export",
}

STATES = {"observed", "inferred", "unknown", "unavailable"}


class ProbeError(Exception):
    """Erreur exploitable par l'utilisateur (REA absent, sortie illisible...)."""


# ============================================================
# REA
# ============================================================

def run_rea(target: Path, integrity_policy: str):
    """Lance `rea analyze-javascript-application` et retourne l'Evidence."""
    executable = shutil.which("rea")
    if executable is None:
        raise ProbeError(
            "Commande `rea` introuvable. Installez REA : "
            "npm install -g --ignore-scripts rea-agents"
        )

    command = [
        executable,
        "analyze-javascript-application",
        str(target),
        "--integrity-policy", integrity_policy,
        "--json",
    ]

    try:
        process = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=REA_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProbeError(
            f"REA a dépassé le délai de {REA_TIMEOUT} secondes."
        ) from exc
    except OSError as exc:
        raise ProbeError(f"Impossible de lancer REA : {exc}") from exc

    evidence = parse_evidence(process.stdout)

    if process.returncode != 0 or "error" in evidence:
        raise ProbeError(
            "REA a échoué : "
            + evidence.get("message", process.stderr.strip()[-500:])
        )

    return evidence


def parse_evidence(text: str):
    """Lit la sortie JSON de REA (un objet, éventuellement précédé de logs)."""
    text = text.strip()
    start = text.find("{")
    if start == -1:
        raise ProbeError("Sortie REA vide ou sans objet JSON.")
    try:
        return json.loads(text[start:])
    except json.JSONDecodeError as exc:
        raise ProbeError(f"Sortie REA illisible : {exc}") from exc


# ============================================================
# RÉSUMÉ
# ============================================================

def clean_label(value) -> str:
    """Neutralise un libellé issu de la cible (donnée non fiable)."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = text.replace("<", "‹").replace(">", "›").replace('"', "'")
    if len(text) > MAX_LABEL_LENGTH:
        text = text[:MAX_LABEL_LENGTH - 1] + "…"
    return text or "?"


def format_location(evidence) -> str:
    """Localisation de la preuve : chemin d'artefact ou source:ligne."""
    location = (evidence or {}).get("location") or {}
    if not location.get("available"):
        return "localisation indisponible"
    value = location.get("value") or {}
    path = value.get("path") or value.get("source") or value.get("url")
    if not path:
        return value.get("kind", "localisation inconnue")
    line = (value.get("start") or {}).get("line")
    return clean_label(f"{path}:{line}" if line else path)


def first_observation(node):
    observations = node.get("observations") or [{}]
    return observations[0]


def node_state(observation) -> str:
    state = (observation.get("evidence") or {}).get("state")
    return state if state in STATES else "unknown"


def summarize(evidence, target_name=None, role=None):
    """Réduit une Evidence REA à un résumé C4 (dict sérialisable)."""
    result = evidence.get("normalized_result") or {}
    graph = result.get("graph")
    if not graph:
        raise ProbeError(
            "Evidence sans graphe d'application "
            "(normalized_result.graph absent)."
        )

    nodes = graph.get("nodes", [])
    kinds = Counter(node.get("kind") for node in nodes)

    application = None
    observations = []
    seen = Counter()

    for node in nodes:
        kind = node.get("kind", "")
        observation = first_observation(node)
        properties = observation.get("properties") or {}

        if kind == "package" and properties.get("path") == "package.json":
            application = {
                "name": clean_label(properties.get("name")),
                "version": clean_label(properties.get("version")),
            }
            continue

        if kind.startswith("electron-"):
            obs_type = kind
        elif kind in CONTAINER_KINDS:
            obs_type = CONTAINER_KINDS[kind]
        else:
            continue

        label = clean_label(
            observation.get("label")
            or properties.get("url")
            or properties.get("path")
        )
        key = (obs_type, label)
        seen[key] += 1
        if seen[key] > 1:
            continue

        observations.append({
            "state": node_state(observation),
            "type": obs_type,
            "label": label,
            "location": format_location(observation.get("evidence")),
        })

    for item in observations:
        count = seen[(item["type"], item["label"])]
        if count > 1:
            item["occurrences"] = count

    ipc = summarize_ipc(nodes, (result.get("summary") or {}).get("ipc") or {})

    coverage = (graph.get("coverage") or {}).get("status") or "unknown"
    limitations = [clean_label(text) for text in graph.get("limitations", [])]

    subject = evidence.get("subject") or {}
    name = target_name or (
        f"{application['name']} {application['version']}"
        if application else subject.get("name", "cible")
    )

    return {
        "source": "rea",
        "target": clean_label(name),
        "role": role,
        "coverage": coverage,
        "evidence_id": evidence.get("evidence_id"),
        "subject_sha256": (subject.get("digest") or {}).get("sha256"),
        "observations": observations,
        "ipc": ipc,
        "details": {
            kind: count
            for kind, count in sorted(kinds.items())
            if kind in DETAIL_KINDS
        },
        "limitations": limitations,
    }


def summarize_ipc(nodes, ipc_summary):
    """Canaux IPC littéraux et relation agrégée renderer → main."""
    channels = {}

    for node in nodes:
        if node.get("kind") not in ("ipc-channel", "ipc-handler"):
            continue
        observation = first_observation(node)
        properties = observation.get("properties") or {}
        channel = properties.get("channel")
        if not channel:
            continue
        entry = channels.setdefault(clean_label(channel), {
            "state": node_state(observation),
            "sides": set(),
            "location": format_location(observation.get("evidence")),
        })
        entry["sides"].add(
            f"{properties.get('side', '?')}:{properties.get('mode', '?')}"
        )

    return {
        "operations": ipc_summary.get("operations", 0),
        "dynamic_operations": ipc_summary.get("dynamic_channel_operations", 0),
        "renderer_transmissions": ipc_summary.get("renderer_transmissions", 0),
        "main_handlers": ipc_summary.get("main_handlers", 0),
        "literal_channels": [
            {
                "channel": channel,
                "state": entry["state"],
                "sides": sorted(entry["sides"]),
                "location": entry["location"],
            }
            for channel, entry in sorted(channels.items())
        ],
    }


# ============================================================
# BLOC <observations>
# ============================================================

def render_block(summary) -> str:
    """Produit le bloc défini par SPEC.md §14.4."""
    attributes = f'source="rea" target="{summary["target"]}"'
    if summary.get("role"):
        attributes += f' role="{summary["role"]}"'
    attributes += f' coverage="{summary["coverage"]}"'

    lines = [f"<observations {attributes}>"]

    for item in summary["observations"]:
        occurrences = (
            f" (×{item['occurrences']})" if item.get("occurrences") else ""
        )
        lines.append(
            f'- [{item["state"]}] {item["type"]} "{item["label"]}"'
            f'{occurrences} — {item["location"]}'
        )

    ipc = summary["ipc"]
    if ipc["operations"]:
        state = "inferred" if ipc["main_handlers"] else "unknown"
        lines.append(
            f'- [{state}] relation "renderer" -> "electron-main" '
            f'(IPC : {ipc["operations"]} opérations, '
            f'{ipc["dynamic_operations"]} à canal dynamique non résolu)'
        )
        for channel in ipc["literal_channels"]:
            lines.append(
                f'- [{channel["state"]}] ipc-channel "{channel["channel"]}" '
                f'({", ".join(channel["sides"])}) — {channel["location"]}'
            )

    if not summary["observations"] and not ipc["operations"]:
        lines.append("- aucun conteneur, endpoint ni stockage observé")

    if summary["details"]:
        details = ", ".join(
            f"{kind} {count}" for kind, count in summary["details"].items()
        )
        lines.append(f"détails non représentés (niveaux 3-4) : {details}")

    limitations = summary["limitations"]
    shown = limitations[:MAX_LIMITATIONS]
    if len(limitations) > MAX_LIMITATIONS:
        shown.append(f"(+{len(limitations) - MAX_LIMITATIONS} autres)")
    lines.append("limitations: " + ("; ".join(shown) or "aucune"))

    lines.append("</observations>")
    return "\n".join(lines)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return slug or "cible"


def save(summary, block):
    REA_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = slugify(summary["target"])
    json_file = REA_RESULTS_DIR / f"{slug}.json"
    block_file = REA_RESULTS_DIR / f"{slug}.txt"
    json_file.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    block_file.write_text(block + "\n", encoding="utf-8")
    return json_file, block_file


# ============================================================
# MAIN
# ============================================================

def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "target",
        nargs="?",
        help="Dossier ou fichier .asar d'une application JavaScript/Electron",
    )
    parser.add_argument(
        "--evidence",
        help="Sortie JSON de REA déjà produite (au lieu de lancer REA)",
    )
    parser.add_argument(
        "--role",
        choices=ROLES,
        help="Rôle de la cible (SPEC.md §4.8). Sans rôle, F. Brooks le demandera.",
    )
    parser.add_argument("--name", help="Nom de la cible affiché à F. Brooks")
    parser.add_argument(
        "--integrity-policy",
        default="record-and-continue",
        choices=("fail", "record-and-continue"),
        help=(
            "Comportement de REA si l'intégrité ASAR est contredite "
            "(binaires natifs signés après empaquetage)"
        ),
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="N'enregistre pas le résultat dans results/rea/",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Affiche le résumé structuré au lieu du bloc",
    )
    args = parser.parse_args(argv)

    if bool(args.target) == bool(args.evidence):
        parser.error("indiquez soit une cible, soit --evidence.")

    try:
        if args.evidence:
            evidence = parse_evidence(
                Path(args.evidence).read_text(encoding="utf-8")
            )
        else:
            evidence = run_rea(Path(args.target), args.integrity_policy)
        summary = summarize(evidence, args.name, args.role)
    except (ProbeError, OSError) as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 1

    block = render_block(summary)

    if not args.role:
        print(
            "⚠ Aucun rôle indiqué : F. Brooks demandera le rôle de la cible.",
            file=sys.stderr,
        )

    if not args.no_save:
        json_file, block_file = save(summary, block)
        print(f"Résumé : {json_file}\nBloc   : {block_file}", file=sys.stderr)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(block)

    return 0


if __name__ == "__main__":
    sys.exit(main())
