# tone_engine.py
def purify_text(text: str):
    replacements = {"عسر": "يسر مكنون", "شر": "خير مستتر", "جهنم": "مقام العدل"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
