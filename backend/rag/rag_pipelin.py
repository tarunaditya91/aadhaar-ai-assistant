from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pdfplumber

from groq import Groq
from config.settings import GROQ_API_KEY, MODEL_NAME

from dotenv import load_dotenv
load_dotenv()

# =========================
# INIT CLIENT
# =========================

client = Groq(api_key=GROQ_API_KEY)


# =========================
# TEXT CHUNKING
# =========================

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)
        start += (chunk_size - overlap)

    return chunks


# =========================
# BUILD INDEX
# =========================

def build_index_from_pdf(pdf_path):

    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

    documents = []

    for p in pages:
        documents.extend(chunk_text(p))

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(documents)

    return documents, vectorizer, X


# =========================
# RETRIEVE CHUNKS
# =========================

def retrieve_chunks(question, documents, vectorizer, X, top_k=3):

    q_vec = vectorizer.transform([question])
    scores = cosine_similarity(q_vec, X).flatten()

    top_indices = np.argsort(scores)[::-1][:top_k]

    return [documents[i] for i in top_indices]


# =========================
# CALL LLM
# =========================

def call_llm(prompt):

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# ANSWER QUESTION
# =========================

def answer_question(question, documents, vectorizer, X):

    chunks = retrieve_chunks(question, documents, vectorizer, X)

    context = "\n".join(chunks)

    prompt = f"""
You are a helpful assistant.

Answer ONLY using the context below.
If the answer is not in the context, say "I don't know".

Question:
{question}

Context:
{context}
"""

    return call_llm(prompt)