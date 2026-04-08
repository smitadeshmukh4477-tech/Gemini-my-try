import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- SETUP ---
# Put your API Key here inside the quotes
API_KEY = "AIzaSyDmxVcwRyYhe2WnBJdkGAD5v_f04UTTXDA" 

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Gemini-Ultra OMNI", page_icon="🌎")
st.title("🌎 Gemini-Ultra: Omni Intelligence")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LIVE SEARCH TOOL ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=3)
            return "\n\n".join([f"🌐 {r['title']}\n{r['body']}" for r in results])
    except: return ""

# --- MAIN CHAT ---
if prompt := st.chat_input("Ask me absolutely anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Decide if we need live web data for news/current events
        search_data = ""
        if any(word in prompt.lower() for word in ["news", "war", "today", "latest", "score"]):
            with st.spinner("Searching live web..."):
                search_data = web_search(prompt)

        # 2. Use the AI Brain + Search Data
        full_context = f"User Question: {prompt}\n\nLive Web Info: {search_data}"
        
        with st.spinner("Thinking..."):
            response = model.generate_content(full_context)
            ai_text = response.text

        st.markdown(ai_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
