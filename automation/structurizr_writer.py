"""
Extrait le workspace Structurizr d'une réponse F. Brooks, le valide avec
le parseur officiel (via Docker) et le sauvegarde.

Usage :

    python automation/structurizr_writer.py [--test-id CTX-001] [--json] < reponse.txt

Le writer ne décide jamais du verdict PASS/FAIL.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
STRUCTURIZR_DIR = BASE_DIR / "structurizr"
WORKSPACE_FILE = STRUCTURIZR_DIR / "workspace.dsl"
DSL_RESULTS_DIR = BASE_DIR / "results" / "dsl"

STRUCTURIZR_IMAGE = os.getenv(
    "STRUCTURIZR_IMAGE",
    "structurizr/structurizr:2026.09.19",
)
DOCKER_TIMEOUT = 120

# workspace ["nom"] ["description"] {
WORKSPACE_HEADER = (
    r"\bworkspace"
    r'(?:\s+"(?:\\.|[^"\\])*"){0,2}'
    r"\s*\{"
)


def extract_balanced_workspace(text: str, start: int):
    """Extract a balanced workspace block beginning at ``start``."""
    opening_brace = text.find("{", start)
    if opening_brace == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(opening_brace, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1].strip()
            if depth < 0:
                return None

    return None


def extract_workspace_dsl(answer: str):
    """Extract a Structurizr workspace from a model response."""
    if not answer:
        return None

    workspace_pattern = re.compile(WORKSPACE_HEADER, re.IGNORECASE)
    fenced_patterns = (
        re.compile(
            r"```(?:structurizr|dsl)\s*(.*?)```",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"```(?:[a-zA-Z0-9_-]+)?\s*(.*?)```",
            re.IGNORECASE | re.DOTALL,
        ),
    )

    for pattern in fenced_patterns:
        for match in pattern.finditer(answer):
            block = match.group(1).strip()
            workspace_match = workspace_pattern.search(block)
            if workspace_match:
                workspace = extract_balanced_workspace(
                    block,
                    workspace_match.start(),
                )
                if workspace:
                    return workspace

    workspace_match = workspace_pattern.search(answer)
    if not workspace_match:
        return None

    return extract_balanced_workspace(answer, workspace_match.start())


def validate_dsl(dsl: str) -> bool:
    """Check workspace structure, brace balance, and quoted strings."""
    if not dsl or not re.match(
        r"^\s*" + WORKSPACE_HEADER,
        dsl,
        re.IGNORECASE,
    ):
        return False

    depth = 0
    in_string = False
    escaped = False

    for char in dsl:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False

    return depth == 0 and not in_string and not escaped


def validate_with_structurizr(dsl_file: Path):
    """
    Valide un fichier DSL avec le parseur Structurizr officiel (Docker).

    Retourne (valid, message). valid vaut None si Docker est indisponible.
    """
    if shutil.which("docker") is None:
        return None, "Docker introuvable : validation Structurizr ignorée."

    command = [
        "docker", "run", "--rm",
        "-v", f"{dsl_file.parent}:/w:ro",
        STRUCTURIZR_IMAGE,
        "validate", "-w", f"/w/{dsl_file.name}",
    ]

    try:
        process = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=DOCKER_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None, (
            f"Validation Structurizr interrompue après {DOCKER_TIMEOUT} s."
        )
    except OSError as exc:
        return None, f"Impossible de lancer Docker : {exc}"

    output = (process.stdout + process.stderr).strip()

    if process.returncode == 0:
        return True, "DSL validé par Structurizr."

    errors = [
        line.split(" -- ", 1)[-1]
        for line in output.splitlines()
        if " ERROR " in line
    ]
    if errors:
        return False, "\n".join(errors)

    # Ni succès ni erreur de parsing : problème Docker (daemon arrêté…).
    return None, output or f"docker a retourné {process.returncode}."


def save_workspace(answer: str, test_id: str = None):
    """Extract, validate, and save a workspace from a model response."""
    dsl = extract_workspace_dsl(answer)
    if not dsl:
        return {
            "status": "NO_WORKSPACE",
            "saved": False,
            "reason": "Aucun workspace Structurizr détecté.",
        }

    if not validate_dsl(dsl):
        return {
            "status": "INVALID_DSL",
            "saved": False,
            "reason": "Le DSL détecté est structurellement invalide.",
        }

    DSL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    dsl_file = DSL_RESULTS_DIR / f"{test_id or 'last'}.dsl"
    dsl_file.write_text(dsl + "\n", encoding="utf-8")

    valid, message = validate_with_structurizr(dsl_file)

    result = {
        "dslFile": str(dsl_file),
        "validation": message,
    }

    if valid is False:
        result.update(
            status="INVALID_DSL",
            saved=False,
            reason="Le DSL est rejeté par Structurizr.",
        )
        return result

    STRUCTURIZR_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_FILE.write_text(dsl + "\n", encoding="utf-8")

    result.update(
        status="SAVED" if valid else "SAVED_UNVALIDATED",
        saved=True,
        path=str(WORKSPACE_FILE),
    )
    return result


def print_result(result):
    print("[STRUCTURIZR]")
    if result["saved"]:
        print("Workspace sauvegardé automatiquement :")
        print(result["path"])
    else:
        print(result["reason"])
    if result.get("validation"):
        print(result["validation"])


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--test-id")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Affiche le résultat en JSON (utilisé par run_tests.py).",
    )
    args = parser.parse_args()

    answer = sys.stdin.read()
    if not answer.strip():
        print("Aucune réponse reçue via stdin.", file=sys.stderr)
        sys.exit(1)

    result = save_workspace(answer, args.test_id)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print_result(result)
