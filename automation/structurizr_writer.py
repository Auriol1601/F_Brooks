from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent.parent

STRUCTURIZR_DIR = BASE_DIR / "structurizr"

WORKSPACE_FILE = STRUCTURIZR_DIR / "workspace.dsl"


def is_valid_evaluation(answer: str) -> bool:
    """
    Vérifie que F. Brooks a explicitement atteint l'état VALID.
    """

    patterns = [
        r"Évaluation\s*:\s*VALID\b",
        r"Evaluation\s*:\s*VALID\b",
    ]

    return any(
        re.search(pattern, answer, re.IGNORECASE)
        for pattern in patterns
    )


def extract_workspace_dsl(answer: str):
    """
    Extrait le bloc :

        workspace {
            ...
        }

    depuis la réponse de F. Brooks.
    """

    match = re.search(
        r"```(?:structurizr|dsl)?\s*(workspace\s*\{.*?\})\s*```",
        answer,
        re.IGNORECASE | re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    # Fallback : recherche directe de workspace {
    start = answer.find("workspace")

    if start == -1:
        return None

    opening_brace = answer.find("{", start)

    if opening_brace == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(opening_brace, len(answer)):

        char = answer[index]

        if in_string:

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True

        elif char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return answer[start:index + 1].strip()

    return None


def validate_dsl(dsl: str) -> bool:
    """
    Validation structurelle minimale.
    """

    if not dsl:
        return False

    if not dsl.strip().startswith("workspace"):
        return False

    depth = 0
    in_string = False
    escaped = False

    for char in dsl:

        if in_string:

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == '"':
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

    return depth == 0


def save_workspace(answer: str):
    """
    Sauvegarde le workspace uniquement si F. Brooks
    a atteint l'état VALID et a produit un DSL valide.
    """

    if not is_valid_evaluation(answer):
        return {
            "saved": False,
            "reason": "Évaluation différente de VALID.",
        }

    dsl = extract_workspace_dsl(answer)

    if not dsl:
        return {
            "saved": False,
            "reason": "Aucun workspace Structurizr détecté.",
        }

    if not validate_dsl(dsl):
        return {
            "saved": False,
            "reason": "Le DSL détecté est structurellement invalide.",
        }

    STRUCTURIZR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    WORKSPACE_FILE.write_text(
        dsl + "\n",
        encoding="utf-8",
    )

    return {
        "saved": True,
        "path": str(WORKSPACE_FILE),
    }