import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE LOCK (PASSWORD) ---
# CHANGE THIS to your own secret word!
MY_PASSWORD = "your_secret_password" 

st.sidebar.title("🔐 Access Control")
user_pass = st.sidebar.text_input("Enter Password", type="password")

if user_pass != MY_PASSWORD:
    st.info("Enter the correct password in the sidebar to start the engine.")
    st.stop() 

# --- 2. SETUP & 2026 MODEL ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # UPDATED: Using the 2026 standard model name
    model = genai.GenerativeModel(
        model_name='gemini-3-flash-preview',
        system_instruction="Your name is Gemini-Ultra. Created by a pro 8th-grade dev. You have full memory."
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. SIDEBAR HISTORY ---
st.sidebar.divider()
st.sidebar.title("📚 Chat History")
if "chat_archive" not in st.session_state:
    st.session_state.chat_archive = {}

if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# --- 4. MAIN UI ---
st.title("🌎 Gemini-Ultra OMNI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. SEARCH & LOGIC ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=1)
            return f"🌐 {results[0]['body']}" if results else ""
    except: return ""

if prompt := st.chat_input("Ask your creation..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Memory (last 5 messages)
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:-1]])
        
        # Web Search Trigger
        search_data = ""
        if any(word in prompt.lower() for word in ["news", "update", "today", "score", "blox fruits"]):
            with st.status("Searching 2026 archives..."):
                search_data = web_search(prompt)

        full_input = f"HISTORY:\n{history}\n\nWEB:\n{search_data}\n\nUSER: {prompt}"
        
        placeholder = st.empty()
        full_response = ""
        
        try:
            # STREAMING for speed
            for chunk in model.generate_content(full_input, stream=True):
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            if "429" in str(e):
                st.error("Quota full! Wait 60 seconds.")
            else:
                st.error(f"Brain Error: {e}")
