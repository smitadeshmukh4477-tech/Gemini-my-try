import streamlit as st
import google.generativeai as genai

st.title("Kreations Emergency Test")

# Try to connect
try:
    # JUST use Key 1 for this test
    key = st.secrets["GEMINI_KEY_1"]
    genai.configure(api_key=key)
    
    # Use the 2.5 Flash model (it's the most stable right now)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    user_input = st.text_input("Type 'Hi' to test:")
    
    if user_input:
        response = model.generate_content(user_input)
        st.write("AI says:", response.text)
except Exception as e:
    st.error(f"System Error: {e}")
