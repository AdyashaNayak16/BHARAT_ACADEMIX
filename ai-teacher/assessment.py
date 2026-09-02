from teaching import call_llm

def generate_report(session_log, language="English"):
    summary_input = ""
    for entry in session_log:
        summary_input += f"Concept: {entry['concept']}\nQuestion: {entry['question']}\nStudent Answer: {entry['student_answer']}\nEvaluation: {entry['evaluation']}\n\n"

    prompt = f"""You are a teacher reviewing a student's lesson session. Here is what happened:

{summary_input}

Based on this, generate a short learning report. Respond ONLY in {language}. Do not use markdown formatting.

Include:
- Overall score (as a percentage, based on how many were correct)
- Concepts the student understood well
- Concepts needing improvement
- One specific recommendation for what to study next"""

    return call_llm(prompt)