import re
import json

def parse_tex(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Parse answers grid
    # Format: 1 & c & 21 & c & 41 & c & 61 & c & 81 & c \\
    answers = {}
    grid_matches = re.finditer(r'(\d+)\s*&\s*([abcd])', content)
    for match in grid_matches:
        q_num = int(match.group(1))
        ans_letter = match.group(2)
        answers[q_num] = ans_letter

    # 2. Parse questions
    # Format: \item Question ? \\ a) ... \quad b) ... \quad c) ... \quad d) ...
    questions = []
    
    # Split content by \item
    items = re.split(r'\\item\s+', content)
    
    q_counter = 1
    for item in items[1:]: # Skip the first part before the first \item
        
        # Check if it's a question item (contains answers a) b) c) d))
        if '\\\\ a)' in item or '\\\\a)' in item or '\n a)' in item:
            
            # Extract question text (everything before \\ a) )
            q_match = re.search(r'^(.*?)(?:\\\\|\n)\s*a\)', item, re.DOTALL)
            
            if q_match:
                question_text = q_match.group(1).strip()
                # Clean up latex commands
                question_text = question_text.replace('\\textbf{', '').replace('}', '').replace('\\quad', '').strip()
                
                # Extract options
                options = {}
                for letter in ['a', 'b', 'c', 'd']:
                    # Look for content between this letter and the next (or end of line)
                    if letter == 'd':
                        opt_match = re.search(fr'{letter}\)\s*(.*?)(?:\n|$)', item)
                    else:
                        next_letter = chr(ord(letter) + 1)
                        opt_match = re.search(fr'{letter}\)\s*(.*?)(?:\s*\\quad\s*{next_letter}\)|\s*{next_letter}\))', item)
                    
                    if opt_match:
                        opt_text = opt_match.group(1).strip()
                        opt_text = opt_text.replace('\\quad', '').strip()
                        options[letter] = opt_text
                
                # Build question object
                if len(options) == 4 and q_counter in answers:
                    q_obj = {
                        "id": q_counter,
                        "question": question_text,
                        "options": [
                            {"id": "a", "text": options["a"]},
                            {"id": "b", "text": options["b"]},
                            {"id": "c", "text": options["c"]},
                            {"id": "d", "text": options["d"]}
                        ],
                        "answer": answers[q_counter],
                        "explanation": "" # Can be filled manually later
                    }
                    questions.append(q_obj)
                    q_counter += 1
                else:
                    print(f"Error parsing question {q_counter}")
                    print(f"Options found: {options}")

    return questions

if __name__ == "__main__":
    tex_file = "/Users/maximeleboeuf/Cadet AF/qcm_psy0.tex"
    out_file = "/Users/maximeleboeuf/Cadet AF/PSY0_Training/data/questions.js"
    
    questions = parse_tex(tex_file)
    print(f"Successfully extracted {len(questions)} questions.")
    
    # Write to JS file
    js_content = "const qcmData = " + json.dumps(questions, indent=2, ensure_ascii=False) + ";\n"
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Saved to {out_file}")
