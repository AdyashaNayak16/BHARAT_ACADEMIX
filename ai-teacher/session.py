import json
from teaching import teach, make_lesson_plan, generate_question, evaluate_answer, reexplain_concept
from assessment import generate_report

def run_interactive_lesson(chunks, chunk_embeddings, topic, num_concepts=3, level="beginner", language="English", time_available="20 minutes"):
    plan_text = make_lesson_plan(chunks, chunk_embeddings, topic, num_concepts)
    concepts = [line.split('.', 1)[-1].strip() for line in plan_text.split('\n') if line.strip()]

    session_log = []

    for concept in concepts:
        explanation = teach(chunks, chunk_embeddings, concept, level=level, language=language, time_available=time_available)
        print(f"\n--- {concept} ---")
        print(explanation)

        question = generate_question(concept, explanation, level=level, language=language)
        print(f"\nQuestion: {question}")

        student_answer = input("Your answer: ")

        result = evaluate_answer(concept, question, student_answer, level=level, language=language)
        print(f"\n{result}")

        if "incorrect" in result.lower() or "partial" in result.lower():
            new_explanation = reexplain_concept(concept, explanation, student_answer, level=level, language=language)
            print(f"\nLet's try again:\n{new_explanation}")

        session_log.append({
            "concept": concept,
            "explanation": explanation,
            "question": question,
            "student_answer": student_answer,
            "evaluation": result
        })

    report = generate_report(session_log, language=language)
    print(f"\n=== Final Report ===\n{report}")

    return {
        "topic": topic,
        "level": level,
        "language": language,
        "time_available": time_available,
        "session_log": session_log,
        "final_report": report
    }

def save_lesson_json(data, filename="sample_output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved output to {filename}")