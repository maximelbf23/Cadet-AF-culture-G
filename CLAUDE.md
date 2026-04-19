# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a study toolkit for Air France Cadet (PSY0) exam preparation. It has two main applications:

1. **PSY0 Training** (`PSY0_Training/`) — A Streamlit QCM/flashcard training app covering aeronautical culture, Air France fleet, aviation history, navigation, etc.
2. **Capitales & Drapeaux** (`Capitale/Drapeau/`) — A Streamlit wrapper serving a vanilla HTML/JS geography quiz app.

There are also LaTeX source files (`qcm_psy0.tex`, `supplement_psy0.tex`, `DESTINATIONS_AIR_FRANCE.tex`) for printable revision guides.

## Commands

### Running the apps

```bash
# PSY0 Training app
cd PSY0_Training
streamlit run streamlit_app.py

# Capitales & Drapeaux app
cd Capitale/Drapeau
streamlit run app.py
```

### Installing dependencies

```bash
pip install -r PSY0_Training/requirements.txt
# Dependencies: streamlit>=1.30, plotly>=5.0, pandas>=2.0
```

### Data pipeline

The question data lives in `PSY0_Training/data/questions.js` (JavaScript object with `qcmData` and `flashcardData` arrays) and `PSY0_Training/data/questions.json`.

```bash
# Regenerate questions.js from LaTeX source files (qcm_psy0.tex + supplement_psy0.tex)
python PSY0_Training/generate_data.py

# Extract QCM from a LaTeX .tex file → questions.js
python PSY0_Training/extract_qcm.py

# Convert kd-tools-quizlet.csv → QCM entries with similarity-based distractors, merged into questions.js
python PSY0_Training/convert_csv_to_qcm.py

# Convert kd-tools-quizlet.csv → flashcard entries, merged into questions.js
python PSY0_Training/convert_csv_flashcards.py
```

### Compiling LaTeX

```bash
pdflatex REVISION_PSY0.tex
pdflatex DESTINATIONS_AIR_FRANCE.tex
```

## Architecture

### PSY0 Training app (`PSY0_Training/streamlit_app.py`)

- Reads `data/questions.json` at startup (not `questions.js`)
- Persists session scores and history in `data/user_data.json`
- Three modes: QCM, Flashcards, Analytics (Plotly charts)
- Sidebar category filter; supports timed quizzes and streak tracking
- CSS uses glassmorphism dark theme with animated gradient background

### Data format

`questions.js` (and mirrored in `questions.json`) contains two arrays:
- `qcmData`: `{id, question, options: [{id: "a"|"b"|"c"|"d", text}], answer: "a"|"b"|"c"|"d", explanation, category}`
- `flashcardData`: `{id, front, back, category}`

QCM IDs 1–350 are from the original LaTeX source; IDs 351+ are from the CSV pipeline.

### Distractor generation (`convert_csv_to_qcm.py`)

Wrong answers (distractors) are chosen by:
1. Matching `question_signature()` patterns (e.g., `CODE_IATA`, `CAPITALE`, `NB_MOTEURS`) — questions of the same type share a distractor pool.
2. Falling back to Jaccard similarity on French-tokenized question text, with bonuses for same category or same signature.

### Capitales & Drapeaux (`Capitale/Drapeau/`)

- `app.py` is a thin Streamlit wrapper that reads and injects `index.html` via `st.components.v1.html`
- All quiz logic is in `index.html` (vanilla JS, inline)

### CSV source (`PSY0_Training/kd-tools-quizlet.csv`)

Format: `id, category, question, answer`. Category values map to French labels via `CATEGORY_MAP` in the converter scripts. Both converter scripts share the same CSV path and deduplication logic.
