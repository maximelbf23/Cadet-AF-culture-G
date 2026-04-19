#!/usr/bin/env python3
"""
Fix distractor options for CSV-generated QCM questions using Claude API.
Processes questions with id > 350 (auto-generated distractors).
Restart-safe: skips already-processed questions via a progress file.
"""
import json
import os
import time
import random
import re

# Load .env if present (ANTHROPIC_API_KEY=sk-ant-...)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

import anthropic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "questions.json")
JS_PATH   = os.path.join(BASE_DIR, "data", "questions.js")
PROGRESS_PATH = os.path.join(BASE_DIR, "data", "fix_progress.json")

BATCH_SIZE = 25
MAX_RETRIES = 3
LETTERS = ["a", "b", "c", "d"]


# ─────────────────────────────────────────────
# I/O helpers
# ─────────────────────────────────────────────

def load_data():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Mirror to questions.js so the HTML app stays in sync
    qcm = data["qcm"]
    fc  = data.get("flashcards", [])
    out = f"// PSY0 Training Data - V6 - Auto-generated\n"
    out += f"// {len(qcm)} questions + {len(fc)} flashcards\n\n"
    out += f"const qcmData = {json.dumps(qcm, ensure_ascii=False, indent=2)};\n\n"
    out += f"const flashcardData = {json.dumps(fc, ensure_ascii=False, indent=2)};\n"
    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write(out)

def load_progress():
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH, "r") as f:
            return set(json.load(f)["fixed_ids"])
    return set()

def save_progress(fixed_ids: set):
    with open(PROGRESS_PATH, "w") as f:
        json.dump({"fixed_ids": list(fixed_ids)}, f)


# ─────────────────────────────────────────────
# Claude call
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es un expert en culture aéronautique, préparation PSY0 Air France et pédagogie.
Tu génères des distracteurs (mauvaises réponses) pour des QCM. Règles absolues :
- Même TYPE que la bonne réponse (date→dates, nom→noms, ville→villes, modèle d'avion→modèles d'avion, code OACI→codes OACI, etc.)
- Plausibles et trompeurs : un candidat qui n'est pas sûr pourrait choisir ces réponses
- Jamais identiques ou quasi-identiques à la bonne réponse
- Tous différents entre eux
- En cohérence avec le domaine de la question (aviation civile, Air France, géographie, histoire de l'aviation, technique de vol)
- En français sauf noms propres et sigles"""

def extract_json(text: str):
    """Robustly extract a JSON array from Claude's response."""
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Strip markdown code blocks
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # Find first [ ... ] block
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError("No valid JSON array found in response")

def fix_batch(client: anthropic.Anthropic, batch: list[dict]) -> list[dict]:
    """
    Send a batch of {qcm_id, question, correct_answer, category} dicts to Claude.
    Returns list of {qcm_id, distractors: [str, str, str]}.
    """
    lines = []
    for item in batch:
        lines.append(
            f'[{item["qcm_id"]}] Catégorie: {item["category"]}\n'
            f'Question: {item["question"]}\n'
            f'Bonne réponse: {item["correct_answer"]}'
        )
    user_msg = (
        "Génère 3 distracteurs pour chaque question. "
        "Réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après :\n"
        '[\n  {"qcm_id": <id>, "distractors": ["mauvaise1", "mauvaise2", "mauvaise3"]},\n  ...\n]\n\n'
        + "\n\n".join(lines)
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=3000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            return extract_json(response.content[0].text)
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"  ⚠ Tentative {attempt} échouée : {e} — retry dans 5s")
            time.sleep(5)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=== Fix Distractors — Claude Haiku ===\n")

    data = load_data()
    q_map = {q["id"]: q for q in data["qcm"]}
    fixed_ids = load_progress()

    # Only fix CSV-generated questions (id > 350) not yet processed
    to_fix = [
        q for q in data["qcm"]
        if q["id"] > 350 and q["id"] not in fixed_ids
    ]
    total = len(to_fix)
    print(f"Questions à corriger : {total}  (déjà traitées : {len(fixed_ids)})\n")

    if total == 0:
        print("✅ Rien à faire — toutes les questions ont déjà été corrigées.")
        return

    client = anthropic.Anthropic()
    n_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    errors = []

    for batch_start in range(0, total, BATCH_SIZE):
        batch_qs = to_fix[batch_start : batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1

        # Build the prepared list
        batch_prepared = []
        for q in batch_qs:
            correct_text = next(
                o["text"] for o in q["options"] if o["id"] == q["answer"]
            )
            batch_prepared.append({
                "qcm_id":         q["id"],
                "question":       q["question"],
                "correct_answer": correct_text,
                "category":       q.get("category", ""),
            })

        id_range = f'{batch_qs[0]["id"]}–{batch_qs[-1]["id"]}'
        print(f"Batch {batch_num:3d}/{n_batches}  IDs {id_range} ...", end=" ", flush=True)

        try:
            results = fix_batch(client, batch_prepared)

            # Build a lookup by qcm_id
            result_map = {r["qcm_id"]: r["distractors"] for r in results}

            for item in batch_prepared:
                qid = item["qcm_id"]
                distractors = result_map.get(qid)
                if not distractors or len(distractors) < 3:
                    print(f"⚠ ID {qid} : distracteurs manquants, skip")
                    continue

                q = q_map[qid]
                correct_text = item["correct_answer"]

                # Rebuild 4 options: correct + 3 wrong, shuffled
                all_texts = [correct_text] + distractors[:3]
                random.shuffle(all_texts)
                q["options"] = [{"id": LETTERS[i], "text": all_texts[i]} for i in range(4)]
                q["answer"]  = next(LETTERS[i] for i in range(4) if all_texts[i] == correct_text)
                fixed_ids.add(qid)

            # Save after every batch
            save_data(data)
            save_progress(fixed_ids)
            print(f"✓  ({len(fixed_ids)} total corrigées)")

        except Exception as e:
            print(f"❌ ERREUR : {e}")
            errors.append({"batch": batch_num, "ids": [q["id"] for q in batch_qs], "error": str(e)})
            # Continue with next batch
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"✅ Terminé. {len(fixed_ids)} questions corrigées.")
    if errors:
        print(f"⚠  {len(errors)} batch(es) en erreur :")
        for err in errors:
            print(f"   Batch {err['batch']} (IDs {err['ids'][0]}–{err['ids'][-1]}): {err['error']}")
    else:
        # Clean up progress file
        if os.path.exists(PROGRESS_PATH):
            os.remove(PROGRESS_PATH)
        print("Fichier de progression supprimé.")

if __name__ == "__main__":
    main()
