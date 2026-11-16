import re
try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    _stemmer = StemmerFactory().create_stemmer()
except Exception:
    _stemmer = None

# Stopwords Bahasa Indonesia yang umum. Kata penting seperti "tidak", "bukan",
# "belum", dan "tanpa" sengaja dipertahankan karena dapat mengubah maksud kalimat.
STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "apa", "berapa",
    "saya", "aku", "ingin", "mau", "dong", "kah", "nya", "ada", "atau",
    "ini", "itu", "apakah", "bisa", "tolong", "jadi", "akan", "sudah",
    "sedang", "pada", "dalam", "oleh", "sebuah", "seorang", "para",
    "aja", "saja", "nih", "sih", "ya", "deh", "kok", "pun", "lah",
    "kami", "kita", "kamu", "anda", "dia", "mereka", "nya", "tersebut"
}

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) > 1]
    cleaned = " ".join(tokens)
    if _stemmer:
        cleaned = _stemmer.stem(cleaned)
    return cleaned
