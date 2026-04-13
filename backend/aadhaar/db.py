import psycopg2
from config.settings import DB_URL

def get_connection():
    try:
        return psycopg2.connect(DB_URL, sslmode="require")
    except:
        return None


def fetch_user(aadhaar):

    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM aadhar_data WHERE aadhaar=%s",
        (aadhaar,)
    )

    result = cursor.fetchone()

    conn.close()

    return result