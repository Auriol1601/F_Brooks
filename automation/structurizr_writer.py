from pathlib import Path
import re
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
STRUCTURIZR_DIR = BASE_DIR / "structurizr"
WORKSPACE_FILE = STRUCTURIZR_DIR / "workspace.dsl"


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

    workspace_pattern = re.compile(
        r"\bworkspace"
        r'(?:\s+"(?:\\.|[^"\\])*")?'
        r"\s*\{",
        re.IGNORECASE,
    )
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
        r"^\s*workspace"
        r'(?:\s+"(?:\\.|[^"\\])*")?'
        r"\s*\{",
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


def save_workspace(answer: str):
    """Extract, validate, and save a workspace from a model response."""
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

    STRUCTURIZR_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_FILE.write_text(dsl + "\n", encoding="utf-8")
    return {
        "saved": True,
        "path": str(WORKSPACE_FILE),
    }


if __name__ == "__main__":
    answer = sys.stdin.read()
    if not answer.strip():
        print("Aucune réponse reçue via stdin.", file=sys.stderr)
        sys.exit(1)

    result = save_workspace(answer)
    print("[STRUCTURIZR]")
    if result["saved"]:
        print("Workspace sauvegarde automatiquement :")
        print(result["path"])
    else:
        print(result["reason"])
