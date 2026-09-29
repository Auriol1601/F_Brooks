#!/usr/bin/env python3

"""
F. Brooks — Gemini test runner

Pipeline :

    SYSTEM_PROMPT.md
          ↓
        Gemini
          ↓
    réponse F. Brooks
          ↓
      Structurizr
          ↓
    Gemini Evaluator
          ↓
 PASS / FAIL / EVALUATION_ERROR
          ↓
 results/CTX-XXX.json

Usage:

    Windows CMD:
        set GEMINI_API_KEY=YOUR_KEY
        python run_tests.py --test CTX-005

    Windows PowerShell:
        $env:GEMINI_API_KEY="YOUR_KEY"
        python run_tests.py --test CTX-005

    Toute la suite:
        python run_tests.py

    Test individuel:
        python run_tests.py --test CTX-005

    Dossier de sortie personnalisé:
        python run_tests.py --save results
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + MODEL
    + ":generateContent"
)

SYSTEM_PROMPT_FILE = Path(__file__).with_name(
    "SYSTEM_PROMPT.md"
)

STRUCTURIZR_WRITER = (
    Path(__file__).parent
    / "automation"
    / "structurizr_writer.py"
)

MAX_EVALUATOR_RETRIES = 2
GEMINI_TIMEOUT = 120

ALLOWED_CONTEXT_STATES = {
    "SUFFICIENT",
    "INSUFFICIENT",
    "AMBIGUOUS",
    "CONTRADICTORY",
    "OUT_OF_SCOPE",
}

ALLOWED_VERDICTS = {
    "PASS",
    "FAIL",
}


# ============================================================
# TESTS
# ============================================================

TESTS = [

    {
        "id": "CTX-001",

        "input": """Nous voulons créer une plateforme de gestion des congés.
Les employés l'utilisent pour soumettre leurs demandes de congés.
Le service RH reçoit les demandes et les valide.""",

        "expected": {
            "contextState": "SUFFICIENT",

            "must": [
                "identify_studied_system",
                "identify_employee",
                "identify_hr_service",
                "identify_employee_relationship",
                "identify_hr_relationship",
            ],

            "must_not": [
                "invent_internal_architecture",
                "invent_external_system",
            ],
        },
    },

    {
        "id": "CTX-002",

        "input": "Je veux faire une application bancaire.",

        "expected": {
            "contextState": "INSUFFICIENT",

            "must": [
                "ask_clarification",
                "recognize_missing_context",
            ],

            "must_not": [
                "invent_client",
                "invent_administrator",
                "invent_bank",
                "invent_payment_provider",
            ],
        },
    },

    {
        "id": "CTX-003",

        "input": """Le client utilise une plateforme de crédit.
La plateforme utilise un service externe de scoring pour évaluer les demandes.""",

        "expected": {
            "contextState": "SUFFICIENT",

            "must": [
                "identify_client",
                "identify_credit_platform",
                "identify_scoring_system",
                "identify_context_relationships",
            ],

            "must_not": [
                "invent_postgresql",
                "invent_redis",
                "invent_api_gateway",
                "invent_microservices",
            ],
        },
    },

    {
        "id": "CTX-004",

        "input": """Un employé utilise l'application RH.
L'application récupère certaines informations depuis le système RH central.""",

        "expected": {
            "contextState": "SUFFICIENT",

            "must": [
                "identify_employee",
                "identify_hr_application",
                "identify_hr_central_system",
                "distinguish_person_from_external_system",
                "identify_context_relationships",
            ],

            "must_not": [
                "invent_internal_architecture",
            ],
        },
    },

    {
        "id": "CTX-005",

        "input": "L'application doit permettre le paiement en ligne.",

        "expected": {
            "contextState": "INSUFFICIENT",

            "must": [
                "recognize_unidentified_payment_system",
            ],

            "must_not": [
                "invent_stripe",
                "invent_paypal",
                "invent_payment_provider",
            ],
        },
    },

    {
        "id": "CTX-006",

        "input": "Client → Application → PostgreSQL",

        "expected": {
            "contextState": "AMBIGUOUS",

            "must": [
                "identify_abstraction_issue",
                "explain_context_level",
                "propose_argumented_correction",
            ],

            "must_not": [
                "treat_postgresql_as_person",
                "treat_postgresql_as_external_system_without_context",
                "claim_postgresql_is_always_forbidden",
            ],
        },
    },

    {
        "id": "CTX-007",

        "input": """Seuls les administrateurs utilisent le système.

Les employés peuvent également soumettre leurs demandes directement dans le système.""",

        "expected": {
            "contextState": "CONTRADICTORY",

            "must": [
                "detect_contradiction",
                "ask_clarification",
            ],

            "must_not": [
                "silently_choose_interpretation",
            ],
        },
    },

    {
        "id": "CTX-008",

        "input": """Donne-moi directement les microservices, les bases PostgreSQL,
Redis et les endpoints REST de cette application.""",

        "expected": {
            "contextState": "OUT_OF_SCOPE",

            "must": [
                "identify_out_of_scope_request",
                "explain_v1_boundary",
            ],

            "must_not": [
                "generate_microservices",
                "generate_database_architecture",
                "generate_rest_endpoints",
            ],
        },
    },

    {
        "id": "CTX-009",

        "input": """Les utilisateurs reçoivent des notifications lorsque leur demande
est traitée.""",

        "expected": {
            "contextState": "AMBIGUOUS",

            "must": [
                "identify_notification_requirement",
                "identify_missing_notification_system",
            ],

            "must_not": [
                "invent_email_system",
                "invent_sms_system",
                "invent_push_system",
                "invent_notification_provider",
            ],
        },
    },

    {
        "id": "CTX-010",

        "input": """Voici le contexte existant :

Client → Application de réservation → Service de paiement

Analyse ce contexte avant de proposer une éventuelle correction.""",

        "expected": {
            "contextState": "SUFFICIENT",

            "must": [
                "analyze_existing_model",
                "preserve_user_elements",
                "trace_proposed_corrections",
            ],

            "must_not": [
                "silently_replace_client",
                "silently_replace_booking_application",
                "silently_replace_payment_system",
            ],
        },
    },
]


# ============================================================
# UTILITAIRES
# ============================================================

def json_dumps(data):
    """Convertit un objet Python en JSON lisible."""
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )


def extract_json(text):
    """
    Extrait un objet JSON même si Gemini l'entoure de
    ```json ... ```
    """

    if not text:
        raise ValueError(
            "Réponse JSON vide."
        )

    cleaned = text.strip()

    # --------------------------------------------------------
    # Cas 1 : JSON pur
    # --------------------------------------------------------

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Cas 2 : bloc Markdown ```json ... ```
    # --------------------------------------------------------

    fenced = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        cleaned,
        flags=re.DOTALL,
    )

    if fenced:

        try:
            return json.loads(
                fenced.group(1)
            )

        except json.JSONDecodeError:
            pass

    # --------------------------------------------------------
    # Cas 3 : recherche d'un objet JSON équilibré
    # --------------------------------------------------------

    start = cleaned.find("{")

    if start == -1:
        raise ValueError(
            "Aucun objet JSON trouvé dans la réponse."
        )

    depth = 0
    in_string = False
    escaped = False

    for index in range(
        start,
        len(cleaned),
    ):

        char = cleaned[index]

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

                candidate = cleaned[
                    start:index + 1
                ]

                try:
                    return json.loads(
                        candidate
                    )

                except json.JSONDecodeError as exc:

                    raise ValueError(
                        "Objet JSON trouvé mais invalide."
                    ) from exc

    raise ValueError(
        "Objet JSON incomplet ou non équilibré."
    )


# ============================================================
# GEMINI
# ============================================================

def call_gemini(
    system_prompt,
    user_input,
    *,
    temperature=0.2,
    timeout=GEMINI_TIMEOUT,
):
    """
    Appel Gemini REST API.

    Les erreurs sont propagées afin que l'appelant puisse
    distinguer une erreur fonctionnelle d'une erreur technique.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY n'est pas définie. "
            "Définissez-la dans votre terminal avant "
            "de lancer le runner."
        )

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": system_prompt
                }
            ]
        },

        "contents": [
            {
                "role": "user",

                "parts": [
                    {
                        "text": user_input
                    }
                ],
            }
        ],

        "generationConfig": {
            "temperature": temperature,
        },
    }

    request = urllib.request.Request(
        API_URL,

        data=json.dumps(
            payload
        ).encode("utf-8"),

        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },

        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Gemini HTTP {exc.code}: {body}"
        ) from exc

    except (
        urllib.error.URLError,
        ConnectionError,
        TimeoutError,
        OSError,
    ) as exc:

        raise RuntimeError(
            f"Erreur de connexion Gemini : {exc}"
        ) from exc

    try:

        return (
            data["candidates"][0]
            ["content"]
            ["parts"][0]
            ["text"]
        )

    except (
        KeyError,
        IndexError,
        TypeError,
    ) as exc:

        raise RuntimeError(
            "Réponse Gemini inattendue:\n"
            + json_dumps(data)
        ) from exc


# ============================================================
# EVALUATEUR
# ============================================================

EVALUATOR_SYSTEM_PROMPT = """
Tu es l'évaluateur automatique de F. Brooks.

Ta mission est d'évaluer une réponse produite par F. Brooks
uniquement selon les critères explicites du test fourni.

IMPORTANT :

Le verdict du test et le contextState de F. Brooks sont
deux notions indépendantes.

contextState autorisés :

- SUFFICIENT
- INSUFFICIENT
- AMBIGUOUS
- CONTRADICTORY
- OUT_OF_SCOPE

Verdicts autorisés :

- PASS
- FAIL

Règles :

1. PASS signifie que la réponse respecte les critères du test.

2. FAIL signifie que la réponse viole au moins un critère
   important du test.

3. Un contextState INSUFFICIENT peut parfaitement produire
   un verdict PASS si le test attend que l'insuffisance
   soit détectée.

4. Un contextState AMBIGUOUS peut parfaitement produire
   un verdict PASS si le test attend que l'ambiguïté
   soit détectée.

5. Un contextState CONTRADICTORY peut parfaitement produire
   un verdict PASS si le test attend que la contradiction
   soit détectée.

6. Un contextState OUT_OF_SCOPE peut parfaitement produire
   un verdict PASS si le test attend que la demande
   hors périmètre soit détectée.

7. Ne juge jamais une réponse FAIL simplement parce que
   son contextState est INSUFFICIENT, AMBIGUOUS,
   CONTRADICTORY ou OUT_OF_SCOPE.

8. Ne récompense pas l'invention d'informations.

9. Une information plausible mais non fournie par
   l'utilisateur doit être considérée comme une invention
   si le test interdit cette invention.

10. Le verdict doit porter sur le comportement observable.

11. Une erreur technique de l'évaluateur n'est PAS un FAIL.
    Cette erreur est gérée par le runner sous le statut
    EVALUATION_ERROR.

Retourne exclusivement un objet JSON avec cette structure :

{
  "verdict": "PASS",
  "contextState": "SUFFICIENT",
  "criteria": {
    "must": {},
    "must_not": {}
  },
  "failedCriteria": [],
  "reason": "..."
}

Le champ verdict doit obligatoirement être PASS ou FAIL.

Le champ contextState doit obligatoirement être l'un des
cinq états autorisés.

Ne retourne aucun texte avant ou après le JSON.
"""


def build_evaluator_prompt(
    test,
    answer,
):
    """
    Construit le prompt envoyé à Gemini Evaluator.
    """

    return f"""
Évalue la réponse de F. Brooks pour le test suivant.

TEST ID :
{test["id"]}

INPUT UTILISATEUR :
{test["input"]}

CRITÈRES ATTENDUS :
{json_dumps(test["expected"])}

RÉPONSE DE F. BROOKS :
{answer}

Évalue précisément :

- les critères "must" ;
- les critères "must_not" ;
- le contextState déclaré ou déductible de la réponse ;
- la fidélité aux informations fournies ;
- l'absence d'invention ;
- le respect du périmètre C4 System Context.

Retourne uniquement le JSON demandé.
"""


def evaluation_error(
    reason,
    failed_criteria=None,
    *,
    raw_evaluator_response=None,
):
    """
    Construit un résultat d'erreur technique.

    IMPORTANT :
    EVALUATION_ERROR n'est ni PASS ni FAIL.
    """

    result = {
        "verdict": "EVALUATION_ERROR",

        "contextState": "UNKNOWN",

        "criteria": {
            "must": {},
            "must_not": {},
        },

        "failedCriteria": (
            failed_criteria
            or ["evaluator_error"]
        ),

        "reason": str(reason),
    }

    if raw_evaluator_response is not None:
        result[
            "rawEvaluatorResponse"
        ] = raw_evaluator_response

    return result


def validate_evaluation(
    evaluation
):
    """
    Vérifie que Gemini Evaluator a retourné
    un résultat exploitable.
    """

    if not isinstance(
        evaluation,
        dict,
    ):

        return evaluation_error(
            "La réponse de l'évaluateur "
            "n'est pas un objet JSON."
        )

    verdict = evaluation.get(
        "verdict"
    )

    if verdict not in ALLOWED_VERDICTS:

        return evaluation_error(
            "Verdict retourné par "
            "l'évaluateur invalide : "
            + repr(verdict),

            ["invalid_evaluator_verdict"],

            raw_evaluator_response=evaluation,
        )

    context_state = evaluation.get(
        "contextState"
    )

    if context_state not in ALLOWED_CONTEXT_STATES:

        return evaluation_error(
            "contextState retourné par "
            "l'évaluateur invalide : "
            + repr(context_state),

            ["invalid_context_state"],

            raw_evaluator_response=evaluation,
        )

    criteria = evaluation.get(
        "criteria"
    )

    if not isinstance(
        criteria,
        dict,
    ):

        criteria = {
            "must": {},
            "must_not": {},
        }

    failed_criteria = evaluation.get(
        "failedCriteria",
        [],
    )

    if not isinstance(
        failed_criteria,
        list,
    ):

        failed_criteria = [
            str(failed_criteria)
        ]

    reason = evaluation.get(
        "reason",
        "",
    )

    return {
        "verdict": verdict,

        "contextState": context_state,

        "criteria": criteria,

        "failedCriteria": failed_criteria,

        "reason": str(reason),
    }


def evaluate_test(
    test,
    answer,
):
    """
    Évalue la réponse de F. Brooks.

    Trois résultats sont possibles :

        PASS
        FAIL
        EVALUATION_ERROR

    Une erreur réseau, une réponse JSON invalide ou un
    résultat d'évaluateur incohérent donne EVALUATION_ERROR.

    Cela évite de transformer un problème d'infrastructure
    en échec fonctionnel de F. Brooks.
    """

    evaluator_prompt = build_evaluator_prompt(
        test,
        answer,
    )

    last_error = None

    for attempt in range(
        1,
        MAX_EVALUATOR_RETRIES + 1,
    ):

        try:

            evaluator_answer = call_gemini(
                EVALUATOR_SYSTEM_PROMPT,
                evaluator_prompt,
                temperature=0.0,
            )

            evaluation = extract_json(
                evaluator_answer
            )

            validated = validate_evaluation(
                evaluation
            )

            return validated

        except Exception as exc:

            last_error = exc

            if attempt < MAX_EVALUATOR_RETRIES:

                print(
                    f"⚠ Évaluateur indisponible "
                    f"(tentative {attempt}/"
                    f"{MAX_EVALUATOR_RETRIES})"
                )

                time.sleep(2)

    return evaluation_error(
        last_error
        or "Erreur inconnue de l'évaluateur.",

        ["evaluator_error"],
    )


# ============================================================
# STRUCTURIZR
# ============================================================

def run_structurizr_writer(
    answer
):
    """
    Envoie la réponse de F. Brooks au writer Structurizr.

    Le writer est responsable de l'extraction et de la
    validation DSL.

    Il ne décide jamais du verdict PASS/FAIL.
    """

    if not STRUCTURIZR_WRITER.exists():

        return {
            "status": "NOT_AVAILABLE",

            "message": (
                "structurizr_writer.py introuvable : "
                f"{STRUCTURIZR_WRITER}"
            ),
        }

    try:

        process = subprocess.run(
            [sys.executable, str(STRUCTURIZR_WRITER)],
            input=answer,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

    except subprocess.TimeoutExpired:

        return {
            "status": "ERROR",

            "message": (
                "Le writer Structurizr a dépassé "
                "le délai de 60 secondes."
            ),
        }

    except OSError as exc:

        return {
            "status": "ERROR",

            "message": (
                f"Impossible d'exécuter Structurizr : {exc}"
            ),
        }

    stdout = process.stdout.strip()
    stderr = process.stderr.strip()

    if process.returncode != 0:

        return {
            "status": "ERROR",

            "returncode": process.returncode,

            "stdout": stdout,

            "stderr": stderr,
        }

    return {
        "status": "SUCCESS",

        "returncode": process.returncode,

        "stdout": stdout,

        "stderr": stderr,
    }


# ============================================================
# AFFICHAGE
# ============================================================

def print_evaluation(
    evaluation
):
    """
    Affiche le résultat de l'évaluation.
    """

    print("\n— ÉVALUATION")

    verdict = evaluation.get(
        "verdict"
    )

    if verdict == "EVALUATION_ERROR":

        print(
            "⚠ Évaluation impossible"
        )

        print(
            "Statut       : EVALUATION_ERROR"
        )

        print(
            "Raison       : "
            + evaluation.get(
                "reason",
                "",
            )
        )

        return

    print(
        "Context state : "
        + str(
            evaluation.get(
                "contextState",
                "UNKNOWN",
            )
        )
    )

    print(
        "Verdict       : "
        + str(verdict)
    )

    failed = evaluation.get(
        "failedCriteria",
        [],
    )

    if failed:

        print(
            "Critères échoués :"
        )

        for criterion in failed:

            print(
                f"  - {criterion}"
            )

    print(
        "Raison        : "
        + str(
            evaluation.get(
                "reason",
                "",
            )
        )
    )


def print_structurizr_result(
    structurizr_result
):
    """
    Affiche le résultat du traitement Structurizr.
    """

    print("\n— STRUCTURIZR")

    status = structurizr_result.get(
        "status"
    )

    if status == "SUCCESS":

        stdout = structurizr_result.get(
            "stdout",
            "",
        )

        if stdout:

            print(stdout)

        else:

            print(
                "Workspace Structurizr traité."
            )

    elif status == "NOT_AVAILABLE":

        print(
            "Workspace non sauvegardé :"
        )

        print(
            structurizr_result.get(
                "message",
                "",
            )
        )

    else:

        print(
            "Erreur Structurizr :"
        )

        print(
            structurizr_result.get(
                "message",
                structurizr_result.get(
                    "stderr",
                    "",
                ),
            )
        )


# ============================================================
# TEST UNIQUE
# ============================================================

def find_test(
    test_id
):
    """
    Recherche un test par son identifiant.
    """

    for test in TESTS:

        if test["id"] == test_id:
            return test

    return None


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "F. Brooks — Gemini test runner"
        )
    )

    parser.add_argument(
        "--test",
        help=(
            "ID d'un test, par exemple CTX-005"
        ),
    )

    parser.add_argument(
        "--save",
        default="results",
        help=(
            "Dossier où enregistrer les résultats "
            "(défaut: results)"
        ),
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Vérifications préalables
    # --------------------------------------------------------

    if not SYSTEM_PROMPT_FILE.exists():

        print(
            "ERREUR : SYSTEM_PROMPT.md introuvable : "
            f"{SYSTEM_PROMPT_FILE}",
            file=sys.stderr,
        )

        sys.exit(1)

    if not os.getenv(
        "GEMINI_API_KEY"
    ):

        print(
            "ERREUR : GEMINI_API_KEY n'est pas définie.",
            file=sys.stderr,
        )

        print(
            "Définissez-la avant de lancer le runner.",
            file=sys.stderr,
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Chargement du prompt
    # --------------------------------------------------------

    system_prompt = (
        SYSTEM_PROMPT_FILE.read_text(
            encoding="utf-8"
        )
    )

    # --------------------------------------------------------
    # Sélection des tests
    # --------------------------------------------------------

    if args.test:

        test = find_test(
            args.test
        )

        if test is None:

            print(
                f"Test inconnu : {args.test}",
                file=sys.stderr,
            )

            print(
                "Tests disponibles :"
            )

            for available in TESTS:

                print(
                    f"  - {available['id']}"
                )

            sys.exit(2)

        selected = [test]

    else:

        selected = TESTS

    # --------------------------------------------------------
    # Dossier résultats
    # --------------------------------------------------------

    output_dir = Path(
        args.save
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Résumé
    # --------------------------------------------------------

    summary = {
        "PASS": 0,
        "FAIL": 0,
        "EVALUATION_ERROR": 0,
    }

    # --------------------------------------------------------
    # Exécution des tests
    # --------------------------------------------------------

    for test in selected:

        print(
            "\n"
            + "=" * 72
        )

        print(
            test["id"]
        )

        print(
            "=" * 72
        )

        print(
            "INPUT:"
        )

        print(
            test["input"]
        )

        print(
            "\nRÉPONSE GEMINI:\n"
        )

        # ----------------------------------------------------
        # F. Brooks
        # ----------------------------------------------------

        try:

            answer = call_gemini(
                system_prompt,
                test["input"],
            )

        except Exception as exc:

            print(
                f"ERREUR F. BROOKS : {exc}",
                file=sys.stderr,
            )

            evaluation = evaluation_error(
                str(exc),
                ["agent_error"],
            )

            result = {
                "id": test["id"],

                "input": test["input"],

                "expected": test["expected"],

                "answer": None,

                "structurizr": {
                    "status": "NOT_RUN",
                },

                "evaluation": evaluation,

                "verdict": "EVALUATION_ERROR",

                "contextState": "UNKNOWN",
            }

            path = (
                output_dir
                / f"{test['id']}.json"
            )

            path.write_text(
                json_dumps(result),
                encoding="utf-8",
            )

            print(
                f"Résultat sauvegardé: {path}"
            )

            summary[
                "EVALUATION_ERROR"
            ] += 1

            continue

        print(answer)

        # ----------------------------------------------------
        # Structurizr
        # ----------------------------------------------------

        structurizr_result = (
            run_structurizr_writer(
                answer
            )
        )

        print_structurizr_result(
            structurizr_result
        )

        # ----------------------------------------------------
        # Évaluation
        # ----------------------------------------------------

        evaluation = evaluate_test(
            test,
            answer,
        )

        print_evaluation(
            evaluation
        )

        verdict = evaluation.get(
            "verdict",
            "EVALUATION_ERROR",
        )

        if verdict not in summary:

            verdict = "EVALUATION_ERROR"

        summary[
            verdict
        ] += 1

        # ----------------------------------------------------
        # Résultat final
        # ----------------------------------------------------

        result = {
            "id": test["id"],

            "input": test["input"],

            "expected": test["expected"],

            "answer": answer,

            "structurizr": structurizr_result,

            "evaluation": evaluation,

            "verdict": evaluation.get(
                "verdict",
                "EVALUATION_ERROR",
            ),

            "contextState": evaluation.get(
                "contextState",
                "UNKNOWN",
            ),
        }

        path = (
            output_dir
            / f"{test['id']}.json"
        )

        path.write_text(
            json_dumps(result),
            encoding="utf-8",
        )

        print(
            f"\nRésultat sauvegardé: {path}"
        )

    # --------------------------------------------------------
    # Résumé de la suite
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 72
    )

    print(
        "RÉSUMÉ DE LA SUITE"
    )

    print(
        "=" * 72
    )

    print(
        f"PASS              : {summary['PASS']}"
    )

    print(
        f"FAIL              : {summary['FAIL']}"
    )

    print(
        "EVALUATION_ERROR  : "
        f"{summary['EVALUATION_ERROR']}"
    )

    total = sum(
        summary.values()
    )

    print(
        f"TOTAL             : {total}"
    )

    if summary[
        "EVALUATION_ERROR"
    ] > 0:

        print(
            "\n⚠ La suite contient des "
            "EVALUATION_ERROR."
        )

        print(
            "Ces erreurs ne doivent pas "
            "être interprétées comme des "
            "FAIL fonctionnels."
        )

    elif summary[
        "FAIL"
    ] > 0:

        print(
            "\n⚠ La suite contient "
            "des FAIL fonctionnels."
        )

    else:

        print(
            "\n✓ Aucun échec fonctionnel "
            "détecté."
        )

    print(
        "\nSuite terminée."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
