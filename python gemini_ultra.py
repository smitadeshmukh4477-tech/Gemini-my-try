import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. THEME & PAGE CONFIG (LIGHT MODE) ---
st.set_page_config(page_title="Kreations AI", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #212529; }
    .stTitle { color: #007bff; font-family: 'Segoe UI', sans-serif; font-weight: 800; }
    .stChatMessage { 
        background-color: #ffffff; 
        border-radius: 10px; 
        border: 1px solid #dee2e6; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px; 
    }
    [data-testid="stSidebar"] { background-color: #e9ecef; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & FILE SETUP ---
USER_DB = "users.json"
CHAT_DIR = "chats"
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB, "w") as f: json.dump(users, f)

# --- 3. THE OMNI-BRAIN (1900-2026) ---
system_info = """
You are Kreations AI. State your name ONLY in the first message. 
KNOWLEDGE BASE:
- Every major war (WWI, WWII, Cold War, Ukraine, Gaza), revolt, and law since 1900.
- Every Olympics, FIFA/Cricket World Cup winner, and legendary sports match.
- Internet history from ARPANET to the 2026 AI era.
- All major movies, pop culture, and Anime (Expert in Jujutsu Kaisen).
- Gaming Meta: Expert in Litematica and Blox Fruits (Draco Race V1-V4, Trial of Flames).
- Built by a 13-year-old developer in India. You are witty and direct.
"""

# --- 4. AUTHENTICATION SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Kreations Gateway")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Enter Studio"):
            users = load_users()
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid Credentials")
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            users = load_users()
            if new_u in users: st.warning("User exists!")
            else:
                save_user(new_u, new_p)
                st.success("Account Created! Go to Login tab.")
    st.stop()

# --- 5. CHAT PERSISTENCE ---
chat_file = f"{CHAT_DIR}/{st.session_state.username}.json"
if "messages" not in st.session_state:
    if os.path.exists(chat_file):
        with open(chat_file, "r") as f: 
            try:
                st.session_state.messages = json.load(f)
            except:
                st.session_state.messages = []
    else:
        st.session_state.messages = []

# --- 6. MAIN INTERFACE ---
st.title("🚀 Kreations AI")
st.sidebar.title("🎨 Kreations Studio")
st.sidebar.write(f"User: **{st.session_state.username}**")

if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.session_state.messages = []
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Multi-Key Rotation
try:
    keys = [st.secrets["GEMINI_KEY_1"], st.secrets["GEMINI_KEY_2"], st.secrets["GEMINI_KEY_3"]]
    if "key_index" not in st.session_state: st.session_state.key_index = 0
except:
    st.error("API Keys missing in Streamlit Secrets!")
    st.stop()

# --- 7. AI LOGIC ---
if prompt := st.chat_input("Ask about history, sports, or games..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        success = False
        
        for _ in range(len(keys)):
            try:
                genai.configure(api_key=keys[st.session_state.key_index])
                model = genai.GenerativeModel(
                    model_name='gemini-3.1-flash-lite-preview',
                    system_instruction=system_info
                )
                
                response = model.generate_content(prompt)
                full_response = response.text
                response_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with open(chat_file, "w") as f: 
                    json.dump(st.session_state.messages, f)
                
                success = True
                break
            except Exception:
                st.session_state.key_index = (st.session_state.key_index + 1) % len(keys)
                continue
        
        if not success:
            st.warning("Connection limit reached. Re-syncing power sources in 60s...")
