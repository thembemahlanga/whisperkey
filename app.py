
import streamlit as st

from detector import redact_text
from policy import evaluate_pipeline_policy, PolicyAction

st.set_page_config(page_title="WhisperKey", page_icon="🔐")
st.title("🔐 WhisperKey")
st.caption("Local-first security guardrail for AI prompts")

st.info(
    "Demo mode: Decider is simulated. No prompts are sent to AWS."
)

text = st.text_area(
    "Enter text to scan",
    placeholder="Paste sample code or logs here. Use fake credentials only.",
    height=180,
)

if st.button("Scan and evaluate", type="primary"):
    if not text.strip():
        st.warning("Enter some text first.")
    else:
        sanitized, categories = redact_text(text)

        # Simulated low-risk score for demonstrating the local policy.
        # This is NOT a real Decider 2B prediction.
        simulated_decider = {
            "status": "SUCCESS",
            "noul_score": 0.10,
        }

        result = evaluate_pipeline_policy(text, simulated_decider)

        st.subheader("Security decision")
        st.write("**Action:**", result["action"])
        st.write("**Reason:**", result["reason"])

        st.subheader("Detected categories")
        st.write(", ".join(categories) if categories else "None detected")

        if result["action"] == PolicyAction.BLOCK_FOR_REVIEW:
            st.error("Blocked. No AI service was called.")
        else:
            st.subheader("Sanitized text")
            st.code(result["processed_text"])

            st.success(
                "Local policy approved this text. "
                "No AI service was called in this demo."
            )
