import json
import re

def clean_lesson(json_path="data/sample.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    code_pattern = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)
    results = []

    for item in data:
        raw_text = item.get("explanation", "")
        code_snippets = code_pattern.findall(raw_text)
        
        
        clean_speech = code_pattern.sub(" As shown on the screen. ", raw_text)
        clean_speech = clean_speech.replace("`", "").replace("‑", "-").strip()

        results.append({
            "concept": item.get("concept"),
            "speech": clean_speech,
            "codes": code_snippets
        })

    return results
def process_live_rag_data(rag_output_data):
    """
    Accepts live JSON/list data directly from the RAG module 
    instead of reading from a local file.
    """
    code_pattern = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)
    results = []

    for item in rag_output_data:
        raw_text = item.get("explanation", "")
        code_snippets = code_pattern.findall(raw_text)
        
        clean_speech = code_pattern.sub(" As shown on the screen. ", raw_text)
        clean_speech = clean_speech.replace("`", "").replace("‑", "-").strip()

        results.append({
            "concept": item.get("concept"),
            "speech": clean_speech,
            "codes": code_snippets
        })

    return results
if __name__ == "__main__":
    lessons = clean_lesson()
    print(f"Loaded {len(lessons)} concepts.")
    print(f"Concept 1: {lessons[0]['concept']}")
    print(f"Code snippets extracted: {len(lessons[0]['codes'])}")