import streamlit as st
from duckduckgo_search import DDGS
import re

# --- UI SETUP ---
st.set_page_config(page_title="Gemini-Ultra v6.9", page_icon="💎")
st.title("💎 Gemini-Ultra Universal")
st.markdown("### 8th Grade Tech Showcase")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CORE FUNCTIONS ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', timelimit='y')
            clean = []
            for r in list(results)[:3]:
                clean.append(f"📍 **{r['title']}**\n{r['body']}")
            return "\n\n".join(clean) if clean else "No live data found."
    except:
        return "Search satellites are currently offline."

# --- CHAT INPUT ---
if prompt := st.chat_input("Type 'search [topic]' or ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        ui = prompt.lower()
        # Math
        if any(op in ui for op in ["+", "-", "*", "/"]):
            try:
                clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', ui)
                response = f"🔢 **Math Engine:** {clean_expr} = `{eval(clean_expr)}`"
            except: response = "Math error!"
        # Search
        elif ui.startswith("search "):
            response = web_search(ui.replace("search ", ""))
        # Wiki
        elif "blox fruits" in ui:
            response = "⚓ **Wiki:** Mirage Island spawns at night. Blue Gear is needed for Race V4!"
        elif "minecraft" in ui:
            response = "🏗️ **Wiki:** Technical MC 1.21.1 works best with Litematica for schematics."
        else:
            response = "I'm live! Try: `search latest news` or `calculate 500/2`."

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
