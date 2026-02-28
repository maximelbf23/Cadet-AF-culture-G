#!/usr/bin/env python3
"""
CSV → QCM Converter V4 — Question-Similarity based distractors.

Instead of matching by answer TYPE, this version finds similar QUESTIONS
and uses their answers as wrong options. This guarantees coherent distractors:
- "Combien de pistes à Orly?" → wrong answers from other "combien de pistes" Q
- "Capitale du Costa Rica?" → wrong answers from other "capitale de" Q
- "Code OACI de Haneda?" → wrong answers from other "code OACI" Q
"""
import csv
import json
import re
import os
import random
from collections import Counter

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "kd-tools-quizlet.csv")
JS_PATH = os.path.join(BASE_DIR, "data", "questions.js")

CATEGORY_MAP = {
    "theory": "Technique",
    "history": "Histoire",
    "aircrafts": "Aéronefs",
    "aircraft": "Aéronefs",
    "airline": "Air France & Flotte",
    "airports": "Aéroports",
    "geography": "Géographie",
    "fleet": "Air France & Flotte",
    "military": "Militaire",
    "network": "Réseau",
}

# French stop words to ignore in similarity
STOP_WORDS = {
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "en", "à", "a",
    "est", "que", "qui", "dans", "pour", "au", "sur", "par", "se", "ce",
    "son", "sa", "ses", "il", "elle", "ou", "ne", "pas", "plus", "avec",
    "sont", "cette", "ces", "on", "nous", "vous", "leur", "été", "être",
    "avoir", "entre", "aussi", "même", "tout", "tous", "très", "bien",
    "fait", "faire", "dit", "dire", "deux", "peut", "dont", "comme", "si",
    "quel", "quelle", "quels", "quelles", "d'un", "d'une", "l'", "qu'",
    "d'", "s'", "n'", "c'", "j'", "l'on",
}

def tokenize(text):
    """Extract meaningful words from text."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Zéèêëàâäîïùûüôöçæœ0-9\'-]', ' ', text)
    words = text.split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]

def question_signature(question):
    """Extract a signature that captures 'what type of thing is being asked'.
    This groups similar questions together more aggressively than word overlap."""
    q = question.lower()
    
    # Very specific patterns → very specific signatures
    patterns = [
        (r'code iata', 'CODE_IATA'),
        (r'code oaci|code icao|indicatif oaci', 'CODE_OACI'),
        (r'capitale de|capitale du|quelle est la capitale', 'CAPITALE'),
        (r'quel pays.*capital|pays a pour capital', 'PAYS_CAPITALE'),
        (r'dans quel pays|de quel pays|quel pays', 'PAYS'),
        (r'quelle ville|dans quelle ville', 'VILLE'),
        (r'en quelle année|quel année|année de|date de|quand a', 'ANNEE'),
        (r'qui a inventé|qui a créé|inventeur', 'INVENTEUR'),
        (r'qui a .*premier|première personne|premier pilote|première femme', 'PREMIER'),
        (r'qui est|qui a été|qui fut', 'PERSONNE'),
        (r'fondateur|créateur|fondatrice', 'FONDATEUR'),
        (r'combien de pistes', 'NB_PISTES'),
        (r'combien de passagers|nombre de passagers|millions? de passagers', 'NB_PASSAGERS'),
        (r'combien de.*moteur|nombre de moteurs|combien de réacteurs', 'NB_MOTEURS'),
        (r'combien de places|nombre de sièges|capacité.*passagers|combien de sièges', 'NB_SIEGES'),
        (r'combien de roues', 'NB_ROUES'),
        (r'combien|nombre de|quel est le nombre', 'NOMBRE'),
        (r'mtow|masse maximale|poids max', 'MTOW'),
        (r'envergure', 'ENVERGURE'),
        (r'longueur de|longueur totale', 'LONGUEUR'),
        (r'hauteur de|hauteur totale', 'HAUTEUR'),
        (r'vitesse de croisière|vitesse maximale|vitesse du son|vmo|mmo', 'VITESSE'),
        (r'autonomie|rayon d\'action|distance franchissable|portée', 'AUTONOMIE'),
        (r'altitude de croisière|plafond|altitude max', 'ALTITUDE'),
        (r'quel avion|quel appareil|quel aéronef|quel modèle d\'avion', 'AVION'),
        (r'quel moteur|quelle motorisation|quel réacteur|propulsé par', 'MOTEUR'),
        (r'quel hélicoptère', 'HELICOPTERE'),
        (r'quel chasseur|quel bombardier|quel avion de chasse', 'AVION_MILITAIRE'),
        (r'quel aéroport|nom de l\'aéroport|aéroport principal', 'AEROPORT'),
        (r'quelle compagnie|compagnie aérienne', 'COMPAGNIE'),
        (r'quelle alliance', 'ALLIANCE'),
        (r'signifie|acronyme|signification|que veut dire|que désigne', 'ACRONYME'),
        (r'surnom|surnommé|comment est surnommé', 'SURNOM'),
        (r'dg d\'|directeur général|pdg|président', 'DIRIGEANT'),
        (r'transpondeur|squawk', 'TRANSPONDEUR'),
        (r'immatriculation', 'IMMATRICULATION'),
    ]
    
    for pattern, sig in patterns:
        if re.search(pattern, q):
            return sig
    
    return None  # No specific signature

def compute_similarity(tokens1, tokens2):
    """Jaccard-like similarity with word overlap."""
    if not tokens1 or not tokens2:
        return 0
    set1, set2 = set(tokens1), set(tokens2)
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)

def read_csv_questions(path):
    questions = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            id_display, category, question, answer = row[0], row[1].strip(), row[2].strip(), row[3].strip()
            if not question or not answer or not category or category not in CATEGORY_MAP:
                continue
            question = question.strip('"')
            answer = answer.strip('"')
            tokens = tokenize(question)
            sig = question_signature(question)
            
            questions.append({
                "csv_id": id_display,
                "question": question,
                "correct_answer": answer,
                "csv_category": category,
                "qcm_category": CATEGORY_MAP[category],
                "tokens": tokens,
                "signature": sig,
            })
    return questions

def deduplicate(questions):
    seen = set()
    unique = []
    for q in questions:
        key = q["question"].lower().strip().rstrip("?").rstrip(":").strip()
        if key not in seen:
            seen.add(key)
            unique.append(q)
    return unique

def build_signature_pools(questions):
    """Group answers by question signature."""
    pools = {}
    for q in questions:
        sig = q["signature"]
        if sig:
            if sig not in pools:
                pools[sig] = []
            pools[sig].append(q["correct_answer"])
    return pools

def find_best_distractors(question, all_questions, sig_pools, n=3):
    """Find n best wrong answers for a question using similarity."""
    correct = question["correct_answer"]
    sig = question["signature"]
    tokens = question["tokens"]
    cat = question["csv_category"]
    
    # Strategy 1: Same signature (most reliable)
    if sig and sig in sig_pools:
        pool = [a for a in sig_pools[sig] if a.lower().strip() != correct.lower().strip()]
        if len(pool) >= n:
            random.shuffle(pool)
            return pool[:n]
    
    # Strategy 2: Find most similar questions by word overlap
    scored = []
    for other in all_questions:
        if other["question"] == question["question"]:
            continue
        if other["correct_answer"].lower().strip() == correct.lower().strip():
            continue
        
        sim = 0
        # Bonus for same signature
        if sig and other["signature"] == sig:
            sim += 2.0
        # Bonus for same category
        if other["csv_category"] == cat:
            sim += 0.3
        # Word overlap
        sim += compute_similarity(tokens, other["tokens"])
        
        scored.append((sim, other["correct_answer"]))
    
    # Sort by similarity (highest first) and deduplicate
    scored.sort(key=lambda x: -x[0])
    seen = {correct.lower().strip()}
    result = []
    for sim, ans in scored:
        key = ans.lower().strip()
        if key not in seen:
            seen.add(key)
            result.append(ans)
            if len(result) == n:
                break
    
    # Fallback if still not enough
    while len(result) < n:
        result.append(["Aucune de ces réponses", "Information non disponible", "Donnée inconnue"][len(result)])
    
    return result

def build_qcm_entry(question, all_questions, sig_pools, qcm_id):
    correct = question["correct_answer"]
    wrongs = find_best_distractors(question, all_questions, sig_pools, 3)
    
    options_texts = [correct] + wrongs
    random.shuffle(options_texts)
    
    letters = ["a", "b", "c", "d"]
    correct_letter = letters[options_texts.index(correct)]
    options = [{"id": letters[i], "text": options_texts[i]} for i in range(4)]
    
    return {
        "id": qcm_id,
        "question": question["question"],
        "options": options,
        "answer": correct_letter,
        "explanation": "",
        "category": question["qcm_category"]
    }

def read_existing_js(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    qcm_match = re.search(r'const qcmData = (\[.*?\]);', content, re.DOTALL)
    fc_match = re.search(r'const flashcardData = (\[.*?\]);', content, re.DOTALL)
    qcm_data = json.loads(qcm_match.group(1)) if qcm_match else []
    fc_data = json.loads(fc_match.group(1)) if fc_match else []
    return qcm_data, fc_data

def write_js(path, qcm_data, fc_data):
    out = f"// PSY0 Training Data - V5 - Auto-generated\n"
    out += f"// {len(qcm_data)} questions + {len(fc_data)} flashcards\n\n"
    out += f"const qcmData = {json.dumps(qcm_data, ensure_ascii=False, indent=2)};\n\n"
    out += f"const flashcardData = {json.dumps(fc_data, ensure_ascii=False, indent=2)};\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)

def main():
    print("=== CSV → QCM Converter V4 (Question Similarity) ===\n")
    
    csv_questions = read_csv_questions(CSV_PATH)
    print(f"📄 CSV: {len(csv_questions)} questions")
    
    csv_questions = deduplicate(csv_questions)
    print(f"🔄 Unique: {len(csv_questions)}")
    
    # Signature stats
    sig_counts = Counter(q["signature"] for q in csv_questions if q["signature"])
    print(f"\n📊 Signatures détectées ({len(sig_counts)} types):")
    for sig, cnt in sig_counts.most_common(20):
        print(f"   {sig}: {cnt} questions")
    no_sig = sum(1 for q in csv_questions if not q["signature"])
    print(f"   (sans signature): {no_sig}")
    
    # Build pools
    sig_pools = build_signature_pools(csv_questions)
    
    # Read existing
    existing_qcm, fc_data = read_existing_js(JS_PATH)
    original_qcm = [q for q in existing_qcm if q["id"] <= 350]
    print(f"\n📦 Originaux: {len(original_qcm)} QCM | {len(fc_data)} flashcards")
    
    existing_questions = set(q["question"].lower().strip() for q in original_qcm)
    next_id = max((q["id"] for q in original_qcm), default=0) + 1
    
    # Convert
    print(f"\n⚙️ Génération des QCM (peut prendre ~30s)...")
    new_qcm = []
    skipped = 0
    for i, q in enumerate(csv_questions):
        if q["question"].lower().strip() in existing_questions:
            skipped += 1
            continue
        qcm_entry = build_qcm_entry(q, csv_questions, sig_pools, next_id)
        new_qcm.append(qcm_entry)
        existing_questions.add(q["question"].lower().strip())
        next_id += 1
        if (i + 1) % 500 == 0:
            print(f"   ... {i+1}/{len(csv_questions)}")
    
    all_qcm = original_qcm + new_qcm
    print(f"\n➕ {len(new_qcm)} QCM ({skipped} doublons)")
    print(f"📇 Total: {len(all_qcm)} QCM + {len(fc_data)} flashcards")
    
    write_js(JS_PATH, all_qcm, fc_data)
    
    # Quality check with diverse samples
    print(f"\n🔍 Échantillon de vérification:")
    # Pick samples from different signatures
    sig_samples = {}
    for q in new_qcm:
        # Find matching CSV question's signature
        for csv_q in csv_questions:
            if csv_q["question"] == q["question"]:
                sig = csv_q.get("signature", "none")
                if sig not in sig_samples:
                    sig_samples[sig] = q
                break
    
    for sig, q in list(sig_samples.items())[:12]:
        print(f"\n   [{sig}] Q: {q['question'][:80]}")
        for o in q['options']:
            m = '✓' if o['id'] == q['answer'] else ' '
            print(f"     [{m}] {o['text'][:70]}")

    print(f"\n✅ Done!")

if __name__ == "__main__":
    main()
