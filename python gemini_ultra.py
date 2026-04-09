import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. THE LOCK (PASSWORD) ---
# Set your own password here!
MY_PASSWORD = "death" 

st.sidebar.title("🔐 Access Control")
user_pass = st.sidebar.text_input("Enter Password to Chat", type="password")

if user_pass != MY_PASSWORD:
    st.info("Please enter the correct password in the sidebar to use Gemini-Ultra.")
    st.stop() # This stops the rest of the code from running

# --- 2. SETUP & KEY ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="Your name is Gemini-Ultra. You only talk to your creator."
    )
except:
    st.error("Check your Secrets!")
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
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:-1]])
        
        search_data = ""
        if any(word in prompt.lower() for word in ["news", "update", "today"]):
            with st.status("Checking web..."):
                search_data = web_search(prompt)

        full_input = f"HISTORY:\n{history}\n\nWEB:\n{search_data}\n\nUSER: {prompt}"
        
        placeholder = st.empty()
        full_response = ""
        
        try:
            for chunk in model.generate_content(full_input, stream=True):
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Quota Error: Wait 60 seconds. {e}")
