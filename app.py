import os
import sys
import streamlit as st
import tempfile
from dotenv import load_dotenv

# =========================
# ENV SETUP
# =========================
load_dotenv()

# Add root path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# =========================
# IMPORT MODULES
# =========================
from backend.rag.rag_pipelin import build_index_from_pdf, retrieve_chunks, answer_question
from backend.rag.questions_gen import generate_followup_questions

from backend.aadhaar.ocr import extract_text
from backend.aadhaar.llm_parser import extract_aadhaar_details
from backend.aadhaar.db import fetch_user
from backend.aadhaar.verifier import calculate_match, normalize_aadhaar

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Assistant", layout="wide")
st.title("🚀 AI Assistant")

BASE_DIR = os.path.dirname(__file__)
DEFAULT_PDF = os.path.join(BASE_DIR, "data/hsg150.pdf")

# =========================
# SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "docs" not in st.session_state:
    st.session_state.docs = None
    st.session_state.vectorizer = None
    st.session_state.X = None

# =========================
# CACHED PDF LOAD
# =========================
@st.cache_resource
def load_pdf_cached(path):
    return build_index_from_pdf(path)

# =========================
# RAG UI
# =========================
def run_rag():

    st.subheader("💬 RAG Chatbot")

    # Sidebar upload
    uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

    # Upload PDF
    if uploaded_pdf:
        if st.sidebar.button("Use Uploaded PDF"):
            with st.spinner("Processing PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_pdf.read())
                    path = tmp.name

                docs, vectorizer, X = load_pdf_cached(path)
                st.session_state.docs = docs
                st.session_state.vectorizer = vectorizer
                st.session_state.X = X
                st.session_state.messages = []

                st.success("Uploaded PDF loaded")

    # Load default PDF button
    if st.session_state.docs is None:
        st.warning("Click below to load default PDF")

        if st.button("Load Default PDF"):
            with st.spinner("Processing PDF..."):
                docs, vectorizer, X = load_pdf_cached(DEFAULT_PDF)

                st.session_state.docs = docs
                st.session_state.vectorizer = vectorizer
                st.session_state.X = X

                st.success("PDF Loaded Successfully!")
        return  # 🚀 STOP execution until PDF loaded

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # User input
    user_input = st.chat_input("Ask something...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = answer_question(
                    user_input,
                    st.session_state.docs,
                    st.session_state.vectorizer,
                    st.session_state.X
                )
                st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

        # Suggestions
        try:
            chunks = retrieve_chunks(
                user_input,
                st.session_state.docs,
                st.session_state.vectorizer,
                st.session_state.X
            )

            result = generate_followup_questions(user_input, chunks)
            st.session_state.suggestions = result.get("questions", [])
        except:
            st.session_state.suggestions = []

    # Suggested questions
    if st.session_state.suggestions:
        st.subheader("💡 Suggested Questions")

        for q in st.session_state.suggestions:
            if st.button(q):
                st.session_state.messages.append({"role": "user", "content": q})

                with st.chat_message("user"):
                    st.write(q)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        answer = answer_question(
                            q,
                            st.session_state.docs,
                            st.session_state.vectorizer,
                            st.session_state.X
                        )
                        st.write(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})

    # Clear chat
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.suggestions = []

# =========================
# AADHAAR UI
# =========================
def run_aadhaar():

    st.subheader("🪪 Aadhaar Verification")

    file = st.file_uploader("Upload Aadhaar Image", type=["jpg", "png", "jpeg"])

    if file:
        st.image(file)

        if st.button("Verify"):
            with st.spinner("Processing..."):

                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(file.getvalue())
                    path = tmp.name

                text = extract_text(path)
                st.subheader("📝 OCR Text")
                st.write(text)

                data = extract_aadhaar_details(text)

                if not data:
                    st.error("Failed to extract data")
                    return

                data["aadhaar"] = normalize_aadhaar(data.get("aadhaar", ""))

                st.subheader("📦 Extracted Data")
                st.json(data)

                db = fetch_user(data["aadhaar"])

                if not db:
                    st.warning("No record found")
                    return

                score = calculate_match(db, data)
                st.success(f"Match Score: {score}%")

# =========================
# MAIN NAVIGATION
# =========================
option = st.sidebar.selectbox(
    "Choose Feature",
    ["RAG Chatbot", "Aadhaar Verification"]
)

if option == "RAG Chatbot":
    run_rag()
else:
    run_aadhaar()