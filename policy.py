
import math
from typing import Any, Dict

from detector import redact_text


class PolicyAction:
    DIRECT_PASS = "DIRECT_PASS"
    SANITIZED_PASS = "SANITIZED_PASS"
    BLOCK_FOR_REVIEW = "BLOCK_FOR_REVIEW"


def evaluate_pipeline_policy(
    raw_input: str,
    decider_res: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluate text before it can be sent to an AI service.

    The caller must send only locally sanitized text to Decider.
    A successful low-risk decision is required before proceeding.
    """
    sanitized_text, detected_categories = redact_text(raw_input)

    if not isinstance(decider_res, dict):
        return _block("Invalid Decider response.")

    if decider_res.get("status") != "SUCCESS":
        return _block("Decider failed or is unavailable.")

    raw_score = decider_res.get("noul_score")

    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return _block("Invalid Decider score.")

    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        return _block("Decider score is outside the valid range.")

    # High risk: block even if regex already redacted a known secret.
    if score >= 0.85:
        return _block("Decider flagged a potential unredacted secret.")

    # Ambiguous risk: require human review.
    if score >= 0.40:
        return _block("Ambiguous risk score; review required.")

    if detected_categories:
        return {
            "action": PolicyAction.SANITIZED_PASS,
            "processed_text": sanitized_text,
            "detected_categories": detected_categories,
            "reason": "Known patterns were redacted and remaining risk scored low.",
        }

    return {
        "action": PolicyAction.DIRECT_PASS,
        "processed_text": raw_input,
        "detected_categories": [],
        "reason": "No known patterns detected and remaining risk scored low.",
    }


def _block(reason: str) -> Dict[str, Any]:
    return {
        "action": PolicyAction.BLOCK_FOR_REVIEW,
        "processed_text": None,
        "detected_categories": [],
        "reason": reason,
    }
