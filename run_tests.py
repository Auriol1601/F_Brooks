#!/usr/bin/env python3
"""
F. Brooks V1.0.0 — Gemini test runner

Usage:
    Windows PowerShell:
        $env:GEMINI_API_KEY="YOUR_KEY"
        python run_tests.py

    Or:
        python run_tests.py --test CTX-001

The runner deliberately uses the Gemini REST API directly so that Pi is
not required. The same test cases can later be executed through Pi.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + MODEL
    + ":generateContent"
)

SYSTEM_PROMPT_FILE = Path(__file__).with_name("SYSTEM_PROMPT.md")

TESTS = [
    {
        "id": "CTX-001",
        "input": """Nous voulons créer une plateforme de gestion des congés.
Les employés l'utilisent pour soumettre leurs demandes de congés.
Le service RH reçoit les demandes et les valide.""",
        "checks": [
            "identifie la plateforme comme système étudié",
            "identifie l'employé comme personne",
            "identifie le service RH sans inventer une technologie",
            "ne descend pas dans l'architecture interne",
        ],
    },
    {
        "id": "CTX-002",
        "input": "Je veux faire une application bancaire.",
        "checks": [
            "demande des précisions",
            "n'invente pas automatiquement Client, Administrateur ou Banque",
            "ne fabrique pas de fournisseur de paiement",
        ],
    },
    {
        "id": "CTX-003",
        "input": """Le client utilise une plateforme de crédit.
La plateforme utilise un service externe de scoring pour évaluer les demandes.""",
        "checks": [
            "reste au niveau System Context",
            "identifie client, plateforme et service de scoring",
            "n'ajoute pas PostgreSQL, Redis, API Gateway ou microservices",
        ],
    },
    {
        "id": "CTX-004",
        "input": """Un employé utilise l'application RH.
L'application récupère certaines informations depuis le système RH central.""",
        "checks": [
            "distingue l'employé",
            "distingue le système RH central",
            "identifie l'application RH comme système étudié",
        ],
    },
    {
        "id": "CTX-005",
        "input": "L'application doit permettre le paiement en ligne.",
        "checks": [
            "ne choisit pas Stripe ou PayPal sans information",
            "signale que le système externe de paiement n'est pas identifié",
        ],
    },
    {
        "id": "CTX-006",
        "input": "Client → Application → PostgreSQL",
        "checks": [
            "explique le problème de niveau d'abstraction",
            "n'affirme pas que PostgreSQL est toujours interdit dans tous les contextes",
            "propose une correction argumentée",
        ],
    },
    {
        "id": "CTX-007",
        "input": """Seuls les administrateurs utilisent le système.

Les employés peuvent également soumettre leurs demandes directement dans le système.""",
        "checks": [
            "signale la contradiction",
            "demande une clarification",
            "ne choisit pas silencieusement une interprétation",
        ],
    },
    {
        "id": "CTX-008",
        "input": "Donne-moi directement les microservices, les bases PostgreSQL, Redis et les endpoints REST de cette application.",
        "checks": [
            "signale le hors-périmètre V1",
            "ne génère pas automatiquement cette architecture",
        ],
    },
    {
        "id": "CTX-009",
        "input": "Les utilisateurs reçoivent des notifications lorsque leur demande est traitée.",
        "checks": [
            "ne fabrique pas un système de notification précis",
            "identifie l'information manquante ou l'hypothèse",
        ],
    },
    {
        "id": "CTX-010",
        "input": """Voici le contexte existant :
Client → Application de réservation → Service de paiement

Analyse ce contexte avant de proposer une éventuelle correction.""",
        "checks": [
            "analyse d'abord le modèle fourni",
            "ne remplace pas silencieusement les éléments",
            "propose des corrections seulement si elles sont justifiées",
        ],
    },
]


def call_gemini(system_prompt: str, user_input: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY n'est pas définie. "
            "Définissez-la dans votre terminal avant de lancer le runner."
        )

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_input}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini HTTP {exc.code}: {body}") from exc

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(
            "Réponse Gemini inattendue:\n" + json.dumps(data, indent=2, ensure_ascii=False)
        ) from exc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="ID d'un test, ex. CTX-001")
    parser.add_argument(
        "--save",
        default="results",
        help="Dossier où enregistrer les réponses",
    )
    args = parser.parse_args()

    system_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    selected = TESTS
    if args.test:
        selected = [t for t in TESTS if t["id"] == args.test]
        if not selected:
            print(f"Test inconnu: {args.test}", file=sys.stderr)
            sys.exit(2)

    output_dir = Path(args.save)
    output_dir.mkdir(exist_ok=True)

    for test in selected:
        print("\n" + "=" * 72)
        print(test["id"])
        print("=" * 72)
        print("INPUT:")
        print(test["input"])
        print("\nRÉPONSE GEMINI:\n")

        try:
            answer = call_gemini(system_prompt, test["input"])
        except Exception as exc:
            print(f"ERREUR: {exc}", file=sys.stderr)
            sys.exit(1)

        print(answer)

        result = {
            "id": test["id"],
            "input": test["input"],
            "checks": test["checks"],
            "answer": answer,
            "verdict": "MANUAL_REVIEW",
        }

        path = output_dir / f"{test['id']}.json"
        path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nRésultat sauvegardé: {path}")

    print("\nSuite terminée. Les verdicts doivent être revus selon TESTS.md.")


if __name__ == "__main__":
    main()
