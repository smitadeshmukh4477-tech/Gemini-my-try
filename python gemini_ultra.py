import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. SETUP & KEY ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Using 'gemini-2.0-flash' - The 2026 Stable Standard
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction="Your name is Gemini-Ultra. You are an Omni-Intelligence AI created by a talented 8th-grade developer. You are fast, smart, and remember the full conversation history."
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
for chat_id in list(st.session_state.chat_archive.keys()):
    if st.sidebar.button(f"💬 {chat_id}", use_container_width=True):
        st.session_state.messages = st.session_state.chat_archive[chat_id]
        st.rerun()

# --- 3. MAIN UI ---
st.title("🌎 Gemini-Ultra OMNI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. FAST SEARCH ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=2)
            if results:
                return "\n\n".join([f"🌐 {r['body']}" for r in results])
            return ""
    except:
        return ""

# --- 5. FAST CHAT LOGIC ---
if prompt := st.chat_input("Ask your creation anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Build history context
        history = ""
        for m in st.session_state.messages[:-1]:
            history += f"{m['role']}: {m['content']}\n"
        
        # Trigger web search
        search_data = ""
        live_triggers = ["news", "update", "today", "score", "blox fruits", "weather"]
        if any(word in prompt.lower() for word in live_triggers):
            with st.status("Searching archives..."):
                search_data = web_search(prompt)

        full_input = f"MEMORIES:\n{history}\n\nLIVE_WEB_DATA:\n{search_data}\n\nUSER_REQUEST: {prompt}"
        
        # --- STREAMING OUTPUT ---
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Generate word-by-word
            for chunk in model.generate_content(full_input, stream=True):
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save to sidebar
            chat_title = st.session_state.messages[0]["content"][:15] + "..."
            st.session_state.chat_archive[chat_title] = st.session_state.messages
            
        except Exception as e:
            if "429" in str(e):
                st.error("Too many requests! Wait 30 seconds.")
            elif "404" in str(e):
                st.error("Model Update in progress. Please refresh in a moment.")
            else:
                st.error(f"Brain Error: {e}")
