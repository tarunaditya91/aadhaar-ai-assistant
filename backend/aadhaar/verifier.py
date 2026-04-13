import re
from difflib import SequenceMatcher


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()) if text else ""


def normalize_aadhaar(a):
    return re.sub(r"\D", "", a)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def calculate_match(db, extracted):

    score = 0

    if similar(normalize_text(db[1]), normalize_text(extracted["name"])) > 0.8:
        score += 1

    if normalize_aadhaar(db[3]) == normalize_aadhaar(extracted["aadhaar"]):
        score += 1

    return (score / 2) * 100