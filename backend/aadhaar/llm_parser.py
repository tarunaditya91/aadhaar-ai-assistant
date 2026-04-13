import re
import json
from groq import Groq
from config.settings import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

def extract_aadhaar_details(text):

    prompt = f"""
Extract Aadhaar details and return JSON:

{{
  "name": "",
  "dob": "",
  "aadhaar": "",
  "gender": ""
}}

Text:
{text}
"""

    try:
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        output = res.choices[0].message.content

        match = re.search(r"\{.*\}", output, re.DOTALL)

        if match:
            return json.loads(match.group())

        return None

    except Exception as e:
        return {"error": str(e)}