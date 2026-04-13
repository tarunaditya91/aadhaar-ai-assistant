import easyocr

reader = easyocr.Reader(['en'])

def extract_text(image_path):
    results = reader.readtext(image_path)
    text = " ".join([r[1] for r in results])
    return text