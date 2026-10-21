
import re
from typing import List, Tuple

# These patterns detect common secret formats.
# Detection is not exhaustive and cannot guarantee that all secrets are found.
PATTERNS = {
    "AWS_ACCESS_KEY_ID": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "SECRET_ASSIGNMENT": re.compile(
        r"""(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|password)\b"""
        r"""(\s*[:=]\s*)["']?([^\s"',;]+)"""
    ),
    "PRIVATE_KEY": re.compile(
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"
        r".*?"
        r"-----END [A-Z0-9 ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    "JWT": re.compile(
        r"\beyJ[a-zA-Z0-9_-]*\."
        r"[a-zA-Z0-9_-]+\."
        r"[a-zA-Z0-9_-]+\b"
    ),
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
}


def redact_text(text: str) -> Tuple[str, List[str]]:
    """Return redacted text and a list of detected categories."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    detected_categories = []
    sanitized_text = text

    # Redact complete private-key blocks first.
    for category, pattern in PATTERNS.items():
        if category == "SECRET_ASSIGNMENT":
            continue

        if pattern.search(sanitized_text):
            detected_categories.append(category)
            sanitized_text = pattern.sub(
                f"[REDACTED_{category}]",
                sanitized_text,
            )

    # Preserve the setting name while redacting its value.
    secret_pattern = PATTERNS["SECRET_ASSIGNMENT"]

    def replace_secret(match: re.Match) -> str:
        return f"{match.group(1)}{match.group(2)}[REDACTED_SECRET]"

    if secret_pattern.search(sanitized_text):
        detected_categories.append("SECRET_ASSIGNMENT")
        sanitized_text = secret_pattern.sub(
            replace_secret,
            sanitized_text,
        )

    return sanitized_text, detected_categories
