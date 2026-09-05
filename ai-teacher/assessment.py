from teaching import call_llm
import json
import re

def generate_report(session_log, language="English"):
    summary_input = ""
    for entry in session_log:
        summary_input += f"Concept: {entry.get('concept', '')}\nQuestion: {entry.get('question', '')}\nStudent Answer: {entry.get('student_answer', '')}\nEvaluation: {entry.get('evaluation', '')}\n\n"

    prompt = f"""You are a master teacher reviewing a student's lesson session. Here is what happened:

{summary_input}

Based on this, generate a comprehensive, encouraging learning report. Respond ONLY in {language}. Do not use markdown formatting (no **, no #, no bullet symbols).

Include:
- Overall score (as a percentage, based on how many were correct)
- Concepts the student understood well
- Concepts needing improvement
- One specific recommendation for what to study next"""

    return call_llm(prompt)

def generate_structured_report(session_log, topic="General Topic", level="beginner", language="English", quiz_results=None):
    """
    Produces a detailed structured JSON report containing:
    - Overall score & mastery level
    - Strong concepts list with mastery percentage
    - Weak concepts list with remediation notes
    - Detected misconceptions breakdown
    - Concrete 3-step Revision plan
    - 2-3 Recommended Next Topics based on student performance
    """
    total_items = len(session_log) + (len(quiz_results) if quiz_results else 0)
    correct_count = 0
    strong_concepts = []
    weak_concepts = []
    misconceptions = []

    for item in session_log:
        eval_data = item.get("evaluation_data", {})
        verdict = eval_data.get("verdict") or ("correct" if "correct" in str(item.get("evaluation", "")).lower() and "incorrect" not in str(item.get("evaluation", "")).lower() else "incorrect")
        concept = item.get("concept", "Core Concept")
        
        if verdict == "correct":
            correct_count += 1
            strong_concepts.append({
                "concept": concept,
                "mastery": 95,
                "note": "Demonstrated solid intuition and accurate reasoning."
            })
        elif verdict == "partial":
            correct_count += 0.5
            weak_concepts.append({
                "concept": concept,
                "mastery": 60,
                "note": "Understood the intuition but missed key operational conditions."
            })
            if eval_data.get("misconception_name") and eval_data.get("misconception_name") != "None":
                misconceptions.append({
                    "concept": concept,
                    "title": eval_data["misconception_name"],
                    "description": eval_data.get("misconception_description", "Partial grasp of mechanics."),
                    "fix": eval_data.get("feedback", "Review boundary checks and core steps.")
                })
        else:
            weak_concepts.append({
                "concept": concept,
                "mastery": 35,
                "note": "Needs targeted revision and practice with simpler analogies."
            })
            if eval_data.get("misconception_name") and eval_data.get("misconception_name") != "None":
                misconceptions.append({
                    "concept": concept,
                    "title": eval_data["misconception_name"],
                    "description": eval_data.get("misconception_description", "Struggled with foundational premise."),
                    "fix": eval_data.get("feedback", "Step back and reinforce the core rule.")
                })

    if quiz_results:
        for q in quiz_results:
            if q.get("is_correct"):
                correct_count += 1
            else:
                c_name = q.get("concept", "Quiz Concept")
                if not any(w["concept"] == c_name for w in weak_concepts):
                    weak_concepts.append({
                        "concept": c_name,
                        "mastery": 45,
                        "note": "Missed during final assessment check."
                    })

    calc_score = round((correct_count / max(1, total_items)) * 100) if total_items > 0 else 85
    calc_score = max(20, min(100, calc_score))

    grade = "A+" if calc_score >= 90 else ("A" if calc_score >= 75 else ("B" if calc_score >= 60 else "Needs Practice"))

    # Generate LLM commentary & smart recommendation
    summary_txt = f"Topic: {topic}, Score: {calc_score}%, Level: {level}, Strong: {[s['concept'] for s in strong_concepts]}, Weak: {[w['concept'] for w in weak_concepts]}"
    
    prompt = f"""You are an expert educational advisor. Based on this student session:
{summary_txt}

Generate in strict JSON format:
{{
  "teacher_summary": "2-3 encouraging sentences summarizing performance in {language}",
  "revision_steps": ["Step 1 in {language}", "Step 2 in {language}", "Step 3 in {language}"],
  "next_recommended_topics": [
    {{"title": "Suggested next topic 1", "reason": "Why this builds on current knowledge in {language}", "difficulty": "{level}"}},
    {{"title": "Suggested next topic 2", "reason": "Alternative deep dive in {language}", "difficulty": "intermediate" if "{level}" == "beginner" else "advanced"}}
  ]
}}"""
    raw = call_llm(prompt)
    teacher_summary = ""
    revision_steps = []
    next_recommended_topics = []

    try:
        cleaned = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
        ai_data = json.loads(cleaned)
        teacher_summary = ai_data.get("teacher_summary", "")
        revision_steps = ai_data.get("revision_steps", [])
        next_recommended_topics = ai_data.get("next_recommended_topics", [])
    except Exception:
        pass

    if not teacher_summary:
        if language == "Hindi":
            teacher_summary = f"शानदार प्रयास! आपने {topic} के कई महत्वपूर्ण बिंदुओं को अच्छी तरह समझा। जो बिंदु थोड़े कमजोर रहे, उन पर थोड़ा सा अभ्यास आपको पूरी तरह निपुण बना देगा।"
            revision_steps = [
                f"{topic} के मुख्य नियमों और बेस शर्तों को दोबारा पढ़ें।",
                "कमजोर अवधारणाओं के 2-3 व्यावहारिक उदाहरण हल करें।",
                "अगले संबंधित विषय पर आगे बढ़ें।"
            ]
            next_recommended_topics = [
                {"title": f"Advanced {topic} Patterns", "reason": "आपकी समझ को और मजबूत करने के लिए", "difficulty": "intermediate"},
                {"title": f"Real-World Applications of {topic}", "reason": "व्यावहारिक प्रोजेक्ट्स में उपयोग समझने के लिए", "difficulty": level}
            ]
        elif language == "Hinglish":
            teacher_summary = f"Great effort! Aapne {topic} ke important principles ache se samjhe. Thoda aur practice karne par aap isme master ho jayenge."
            revision_steps = [
                f"{topic} ke core principles aur edge cases ko revise karein.",
                "Weak concepts par 2 practical exercises attempt karein.",
                "Next related topic start karein."
            ]
            next_recommended_topics = [
                {"title": f"Advanced {topic} Concepts", "reason": "Build deeper problem-solving mastery", "difficulty": "intermediate"},
                {"title": f"Practical Projects on {topic}", "reason": "Apply this directly into real code/work", "difficulty": level}
            ]
        else:
            teacher_summary = f"Great job on completing the lesson on {topic}! You demonstrated solid grasp of the foundations. With a quick review of the tricky edge cases, you'll achieve full mastery."
            revision_steps = [
                f"Review the key rules and boundary conditions of {topic}.",
                "Practice 2-3 applied scenarios focusing on identified gaps.",
                "Proceed to the next complementary topic."
            ]
            next_recommended_topics = [
                {"title": f"Advanced {topic} & Edge Cases", "reason": "Build deeper problem-solving mastery", "difficulty": "intermediate"},
                {"title": f"Practical Architecture & Applications of {topic}", "reason": "See how industry applies this in real-world systems", "difficulty": level}
            ]

    # Fill default strong/weak if empty
    if not strong_concepts:
        strong_concepts.append({"concept": f"Foundational {topic}", "mastery": 80, "note": "Grasped primary intuition."})
    if not weak_concepts and calc_score < 100:
        weak_concepts.append({"concept": f"Complex Edge Cases in {topic}", "mastery": 65, "note": "Review boundary conditions."})

    return {
        "topic": topic,
        "level": level,
        "language": language,
        "score_percent": calc_score,
        "grade": grade,
        "teacher_summary": teacher_summary,
        "strong_concepts": strong_concepts,
        "weak_concepts": weak_concepts,
        "misconceptions": misconceptions,
        "revision_steps": revision_steps,
        "next_recommended_topics": next_recommended_topics
    }