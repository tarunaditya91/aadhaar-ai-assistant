from groq import Groq
from config.settings import GROQ_API_KEY, MODEL_NAME

# =========================
# INIT CLIENT
# =========================

client = Groq(api_key=GROQ_API_KEY)


# =========================
# GENERATE QUESTIONS
# =========================

def generate_followup_questions(question, retrieved_chunks):

    context = "\n".join(retrieved_chunks)

    prompt = f"""
You are a smart assistant.

Based ONLY on the context below, generate exactly 3 follow-up questions.

Rules:
- Questions must be answerable from the context
- Do not repeat the original question
- Keep each question short (under 20 words)
- Make them meaningful

Return ONLY JSON:
{{
  "questions": [
    "question 1",
    "question 2",
    "question 3"
  ]
}}

Question:
{question}

Context:
{context}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        output = response.choices[0].message.content

        import json
        import re

        match = re.search(r"\{.*\}", output, re.DOTALL)

        if match:
            return json.loads(match.group())

        return {"questions": []}

    except Exception as e:
        return {"questions": [], "error": str(e)}