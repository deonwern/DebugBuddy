import streamlit as st
import subprocess


def translate_text(text, target_language="English"):
    """
    Translates AI response into target language.
    Can be connected to a lightweight translation library or API.
    """
    if not target_language or target_language.lower() == "english":
        return text

    # Placeholder for translation integration (e.g., deep-translator or local LLM translation step)
    return f"[Translated to {target_language}]:\n{text}"


st.set_page_config(page_title="DebugBuddy AI Assistant", layout="centered")

st.title("🤖 DebugBuddy AI Assistant")
st.markdown("Your local AI companion for debugging code diagnostics.")

# Sidebar options
st.sidebar.header("Configuration")
target_lang = st.sidebar.selectbox(
    "Preferred Language",
    ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean"],
    index=0,
)
model_name = st.sidebar.text_input("Local LLM Model (Ollama)", value="llama3")

# Session state initialization for error payload
if "error_payload" not in st.session_state:
    st.session_state.error_payload = ""

st.markdown("### Error Context Payload")
payload_input = st.text_area(
    "Paste or auto-loaded error payload:",
    value=st.session_state.error_payload,
    height=150,
)

if st.button("Ask Local AI"):
    if not payload_input.strip():
        st.warning("Please provide an error payload first.")
    else:
        with st.spinner("Consulting local LLM (Ollama)..."):
            try:
                # Query local Ollama model
                result = subprocess.run(
                    ["ollama", "run", model_name, payload_input],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
                raw_response = result.stdout
                translated_response = translate_text(raw_response, target_lang)

                st.markdown("### 💡 AI Solution")
                st.success(translated_response)
            except Exception as e:
                st.error(f"Failed to communicate with local LLM (`ollama`): {e}")
