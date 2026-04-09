import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Using 'flash' is 3x faster than 'pro' models
    model = genai.GenerativeModel('gemini-3-flash-preview')
except:
    st.error("Check your Secrets!")
    st.stop()

# --- 2. SIDEBAR ---
st.sidebar.title("📚 Chat History")
if "chat_archive" not in st.session_state:
    st.session_state.chat_archive = {}
if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# --- 3. MAIN UI ---
st.title("🌎 Gemini-Ultra OMNI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show current chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. OPTIMIZED SEARCH ---
def web_search(query):
    # Reduced max_results to 2 for faster loading
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=2)
            return "\n\n".join([f"🌐 {r['body']}" for r in results]) if results else ""
    except: return ""

# --- 5. FAST CHAT LOGIC ---
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Build memory
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
        
        # Speed Tip: Only search if absolutely necessary
        search_data = ""
        if any(x in prompt.lower() for x in ["news", "update", "today", "score"]):
            with st.status("Searching web..."):
                search_data = web_search(prompt)
        
        full_input = f"HISTORY:\n{history}\n\nWEB:\n{search_data}\n\nUSER: {prompt}"
        
        # --- THE SPEED FIX: STREAMING ---
        placeholder = st.empty()
        full_response = ""
        
        # This makes it type out word-by-word instantly
        try:
            for chunk in model.generate_content(full_input, stream=True):
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response) # Final clean version
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save to archive
            chat_id = st.session_state.messages[0]["content"][:20]
            st.session_state.chat_archive[chat_id] = st.session_state.messages
        except Exception as e:
            st.error(f"Error: {e}")
