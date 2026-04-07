import json
import os

# المسار الموحد للملف
file_path = os.path.join('data', 'quran_roots_complete.json')

def run_purification():
    if not os.path.exists(file_path):
        print(f"❌ خطأ: لم يتم العثور على الملف في: {file_path}")
        return

    print("⏳ جاري قراءة وتطهير 11 ألف سطر... يرجى الانتظار.")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    clean_roots = []
    for entry in data.get("roots", []):
        # استخراج الجذر وتنظيفه من الشوائب التقنية
        raw_root = entry.get("root") or entry.get("lemma") or entry.get("word") or ""
        clean_root = str(raw_root).replace("LEM:", "").replace("ROOT:", "").replace("Part:", "").strip()
        
        if not clean_root: continue

        # بناء السجل بالأسماء التي يبحث عنها الـ App حالياً
        standard_entry = {
            "root": clean_root,
            "orbit_hint": entry.get("orbit_hint") or "فتح",
            "verse": entry.get("verse") or entry.get("text") or entry.get("ayah") or "آية المدار الحكيمة",
            "surah": entry.get("surah") or entry.get("sura") or entry.get("surah_name") or "القرآن",
            "frequency": entry.get("frequency") or entry.get("freq") or 0
        }
        clean_roots.append(standard_entry)

    # تحديث البيانات وحفظها بنفس الاسم لاستبدال القديم
    data["roots"] = clean_roots
    data["metadata"]["status"] = "V71_10_PURE"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ تم التطهير بنجاح! تم معالجة {len(clean_roots)} جذراً.")
    print(f"📍 الملف المحدث جاهز الآن في: {file_path}")

if __name__ == "__main__":
    run_purification()
