#!/usr/bin/env python3
"""
Fix distractor options for CSV-generated QCM questions — 100% local, no API.

Strategy (applied in priority order for each question):
  1. Type pool        : distractors of the exact same semantic type (year, IATA, aircraft…)
                        filtered to same category/signature when possible
  2. Signature pool   : answers from questions with the same question pattern
  3. Category pool    : answers from the same category
  4. Global pool      : any answer of compatible type in the dataset
"""

from __future__ import annotations
import json
import os
import re
import random
from collections import defaultdict
from typing import Optional, List

random.seed(42)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "questions.json")
JS_PATH   = os.path.join(BASE_DIR, "data", "questions.js")

LETTERS = ["a", "b", "c", "d"]

# ──────────────────────────────────────────────────────────────
# QUESTION SIGNATURE  (same as convert_csv_to_qcm.py)
# ──────────────────────────────────────────────────────────────
SIGNATURE_PATTERNS = [
    (r'code iata',                                  "CODE_IATA"),
    (r'code oaci|code icao|indicatif oaci',         "CODE_OACI"),
    (r'capitale de|capitale du|quelle est la capitale|capitale\s+\?', "CAPITALE"),
    (r'quel pays.*capital|pays a pour capital',     "PAYS_CAPITALE"),
    (r'dans quel pays|de quel pays|quel pays',      "PAYS"),
    (r'quelle ville|dans quelle ville',             "VILLE"),
    (r'en quelle année|quelle année|année de|date de|quand a|quel an', "ANNEE"),
    (r'qui a inventé|qui a créé|inventeur',         "INVENTEUR"),
    (r'premier pilote|première personne|première femme|premier vol', "PREMIER"),
    (r'qui est|qui a été|qui fut|comment s.appel',  "PERSONNE"),
    (r'fondateur|créateur|fondatrice',              "FONDATEUR"),
    (r'surnom|surnommé|comment est surnommé',       "SURNOM"),
    (r'combien de pistes',                          "NB_PISTES"),
    (r'combien de passagers|nombre de passagers|millions? de passagers', "NB_PASSAGERS"),
    (r'combien de.*moteur|nombre de moteurs|combien de réacteurs', "NB_MOTEURS"),
    (r'combien de places|nombre de sièges|capacité.*passagers|combien de sièges', "NB_SIEGES"),
    (r'combien de roues',                           "NB_ROUES"),
    (r'combien|nombre de|quel est le nombre',       "NOMBRE"),
    (r'mtow|masse maximale|poids max',              "MTOW"),
    (r'envergure',                                  "ENVERGURE"),
    (r'longueur de|longueur totale',                "LONGUEUR"),
    (r'hauteur de|hauteur totale',                  "HAUTEUR"),
    (r'vitesse de croisière|vitesse maximale|vitesse du son|vmo|mmo', "VITESSE"),
    (r'autonomie|rayon d.action|distance franchissable|portée', "AUTONOMIE"),
    (r'altitude de croisière|plafond|altitude max', "ALTITUDE"),
    (r'quel avion|quel appareil|quel aéronef|quel modèle d.avion', "AVION"),
    (r'quel moteur|quelle motorisation|quel réacteur|propulsé par', "MOTEUR"),
    (r'quel hélicoptère',                           "HELICOPTERE"),
    (r'quel chasseur|quel bombardier|quel avion de chasse', "AVION_MILITAIRE"),
    (r'quel aéroport|nom de l.aéroport|aéroport principal', "AEROPORT"),
    (r'quelle compagnie|compagnie aérienne',        "COMPAGNIE"),
    (r'quelle alliance',                            "ALLIANCE"),
    (r'signifie|acronyme|signification|que veut dire|que désigne|a quoi sert|quel est le rôle', "ACRONYME"),
    (r'dg d.|directeur général|pdg|président',      "DIRIGEANT"),
    (r'transpondeur|squawk',                        "SQUAWK"),
    (r'immatriculation',                            "IMMATRICULATION"),
    (r'durée|temps de vol|combien de temps',        "DUREE"),
    (r'pourcentage|part de|taux',                   "POURCENTAGE"),
    (r'créateur|styliste|designer|uniforme',        "CREATEUR"),
]

def question_signature(question: str) -> Optional[str]:
    q = question.lower()
    for pattern, sig in SIGNATURE_PATTERNS:
        if re.search(pattern, q):
            return sig
    return None


# ──────────────────────────────────────────────────────────────
# ANSWER TYPE DETECTION
# ──────────────────────────────────────────────────────────────
def detect_type(answer: str) -> str:
    a = answer.strip()

    # Year (1600–2100, standalone)
    if re.match(r'^(1[6-9]\d{2}|20\d{2}|21\d{2})$', a):
        return "YEAR"

    # Mach number
    if re.match(r'^Mach\s*\d+[,.]?\d*$', a, re.I):
        return "MACH"

    # Percentage
    if re.match(r'^\d+[,.]?\d*\s*%$', a):
        return "PERCENTAGE"

    # Duration  "3h30", "11h", "45 min", "1h30min"
    if re.match(r'^\d+\s*h(?:\d+)?(?:\s*min)?$', a, re.I) or re.match(r'^\d+\s*min$', a, re.I):
        return "DURATION"

    # Distance with unit
    if re.match(r'^\d[\d\s,\.]*\s*(km|nm|milles?|miles?)$', a, re.I):
        return "DISTANCE"

    # Weight / MTOW
    if re.match(r'^\d[\d\s,\.]*\s*(t|kg|tonnes?)$', a, re.I):
        return "WEIGHT"

    # Length / wingspan
    if re.match(r'^\d[\d\s,\.]*\s*m$', a, re.I) and not re.search(r'km', a, re.I):
        return "LENGTH"

    # Altitude  "FL350", "35 000 ft", "12 500 m"
    if re.match(r'^FL\s*\d+$', a, re.I) or re.match(r'^\d[\d\s,\.]*\s*ft$', a, re.I):
        return "ALTITUDE"

    # Speed  "850 km/h", "450 kts"
    if re.match(r'^\d[\d\s,\.]*\s*(km/h|kts?|nœuds?|mph|kt)$', a, re.I):
        return "SPEED"

    # Generic number  "4 276", "853", "2"
    if re.match(r'^\d[\d\s]*$', a):
        return "NUMBER"

    # Squawk code (4 digits — covered by NUMBER above; explicit alias)
    if re.match(r'^\d{4}$', a):
        return "SQUAWK"

    # IATA code  "CDG", "BOD"
    if re.match(r'^[A-Z]{3}$', a):
        return "IATA"

    # ICAO code  "LFPG", "KLAX"
    if re.match(r'^[A-Z]{4}$', a):
        return "ICAO"

    # Aircraft variant / sub-model  "200 LR", "300ER", "MAX 10", "-800", "XWB"
    if re.match(r'^(?:\d{3}\s?(?:ER|LR|F|X|XWB|neo|ceo|MAX)?|MAX\s*\d+|XWB|-\d{3})$', a, re.I):
        return "AIRCRAFT_VARIANT"

    # Civil aircraft model  A320, Boeing 777, ATR 72…
    if re.match(
        r'^(?:Airbus\s+)?A[23]\d{2}(?:neo|ceo|-\d+)?'
        r'|^(?:Boeing\s+)?B?7[0-9]{2}(?:-\d+\w*)?'
        r'|^ATR[\s-]?\d+'
        r'|^(?:CRJ|ERJ|Embraer)\s*\d+'
        r'|^(?:De Havilland|DHC|Bombardier)',
        a, re.I
    ):
        return "AIRCRAFT_CIVIL"

    # Military aircraft
    if re.match(
        r'^(?:F[-\s]\d|MiG[-\s]\d|Su[-\s]\d|Rafale|Mirage|Eurofighter'
        r'|Spitfire|Hurricane|Typhoon|Gripen|P-\d+|B-\d+|F/A-\d+)',
        a, re.I
    ):
        return "AIRCRAFT_MILITARY"

    # Engine / powerplant
    if re.match(
        r'^(?:GE9|CFM\d|Trent|LEAP|PW\d|Olympus|Merlin|RB\d|V2500|M88|EJ200)',
        a, re.I
    ):
        return "ENGINE"

    # Acronym / code (2–6 uppercase chars)
    if re.match(r'^[A-Z]{2,6}$', a):
        return "ACRONYM"

    # Person name: multiple words, all starting with uppercase, no digits
    words = a.split()
    if (2 <= len(words) <= 5
            and not re.search(r'\d', a)
            and all(w[0].isupper() for w in words if w[0].isalpha())):
        lower = [w.lower() for w in words]
        # Place phrases contain French particles
        PARTICLES = {"de", "du", "la", "le", "les", "des", "d", "l", "en", "au", "aux"}
        if any(p in PARTICLES for p in lower[1:]):
            return "PLACE"
        return "PERSON"

    # Single capitalised word  "France", "Paris", "Concorde"
    if re.match(r'^[A-Z][a-zA-Zéèêëàâäîïùûüôöçæœ\-]+$', a) and len(a) > 2:
        return "PLACE_OR_WORD"

    return "OTHER"


# Common French nouns that should NOT appear as person-name distractors
_NOT_PERSON_WORDS = {
    "animaux", "animal", "oiseaux", "oiseau", "hommes", "homme", "femmes", "femme",
    "pilotes", "pilote", "avions", "avion", "moteurs", "moteur", "ailes", "aile",
    "passagers", "passager", "équipages", "équipage", "frères", "frère", "soeurs",
    "plusieurs", "certains", "aucun", "tous", "chacun", "nations", "pays", "villes",
}

def _is_plausible_person(answer: str) -> bool:
    """Return False if the answer looks like a common noun phrase rather than a person name."""
    words = answer.lower().split()
    return not any(w in _NOT_PERSON_WORDS for w in words)


# ──────────────────────────────────────────────────────────────
# POOL BUILDING
# ──────────────────────────────────────────────────────────────
def build_pools(qcm: List[dict]) -> dict:
    """
    Build lookup tables:
      pools["type"]             → set of answers
      pools["type|cat"]         → set of answers  (type + category)
      pools["sig|<SIG>"]        → set of answers  (question signature)
      pools["sig|<SIG>|cat"]    → set of answers
    """
    pools = defaultdict(set)

    for q in qcm:
        correct = next(o["text"] for o in q["options"] if o["id"] == q["answer"])
        cat  = q.get("category", "")
        sig  = question_signature(q["question"])
        atype = detect_type(correct)

        pools[f"type|{atype}"].add(correct)
        pools[f"type|{atype}|cat|{cat}"].add(correct)
        if sig:
            pools[f"sig|{sig}"].add(correct)
            pools[f"sig|{sig}|cat|{cat}"].add(correct)

    return pools


# ──────────────────────────────────────────────────────────────
# DISTRACTOR SELECTION
# ──────────────────────────────────────────────────────────────
def pick_distractors(correct: str, q: dict, pools: dict, n: int = 3) -> List[str]:
    """Return n distractors, never equal to correct."""
    atype = detect_type(correct)
    cat   = q.get("category", "")
    sig   = question_signature(q["question"])
    excl  = {correct.lower().strip()}

    # Max acceptable distractor length: 3× correct length or 120 chars, whichever is larger
    max_len = max(len(correct) * 3, 120)
    correct_lc = correct.lower().strip()

    # Normalise numbers for similarity check (remove spaces from digit sequences)
    def _norm(s: str) -> str:
        return re.sub(r'(\d)\s+(\d)', r'\1\2', s.lower().strip())

    correct_norm = _norm(correct)

    def too_similar(a: str) -> bool:
        """True if a is a substring of correct, correct is a substring of a,
        or they are numerically identical (ignoring spaces)."""
        a_lc = a.lower().strip()
        if a_lc in correct_lc or correct_lc in a_lc:
            return True
        return _norm(a) == correct_norm

    def candidates(pool_key: str, enforce_type: bool = True) -> list[str]:
        return [
            a for a in pools.get(pool_key, set())
            if a.lower().strip() not in excl
            and "\n" not in a
            and len(a) <= max_len
            and not too_similar(a)
            and (not enforce_type or detect_type(a) == atype)
            and (atype != "PERSON" or _is_plausible_person(a))
        ]

    # Priority list of pool keys to try (all filtered to same answer type)
    priority = []
    if sig:
        priority.append(f"sig|{sig}|cat|{cat}")
        priority.append(f"sig|{sig}")
    priority.append(f"type|{atype}|cat|{cat}")
    priority.append(f"type|{atype}")

    result: List[str] = []
    seen = set(excl)

    for key in priority:
        pool = [a for a in candidates(key) if a.lower().strip() not in seen]
        random.shuffle(pool)
        for a in pool:
            result.append(a)
            seen.add(a.lower().strip())
            if len(result) == n:
                return result

    # Last resort generic fallbacks per type (before broad category pool)
    GENERIC: dict[str, list[str]] = {
        "YEAR":     ["1920", "1955", "1978", "1995", "2001", "2015", "1968", "1985"],
        "IATA":     ["CDG", "LHR", "JFK", "DXB", "AMS", "FCO", "MAD", "BCN", "FRA", "SYD"],
        "ICAO":     ["LFPG", "EGLL", "KJFK", "OMDB", "EHAM", "LIRF", "LEMD", "EDDF"],
        "MACH":     ["Mach 0.82", "Mach 0.85", "Mach 0.78", "Mach 2.0", "Mach 3.3"],
        "ALTITUDE": ["FL310", "FL350", "FL370", "FL410", "12 000 m", "10 000 ft"],
        "SPEED":    ["850 km/h", "920 km/h", "780 km/h", "450 kts", "600 km/h"],
        "DISTANCE": ["5 000 km", "8 000 km", "12 000 km", "3 500 km", "15 000 km"],
        "WEIGHT":   ["280 t", "351 t", "560 t", "180 t", "73 t"],
        "LENGTH":   ["60,3 m", "73,9 m", "48,5 m", "38,0 m", "66,8 m"],
        "DURATION": ["3h", "5h30", "8h", "12h30", "2h30", "14h", "9h", "7h", "16h", "4h"],
        "NUMBER":   ["100", "250", "500", "1 000", "2 500", "10 000"],
        "PERCENTAGE": ["15%", "25%", "40%", "51%", "66%"],
        "AIRCRAFT_VARIANT":   ["300ER", "200ER", "777X", "MAX 10", "900", "800", "XWB"],
        "AIRCRAFT_CIVIL":     ["A320", "B777", "A350", "B787", "A380", "A220", "B737"],
        "AIRCRAFT_MILITARY":  ["Rafale", "Mirage 2000", "F-16", "Eurofighter", "MiG-29"],
        "ENGINE":   ["CFM56", "GE90", "Trent XWB", "LEAP-1A", "PW1100G"],
        "PERSON":   ["Antoine de Saint-Exupéry", "Jean Mermoz", "Henri Guillaumet",
                     "Louis Blériot", "Roland Garros", "Didier Daurat"],
        "PLACE":    ["Paris", "Londres", "New York", "Tokyo", "Dubaï", "Francfort"],
        "PLACE_OR_WORD": ["Paris", "Londres", "Airbus", "Boeing", "Concorde", "Caravelle"],
        "ACRONYM":  ["ILS", "VOR", "DME", "NDB", "ATIS", "METAR", "SIGMET"],
    }
    for a in GENERIC.get(atype, ["—", "Non applicable", "Donnée non disponible"]):
        if a.lower().strip() not in seen:
            result.append(a)
            seen.add(a.lower().strip())
            if len(result) == n:
                return result

    # Broad pool: same category, any type (last resort before hardcoded strings)
    broad_pool = [
        a for a in pools.get(f"type|OTHER|cat|{cat}", set())
        if a.lower().strip() not in seen and "\n" not in a and len(a) <= max_len
    ]
    random.shuffle(broad_pool)
    for a in broad_pool:
        result.append(a)
        seen.add(a.lower().strip())
        if len(result) == n:
            return result

    # Absolute last resort
    while len(result) < n:
        result.append(["Non applicable", "Donnée inconnue", "Aucune de ces réponses"][len(result) % 3])

    return result


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    print("=== Fix Distractors — Local Algorithm V2 ===\n")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    qcm = data["qcm"]
    q_map = {q["id"]: q for q in qcm}

    print(f"Total questions  : {len(qcm)}")
    csv_qs = [q for q in qcm if q["id"] > 350]
    print(f"À régénérer (id>350) : {len(csv_qs)}")

    # Build pools from ALL questions (originals included → richer pools)
    print("Construction des pools…")
    pools = build_pools(qcm)
    print(f"  {len(pools)} pools construits\n")

    # Stats on pool sizes for key types
    for t in ["YEAR", "IATA", "ICAO", "AIRCRAFT_CIVIL", "PERSON", "PLACE", "PLACE_OR_WORD", "NUMBER"]:
        k = f"type|{t}"
        print(f"  Pool {t:20s}: {len(pools.get(k, set()))} entrées")
    print()

    fixed = 0
    type_stats = defaultdict(int)

    for q in csv_qs:
        correct_text = next(o["text"] for o in q["options"] if o["id"] == q["answer"])
        atype = detect_type(correct_text)
        type_stats[atype] += 1

        distractors = pick_distractors(correct_text, q, pools, n=3)

        # Rebuild options with correct answer + new distractors, shuffled
        all_texts = [correct_text] + distractors
        random.shuffle(all_texts)
        q["options"] = [{"id": LETTERS[i], "text": all_texts[i]} for i in range(4)]
        q["answer"]  = next(LETTERS[i] for i in range(4) if all_texts[i] == correct_text)
        fixed += 1

    print(f"✅ {fixed} questions régénérées\n")
    print("Distribution des types de réponses :")
    for t, n in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"  {t:25s}: {n}")

    # Save questions.json
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 questions.json mis à jour")

    # Mirror to questions.js
    fc = data.get("flashcards", [])
    out  = f"// PSY0 Training Data - V6 - Auto-generated\n"
    out += f"// {len(qcm)} questions + {len(fc)} flashcards\n\n"
    out += f"const qcmData = {json.dumps(qcm, ensure_ascii=False, indent=2)};\n\n"
    out += f"const flashcardData = {json.dumps(fc, ensure_ascii=False, indent=2)};\n"
    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"💾 questions.js   mis à jour\n")

    # Quality check — show 10 samples across different types
    print("=== ÉCHANTILLON DE VÉRIFICATION ===")
    shown_types = set()
    for q in csv_qs:
        correct = next(o["text"] for o in q["options"] if o["id"] == q["answer"])
        atype = detect_type(correct)
        if atype in shown_types:
            continue
        shown_types.add(atype)
        print(f"\n[{atype}] {q['question'][:80]}")
        for o in q["options"]:
            mark = "✓" if o["id"] == q["answer"] else " "
            print(f"  [{mark}] {o['text']}")
        if len(shown_types) >= 12:
            break


if __name__ == "__main__":
    main()
