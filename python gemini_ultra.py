import streamlit as st
import google.generativeai as genai
import random

# --- 1. BRANDING & CONFIG ---
st.set_page_config(page_title="Kreations AI", page_icon="🎨", layout="centered")

# Custom CSS to give it that "Studio" vibe
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTitle { color: #00ffcc; font-family: 'Trebuchet MS', sans-serif; text-shadow: 2px 2px #000000; }
    .stChatMessage { border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-KEY ROTATION ---
try:
    keys = [st.secrets["GEMINI_KEY_1"], st.secrets["GEMINI_KEY_2"], st.secrets["GEMINI_KEY_3"]]
    
    if "key_index" not in st.session_state:
        st.session_state.key_index = 0

    def rotate_key():
        key = keys[st.session_state.key_index]
        genai.configure(api_key=key)
        st.session_state.key_index = (st.session_state.key_index + 1) % len(keys)

    rotate_key()
    
    # UPGRADED TO GEMINI 3.1 FLASH LITE (2026 PREVIEW)
    model = genai.GenerativeModel(
        model_name='gemini-3.1-flash-lite-preview',
        system_instruction="Your name is Kreations AI. You are a 3.1-generation intelligence built by a student developer. You are fast, creative, and expert at modding and building."
    )
except Exception as e:
    st.error("Missing API Keys! Add GEMINI_KEY_1, 2, and 3 to your Streamlit Secrets.")
    st.stop()

# --- 3. UI ELEMENTS ---
st.title("🚀 Kreations AI")
st.caption("Engine: Gemini 3.1 Flash-Lite (Multi-Key Enabled)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for controls
st.sidebar.title("🎨 Kreations Studio")
if st.sidebar.button("🗑️ Clear Canvas", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()
st.sidebar.info("This AI uses 3 separate power sources (API keys) to stay online without hitting limits.")

# --- 4. CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What are we creating today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        success = False
        
        # Automatic Key-Swap Loop
        for attempt in range(len(keys)):
            try:
                # We rotate keys BEFORE the call to stay ahead of limits
                rotate_key()
                response = model.generate_content(prompt)
                full_response = response.text
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                success = True
                break 
                
            except Exception as e:
                if "429" in str(e):
                    # If this key is tired, loop to the next one
                    continue 
                else:
                    st.error(f"Error: {e}")
                    break
        
        if not success:
            st.warning("All power sources (API keys) are exhausted. Wait 60 seconds!")
