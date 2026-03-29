# letter_engine.py (المحدث v20.2)
def analyze_word_letters(word: str):
    # (نفس القاموس السابق LETTER_MAP)
    letters = [ch for ch in word if ch in LETTER_MAP]
    if not letters: return None
    details = [LETTER_MAP[l] for l in letters]
    vectors = [d["vector"] for d in details]
    return {
        "dominant_vector": max(set(vectors), key=vectors.count) if vectors else "محايد",
        "details": details
    }
