import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE KEY ---
# Use the key ending in 9W5I or TXDA
API_KEY = "AIzaSyDobAz6bT6FGvAyeSf0YdDVS-PwDXH9W5I" 

# --- 2. INITIALIZE AI ---
try:
    genai.configure(api_key=API_KEY)
    # Using the most stable global ID to avoid the 404 error
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 3. UI SETUP ---
st.set_page_config(page_title="Gemini-Ultra OMNI", page_icon="🌎", layout="wide")
st.title("🌎 Gemini-Ultra: Omni Intelligence")
st.caption("Status: Multi-Model Knowledge Engine Active")

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
        return f"Web connection busy. (Error: {e})"

# --- 5. MAIN CHAT LOGIC ---
if prompt := st.chat_input("Ask me about science, history, games..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        search_data = ""
        live_keywords = ["news", "war", "today", "latest", "score", "match", "blox fruits", "update"]
        
        if any(word in prompt.lower() for word in live_keywords):
            with st.spinner("Accessing live archives..."):
                search_data = web_search(prompt)

        # Build context
        if search_data:
            full_context = f"LATEST DATA:\n{search_data}\n\nUSER QUESTION: {prompt}"
        else:
            full_context = prompt

        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(full_context)
                ai_text = response.text
                
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
        
        except Exception as e:
            st.error("⚠️ AI Brain Connection Issue")
            st.info(f"Details: {e}")
