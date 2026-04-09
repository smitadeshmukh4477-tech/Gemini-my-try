import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE KEY (SECURE METHOD) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to your Streamlit Secrets.")
    st.stop()

# --- 2. INITIALIZE AI WITH PERSONALITY ---
try:
    genai.configure(api_key=API_KEY)
    
    # We add a System Instruction here to give it a personality
    model = genai.GenerativeModel(
        model_name='gemini-3-flash-preview',
        system_instruction="Your name is Gemini-Ultra. You are a highly advanced Omni-Intelligence AI. You were created by a talented developer and student. You are helpful, tech-savvy, and expert in coding, games like Roblox, and 8th-grade academics."
    )
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 3. UI SETUP ---
st.set_page_config(page_title="Gemini-Ultra OMNI", page_icon="🌎", layout="wide")
st.title("🌎 Gemini-Ultra: Omni Intelligence")
st.caption("Custom AI Engine | Version 10.0 Stable")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. WEB SEARCH ENGINE ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=3)
            if results:
                return "\n\n".join([f"🌐 {r['title']}\n{r['body']}" for r in results])
            return "No live data found."
    except Exception as e:
        return f"Web search busy. (Error: {e})"

# --- 5. MAIN CHAT LOGIC ---
if prompt := st.chat_input("Ask your creation anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        search_data = ""
        live_keywords = ["news", "today", "latest", "score", "match", "blox fruits", "update", "weather"]
        
        if any(word in prompt.lower() for word in live_keywords):
            with st.spinner("Accessing live web archives..."):
                search_data = web_search(prompt)

        if search_data:
            full_context = f"LATEST WEB DATA:\n{search_data}\n\nUSER QUESTION: {prompt}"
        else:
            full_context = prompt

        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(full_context)
                ai_text = response.text
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
        except Exception as e:
            st.error(f"Connection Issue: {e}")
