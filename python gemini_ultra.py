import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. SETUP & KEY ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Using 'gemini-2.0-flash' for the best balance of speed and 2026 stability
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction="Your name is Gemini-Ultra. You are an Omni-Intelligence AI created by a talented student developer. You are fast, smart, and helpful."
    )
except Exception as e:
    st.error("Missing API Key in Streamlit Secrets!")
    st.stop()

# --- 2. SIDEBAR HISTORY ---
st.sidebar.title("📚 Chat History")
if "chat_archive" not in st.session_state:
    st.session_state.chat_archive = {}

if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()
# Display saved chat sessions
for chat_id in list(st.session_state.chat_archive.keys()):
    if st.sidebar.button(f"💬 {chat_id}", use_container_width=True):
        st.session_state.messages = st.session_state.chat_archive[chat_id]
        st.rerun()

# --- 3. MAIN UI ---
st.title("🌎 Gemini-Ultra OMNI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show current conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. FAST SEARCH ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=1)
            return f"🌐 {results[0]['body']}" if results else ""
    except:
        return ""

# --- 5. CHAT LOGIC ---
if prompt := st.chat_input("Ask your creation anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Build history context (last 5 messages for quota safety)
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:-1]])
        
        # Search for live info if keywords match
        search_data = ""
        if any(word in prompt.lower() for word in ["news", "update", "today", "score", "blox fruits"]):
            with st.status("Searching archives..."):
                search_data = web_search(prompt)

        full_input = f"HISTORY:\n{history}\n\nWEB:\n{search_data}\n\nUSER: {prompt}"
        
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Simple non-streaming for maximum stability on free tier
            response = model.generate_content(full_input)
            full_response = response.text
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save this session to sidebar using the first message
            chat_title = st.session_state.messages[0]["content"][:15] + "..."
            st.session_state.chat_archive[chat_title] = st.session_state.messages
            
        except Exception as e:
            if "429" in str(e):
                st.error("Quota reached! Wait 60 seconds and try again.")
            else:
                st.error(f"Brain Error: {e}")
