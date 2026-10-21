
import streamlit as st

from detector import redact_text
from policy import evaluate_pipeline_policy, PolicyAction
from decider_client import DeciderClient

st.set_page_config(page_title="WhisperKey", page_icon="🔐")
st.title("🔐 WhisperKey")
st.caption("Local-first security guardrail for AI prompts")

mode = st.radio(
    "Decision engine",
    ["Demo Mode", "Real Decider Mode"],
    help="Demo Mode uses a simulated score. Real Decider Mode calls your configured local Decider server.",
)

if mode == "Demo Mode":
    st.info("Demo mode: Decider is simulated. No prompts are sent to AWS.")
else:
    st.warning(
        "Real Decider mode: requires a running Decider server. "
        "No Bedrock calls are made by this app."
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

        if mode == "Demo Mode":
            decider_result = {
                "status": "SUCCESS",
                "noul_score": 0.10,
            }
        else:
            decider_result = DeciderClient().evaluate_noul(
                processed_text=sanitized,
                question_id="contains_secret",
            )

        result = evaluate_pipeline_policy(text, decider_result)

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

            if mode == "Demo Mode":
                st.success(
                    "Demo policy approved this text. "
                    "No external AI service was called."
                )
            else:
                st.success(
                    "The real Decider endpoint returned a low-risk score. "
                    "No Bedrock service was called."
                )
