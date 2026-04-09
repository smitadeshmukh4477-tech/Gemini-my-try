import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import json
import os

# --- 1. SETUP & KEY ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
except:
    st.error("Check your Secrets for GEMINI_API_KEY")
    st.stop()

# --- 2. SIDEBAR FOR CHAT HISTORY ---
st.sidebar.title("📚 Chat History")

# Initialize storage for multiple chats
if "chat_archive" not in st.session_state:
    st.session_state.chat_archive = {} # { "Chat Name": [messages] }

# Function to start a new chat
if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()

# List old chats in the sidebar
for chat_name in st.session_state.chat_archive.keys():
    if st.sidebar.button(f"💬 {chat_name}", use_container_width=True):
        st.session_state.messages = st.session_state.chat_archive[chat_name]
        st.rerun()

# --- 3. MAIN UI ---
st.title("🌎 Gemini-Ultra OMNI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show current chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. WEB SEARCH ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            return "\n\n".join([f"🌐 {r['title']}\n{r['body']}" for r in results]) if results else ""
    except: return ""

# --- 5. CHAT LOGIC ---
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Build memory context
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
        
        # Check for web needs
        search_data = web_search(prompt) if any(x in prompt.lower() for x in ["news", "update", "latest"]) else ""
        
        full_input = f"HISTORY:\n{history}\n\nWEB:\n{search_data}\n\nUSER: {prompt}"
        
        response = model.generate_content(full_input)
        ai_text = response.text
        st.markdown(ai_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        
        # --- AUTO-SAVE TO SIDEBAR ---
        # We use the first question as the Chat Name
        chat_id = st.session_state.messages[0]["content"][:20] + "..."
        st.session_state.chat_archive[chat_id] = st.session_state.messages
