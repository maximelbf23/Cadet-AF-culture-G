#!/usr/bin/env python3
"""Convert kd-tools-quizlet.csv questions into flashcards and merge into questions.js."""
import csv
import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "kd-tools-quizlet.csv")
JS_PATH = os.path.join(BASE_DIR, "data", "questions.js")

# Category mapping: CSV category → Flashcard category
CATEGORY_MAP = {
    "theory": "Technique",
    "history": "Dates Clés",
    "aircrafts": "Flotte",
    "aircraft": "Flotte",
    "airline": "Air France",
    "airports": "Navigation",
    "geography": "Géographie",
    "fleet": "Flotte",
    "military": "Militaire",
    "network": "Air France",
}

def read_csv_questions(path):
    """Read CSV and return list of (question, answer, category) tuples."""
    questions = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        print(f"CSV header: {header}")
        
        for i, row in enumerate(reader, start=2):
            if len(row) < 4:
                continue
            
            id_display, category, question, answer = row[0], row[1], row[2], row[3]
            
            # Skip empty or malformed entries
            if not question.strip() or not answer.strip():
                continue
            if not category.strip() or category.strip() not in CATEGORY_MAP:
                continue
            
            # Clean up question (remove leading quotes, numbers, etc.)
            question = question.strip().strip('"')
            answer = answer.strip().strip('"')
            
            questions.append({
                "question": question,
                "answer": answer,
                "category": CATEGORY_MAP.get(category.strip(), "Général"),
                "csv_id": id_display
            })
    
    return questions

def deduplicate(questions):
    """Remove duplicate questions (keep first occurrence)."""
    seen = set()
    unique = []
    for q in questions:
        # Normalize question for comparison
        key = q["question"].lower().strip().rstrip("?").rstrip(":").strip()
        if key not in seen:
            seen.add(key)
            unique.append(q)
    return unique

def read_existing_js(path):
    """Read existing questions.js and extract qcmData and flashcardData."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract qcmData
    qcm_match = re.search(r'const qcmData = (\[.*?\]);', content, re.DOTALL)
    # Extract flashcardData
    fc_match = re.search(r'const flashcardData = (\[.*?\]);', content, re.DOTALL)
    
    qcm_data = json.loads(qcm_match.group(1)) if qcm_match else []
    fc_data = json.loads(fc_match.group(1)) if fc_match else []
    
    return qcm_data, fc_data

def build_flashcards(csv_questions, existing_flashcards):
    """Build the merged flashcard array."""
    # Start with existing flashcards
    all_flashcards = list(existing_flashcards)
    next_id = max((fc["id"] for fc in all_flashcards), default=0) + 1
    
    # Track existing questions to avoid duplicates
    existing_fronts = set(fc.get("front", "").lower().strip() for fc in all_flashcards)
    
    added = 0
    for q in csv_questions:
        front = q["question"]
        if front.lower().strip() in existing_fronts:
            continue
        
        all_flashcards.append({
            "id": next_id,
            "front": front,
            "back": q["answer"],
            "category": q["category"]
        })
        existing_fronts.add(front.lower().strip())
        next_id += 1
        added += 1
    
    return all_flashcards, added

def write_js(path, qcm_data, fc_data):
    """Write the updated questions.js file."""
    out = f"// PSY0 Training Data - V3 - Auto-generated\n"
    out += f"// {len(qcm_data)} questions + {len(fc_data)} flashcards\n\n"
    out += f"const qcmData = {json.dumps(qcm_data, ensure_ascii=False, indent=2)};\n\n"
    out += f"const flashcardData = {json.dumps(fc_data, ensure_ascii=False, indent=2)};\n"
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)

def main():
    print("=== CSV → Flashcards Converter ===\n")
    
    # 1. Read CSV
    csv_questions = read_csv_questions(CSV_PATH)
    print(f"📄 CSV: {len(csv_questions)} questions lues")
    
    # 2. Deduplicate
    csv_questions = deduplicate(csv_questions)
    print(f"🔄 Après déduplication: {len(csv_questions)} questions uniques")
    
    # 3. Category breakdown
    cats = {}
    for q in csv_questions:
        cats[q["category"]] = cats.get(q["category"], 0) + 1
    print(f"\n📊 Répartition par catégorie:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    # 4. Read existing JS
    qcm_data, existing_fc = read_existing_js(JS_PATH)
    print(f"\n📦 Existant: {len(qcm_data)} QCM + {len(existing_fc)} flashcards")
    
    # 5. Merge flashcards
    all_flashcards, added = build_flashcards(csv_questions, existing_fc)
    print(f"➕ {added} nouvelles flashcards ajoutées")
    print(f"📇 Total flashcards: {len(all_flashcards)}")
    
    # 6. Write output
    write_js(JS_PATH, qcm_data, all_flashcards)
    print(f"\n✅ Fichier questions.js mis à jour avec {len(qcm_data)} QCM + {len(all_flashcards)} flashcards")

if __name__ == "__main__":
    main()
