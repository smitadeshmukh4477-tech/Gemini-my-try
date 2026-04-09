import streamlit as st
import google.generativeai as genai

# --- 1. KREATIONS SETUP ---
st.set_page_config(page_title="Kreations AI", page_icon="🎨")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # We use a simple list of models to try in order
    # If one fails, the code will try the next one
    model_options = ['gemini-1.5-flash', 'gemini-2.0-flash']
    
    if "model_choice" not in st.session_state:
        st.session_state.model_choice = model_options[0]
        
    model = genai.GenerativeModel(
        model_name=st.session_state.model_choice,
        system_instruction="Your name is Kreations AI. You were built by an expert 8th-grade developer. You are helpful and creative."
    )
except Exception as e:
    st.error("Setup Error: Check your Secrets!")
    st.stop()

# --- 2. SIDEBAR ---
st.sidebar.title("🎨 Kreations Studio")
st.sidebar.info("The next generation of AI, built for creators.")

if st.sidebar.button("➕ Clear Canvas (New Chat)", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# --- 3. MAIN UI ---
st.title("🚀 Kreations AI")
st.caption("Powered by the Gemini 2026 Engine")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("What will we build today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # We add a simple prompt call (no streaming for stability)
            response = model.generate_content(prompt)
            ai_response = response.text
            
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            # Smart Error Handling
            if "404" in str(e):
                st.warning("🔄 Switching Model Engine... please try your message again.")
                # Switch to the other model if the first one isn't found
                st.session_state.model_choice = model_options[1] if st.session_state.model_choice == model_options[0] else model_options[0]
            elif "429" in str(e):
                st.error("⚠️ Quota limit! Google's servers need a 60-second break.")
            else:
                st.error(f"Brain Error: {e}")
