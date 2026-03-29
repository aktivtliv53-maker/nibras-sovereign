# state_engine.py
STATE_TAGS = {"سكن": "لبث", "نفس": "لبث", "روح": "لبث", "مكث": "مكث", "ظهر": "مكث", "بني": "مكث"}
def detect_state(roots: list):
    states = [STATE_TAGS.get(r, "استقرار") for r in roots]
    return max(set(states), key=states.count) if states else "استقرار"
