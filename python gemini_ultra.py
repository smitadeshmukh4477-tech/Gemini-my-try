import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE LOCK ---
MY_PASSWORD = "your_secret_password" 

st.sidebar.title("🔐 Access Control")
user_pass = st.sidebar.text_input("Enter Password", type="password")

if user_pass != MY_PASSWORD:
    st.info("App Locked. Enter password to start.")
    st.stop() 

# --- 2. SETUP (STABLE 2026 MODEL) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # gemini-2.0-flash is the most reliable "Free" model right now
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction="Your name is Gemini-Ultra. Created by a pro 8th-grade dev."
    )
except Exception as e:
    st.error("Setup Error. Check your API Key.")
    st.stop()

# --- 3. UI & HISTORY ---
st.title("🌎 Gemini-Ultra OMNI")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. SEARCH ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=1)
            return f"🌐 {results[0]['body']}" if results else ""
    except: return ""

# --- 5. LOGIC ---
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:-1]])
        
        search_data = ""
        if any(word in prompt.lower() for word in ["news", "update", "today", "score"]):
            with st.status("Searching..."):
                search_data = web_search(prompt)

        full_input = f"HISTORY:\n{history}\n\nWEB:\n{search_data}\n\nUSER: {prompt}"
        
        placeholder = st.empty()
        full_response = ""
        
        try:
            # We removed streaming here to keep the connection "stable" and avoid 429 errors
            response = model.generate_content(full_input)
            full_response = response.text
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Quota reached. Wait 1 minute. ({e})")
