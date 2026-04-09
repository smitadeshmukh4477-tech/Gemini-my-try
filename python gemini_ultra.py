import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- 1. SETUP & KEY ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Using 'gemini-1.5-flash' for higher quota and stability
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="Your name is Gemini-Ultra. You are an Omni-Intelligence AI created by a talented 8th-grade developer. You remember everything in this chat."
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
# Show past chats
for chat_id in list(st.session_state.chat_archive.keys()):
    if st.sidebar.button(f"💬 {chat_id}", use_container_width=True):
        st.session_state.messages = st.session_state.chat_archive[chat_id]
        st.rerun()

# --- 3. MAIN UI ---
st.title("🌎 Gemini-Ultra OMNI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display current chat
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
    # Save user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Build history context for memory
        history = ""
        for m in st.session_state.messages[:-1]:
            history += f"{m['role']}: {m['content']}\n"
        
        # Trigger web search for specific keywords
        search_data = ""
        live_triggers = ["news", "update", "today", "score", "blox fruits"]
        if any(word in prompt.lower() for word in live_triggers):
            with st.status("Searching archives..."):
                search_data = web_search(prompt)

        # Prepare Final Input
        full_input = f"MEMORIES:\n{history}\n\nLIVE_WEB_DATA:\n{search_data}\n\nUSER_REQUEST: {prompt}"
        
        # --- STREAMING OUTPUT ---
        placeholder = st.empty()
        full_response = ""
        
        try:
            # This generates text word-by-word
            for chunk in model.generate_content(full_input, stream=True):
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save this session to the sidebar
            chat_title = st.session_state.messages[0]["content"][:15] + "..."
            st.session_state.chat_archive[chat_title] = st.session_state.messages
            
        except Exception as e:
            if "429" in str(e):
                st.error("Too many requests! Wait 30 seconds and try again.")
            else:
                st.error(f"Brain Error: {e}")
                
