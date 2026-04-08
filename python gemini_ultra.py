import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE KEY (PASTE YOUR KEY HERE) ---
# Ensure there are NO spaces before or after the key inside the quotes
API_KEY = "AIzaSyDobAz6bT6FGvAyeSf0YdDVS-PwDXH9W5I" 

# --- 2. INITIALIZE AI ---
try:
    genai.configure(api_key=API_KEY)
    # Using 'gemini-1.5-flash' because it's the fastest and most reliable for free tier
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 3. UI SETUP ---
st.set_page_config(page_title="Gemini-Ultra OMNI", page_icon="🌎", layout="wide")
st.title("🌎 Gemini-Ultra: Omni Intelligence")
st.caption("Now connected to the Universal Knowledge Base")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. WEB SEARCH FUNCTION ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=3)
            if results:
                return "\n\n".join([f"🌐 {r['title']}\n{r['body']}" for r in results])
            return "No live web results found."
    except Exception as e:
        return f"Search connection busy. (Error: {e})"

# --- 5. MAIN CHAT LOGIC ---
if prompt := st.chat_input("Ask me absolutely anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Determine if we need live data
        search_data = ""
        keywords = ["news", "war", "today", "latest", "score", "match", "weather", "blox fruits update"]
        
        if any(word in prompt.lower() for word in keywords):
            with st.spinner("Searching live web for updates..."):
                search_data = web_search(prompt)

        # Prepare the context for the AI
        if search_data:
            full_context = f"Context from Web:\n{search_data}\n\nUser Question: {prompt}"
        else:
            full_context = prompt

        # Generate Response from Gemini
        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(full_context)
                ai_text = response.text
                
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
        
        except Exception as e:
            # If it fails, we show a helpful error message
            st.error("⚠️ AI Brain Connection Issue")
            st.info(f"Details: {e}")
            st.warning("Check if your API Key is pasted correctly in the code and has no spaces!")
