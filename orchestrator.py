
from policy import evaluate_pipeline_policy, PolicyAction


def run_whisperkey_agent(input_text, decider_client, bedrock_client):
    # Scan and redact locally before contacting Decider.
    from detector import redact_text
    sanitized_text, _ = redact_text(input_text)

    # Decider receives sanitized text, never the original input.
    try:
        result = decider_client.evaluate_noul(
            processed_text=sanitized_text,
            question_id="contains_secret",
        )
    except Exception:
        result = {"status": "ERROR", "noul_score": None}

    # Policy checks the original text to decide whether redaction occurred.
    decision = evaluate_pipeline_policy(input_text, result)

    if decision["action"] == PolicyAction.BLOCK_FOR_REVIEW:
        return {
            "action": decision["action"],
            "text": None,
            "reason": decision["reason"],
            "bedrock_invoked": False,
        }

    # Only approved, processed text reaches Bedrock.
    try:
        response = bedrock_client.generate_response(
            decision["processed_text"]
        )
    except Exception:
        return {
            "action": decision["action"],
            "text": None,
            "reason": "AI service failed.",
            "bedrock_invoked": True,
        }

    return {
        "action": decision["action"],
        "text": response,
        "reason": decision["reason"],
        "bedrock_invoked": True,
    }
