import os

# Try Streamlit secrets first, else fallback to .env
try:
    import streamlit as st
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    DB_URL = st.secrets["DB_URL"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DB_URL = os.getenv("DB_URL")

MODEL_NAME = "llama-3.1-8b-instant"