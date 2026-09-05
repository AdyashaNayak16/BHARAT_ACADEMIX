import json
import os
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PROFILE_FILE = os.path.join(DATA_DIR, "student_profile.json")

def load_profile():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Default profile for initial demo state
    default_profile = {
        "student_name": "Aarav Sharma",
        "level": "beginner",
        "preferred_language": "Hinglish",
        "total_xp": 1450,
        "streak_days": 4,
        "lessons_completed": 3,
        "mastery_average": 82,
        "completed_topics": [
            {
                "topic": "Python Functions & Scope",
                "date": "2026-09-03",
                "score": 88,
                "grade": "A",
                "language": "Hinglish"
            },
            {
                "topic": "Newton's Laws of Motion",
                "date": "2026-09-04",
                "score": 76,
                "grade": "B",
                "language": "English"
            }
        ],
        "strong_skills": ["Logical Flow", "Function Definition", "First Law of Motion"],
        "weak_areas": ["Recursion Base Cases", "Friction Vector Calculations", "Variable Scoping in Closures"],
        "recommended_topics": [
            {
                "title": "Recursion & Call Stack in Python",
                "reason": "Directly addresses identified gap in recursive base conditions",
                "difficulty": "beginner",
                "estimated_time": "20 min"
            },
            {
                "title": "Object-Oriented Programming (OOP) Fundamentals",
                "reason": "Next natural milestone after mastering Functions & Scope",
                "difficulty": "intermediate",
                "estimated_time": "25 min"
            },
            {
                "title": "Binary Search & Divide-and-Conquer",
                "reason": "Builds algorithmic intuition on top of recursion",
                "difficulty": "intermediate",
                "estimated_time": "30 min"
            }
        ]
    }
    save_profile(default_profile)
    return default_profile

def save_profile(profile_data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    return profile_data

def update_profile_after_lesson(topic, score, grade, language, strong_concepts, weak_concepts, next_topics):
    profile = load_profile()
    profile["lessons_completed"] = profile.get("lessons_completed", 0) + 1
    profile["total_xp"] = profile.get("total_xp", 0) + int(score * 2.5)
    
    # Update completed topics
    profile.setdefault("completed_topics", []).insert(0, {
        "topic": topic,
        "date": time.strftime("%Y-%m-%d"),
        "score": score,
        "grade": grade,
        "language": language
    })
    
    # Calculate new average mastery
    all_scores = [t["score"] for t in profile["completed_topics"] if "score" in t]
    profile["mastery_average"] = round(sum(all_scores) / max(1, len(all_scores)))

    # Update strong/weak skills
    for sc in strong_concepts:
        c_name = sc.get("concept") if isinstance(sc, dict) else str(sc)
        if c_name and c_name not in profile.setdefault("strong_skills", []):
            profile["strong_skills"].append(c_name)
            # Remove from weak if now mastered
            if c_name in profile.setdefault("weak_areas", []):
                profile["weak_areas"].remove(c_name)

    for wc in weak_concepts:
        c_name = wc.get("concept") if isinstance(wc, dict) else str(wc)
        if c_name and c_name not in profile.setdefault("weak_areas", []):
            profile["weak_areas"].append(c_name)

    if next_topics:
        profile["recommended_topics"] = next_topics

    save_profile(profile)
    return profile
