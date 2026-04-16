import streamlit as st
import google.generativeai as genai
import random

# --- 1. PAGE CONFIG & BRANDING ---
st.set_page_config(page_title="Kreations AI", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTitle { color: #00ffcc; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-KEY LOAD BALANCER ---
try:
    # Pulling all 3 keys from secrets
    api_keys = [
        st.secrets["GEMINI_KEY_1"],
        st.secrets["GEMINI_KEY_2"],
        st.secrets["GEMINI_KEY_3"]
    ]
    
    # Initialize session state for tracking which key to use
    if "key_index" not in st.session_state:
        st.session_state.key_index = 0

    # Function to configure the next available key
    def configure_next_key():
        key = api_keys[st.session_state.key_index]
        genai.configure(api_key=key)
        # Rotate to next key for the next request
        st.session_state.key_index = (st.session_state.key_index + 1) % len(api_keys)

    configure_next_key()
    
    # Using the 2026 stable model name
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash', # Highest daily limit for Free Tier
        system_instruction="Your name is Kreations AI. You were built by a pro student developer. You are witty, smart, and helpful."
    )
except Exception as e:
    st.error("⚠️ Setup Error: Make sure KEY_1, KEY_2, and KEY_3 are in Streamlit Secrets!")
    st.stop()

# --- 3. SIDEBAR & HISTORY ---
st.sidebar.title("🎨 Kreations Studio")
st.sidebar.write("Triple-Key Power Active ⚡")

if st.sidebar.button("➕ New Canvas", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# --- 4. MAIN CHAT INTERFACE ---
st.title("🚀 Kreations AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT LOGIC WITH AUTO-RETRY ---
if prompt := st.chat_input("What are we creating today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        success = False
        
        # Try up to 3 times (once for each key) if a Quota Error happens
        for attempt in range(len(api_keys)):
            try:
                # Attempt to generate content
                response = model.generate_content(prompt)
                full_response = response.text
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                success = True
                break # Exit the loop if successful
            
            except Exception as e:
                if "429" in str(e):
                    # If quota hit, switch key and try again
                    configure_next_key()
                    continue 
                else:
                    st.error(f"Error: {e}")
                    break
        
        if not success:
            st.warning("All API keys are currently resting. Please wait 60 seconds!")
