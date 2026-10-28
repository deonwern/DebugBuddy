import streamlit as st
import subprocess


def translate_text(text, target_language="English"):
    if not target_language or target_language.lower() == "english":
        return text
    return text


def get_local_llm_model():
    return "qwen2.5-coder:1.5b"


def main():
    st.set_page_config(page_title="DebugBuddy AI Assistant", layout="centered")

    if "error_payload" not in st.session_state:
        st.session_state.error_payload = ""

    st.title("🤖 DebugBuddy AI Assistant")
    st.markdown("Your local AI companion for debugging code diagnostics.")

    st.sidebar.header("Configuration")
    target_lang = st.sidebar.selectbox(
        "Preferred Language",
        ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean"],
        index=0,
    )
    model_name = st.sidebar.text_input(
        "Local LLM Model (Ollama)", value=get_local_llm_model()
    )

    payload_input = st.text_area(
        "Paste or auto-loaded error payload:",
        value=st.session_state.error_payload,
        height=150,
    )

    st.session_state.error_payload = payload_input

    if payload_input.strip():
        try:
            with st.spinner(f"Consulting local LLM ({model_name})..."):
                result = subprocess.run(
                    ["ollama", "run", model_name, payload_input],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=45,
                )
                raw_response = result.stdout
                translated_response = translate_text(raw_response, target_lang)

                st.markdown("### 💡 AI Solution")
                st.success(translated_response)
        except subprocess.TimeoutExpired:
            st.error("LLM took too long to respond.")
        except subprocess.CalledProcessError as e:
            st.error(f"Failed to communicate with local LLM `ollama`: {e}")
        except Exception as e:
            st.error(f"Error processing the error payload: {e}")
    else:
        st.warning("Please provide an error payload first.")

    st.sidebar.header("Tools")
    if st.sidebar.button("Clear Payload"):
        st.session_state.error_payload = ""
        st.rerun()


if __name__ == "__main__":
    main()
