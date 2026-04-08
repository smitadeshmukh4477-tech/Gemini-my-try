import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE KEY ---
# Replace YOUR_API_KEY_HERE with your actual key from Google AI Studio
API_KEY = "AIzaSyDobAz6bT6FGvAyeSf0YdDVS-PwDXH9W5I" 

# --- 2. INITIALIZE AI ---
try:
    genai.configure(api_key=API_KEY)
    # Using 'gemini-1.5-flash' - this is the most compatible version globally
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 3. UI SETUP ---
st.set_page_config(page_title="Gemini-Ultra OMNI", page_icon="🌎", layout="wide")
st.title("🌎 Gemini-Ultra: Omni Intelligence")
st.caption("Universal Knowledge Base & Live Web Access")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous chat messages
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
if prompt := st.chat_input("Ask me about anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Auto-detect if we need fresh data from the internet
        search_data = ""
        live_keywords = ["news", "war", "today", "latest", "score", "match", "blox fruits", "update", "weather"]
        
        if any(word in prompt.lower() for word in live_keywords):
            with st.spinner("Accessing live archives..."):
                search_data = web_search(prompt)

        # Build the final prompt for the AI
        if search_data:
            full_context = f"LATEST WEB DATA:\n{search_data}\n\nUSER QUESTION: {prompt}"
        else:
            full_context = prompt

        # Generate Response
        try:
            with st.spinner("Consulting Brain..."):
                response = model.generate_content(full_context)
                ai_text = response.text
                
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
        
        except Exception as e:
            st.error("⚠️ AI Brain Connection Issue")
            st.info(f"Details: {e}")
            st.warning("If you see 404, check that your API Key is active in AI Studio.")
