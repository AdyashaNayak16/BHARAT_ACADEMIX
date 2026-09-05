import os
import sys
import uuid
import re
import asyncio

# Ensure parent modules are accessible
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "ai-teacher"))
sys.path.insert(0, os.path.join(BASE_DIR, "video_pipeline"))

from ingest import load_document_text
from retrieval import chunk_text, model, search
import teaching
from teaching import (
    teach,
    make_lesson_plan,
    generate_question,
    evaluate_answer_detailed,
    reexplain_concept,
    ask_teacher_contextual,
    generate_final_quiz,
    teach_topic_no_pdf,
    set_groq_api_key
)
from assessment import generate_structured_report, generate_report
from tts import text_to_audio, generate_speech_sync, clean_for_speech
from slide_generator import create_concept_slide, create_code_slide
from student_profile import update_profile_after_lesson, load_profile

STATIC_AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
STATIC_SLIDES_DIR = os.path.join(BASE_DIR, "static", "slides")
STATIC_VIDEO_DIR = os.path.join(BASE_DIR, "static", "video")

os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)
os.makedirs(STATIC_SLIDES_DIR, exist_ok=True)
os.makedirs(STATIC_VIDEO_DIR, exist_ok=True)

class TeacherEngine:
    def __init__(self):
        self.active_sessions = {}

    def create_lesson(self, topic=None, file_path=None, level="beginner", language="Hinglish", time_available="20 minutes", objective="Concept Mastery"):
        session_id = str(uuid.uuid4())[:8]
        chunks = []
        chunk_embeddings = None
        doc_text = ""

        if file_path and os.path.exists(file_path):
            doc_text = load_document_text(file_path)
            chunks = chunk_text(doc_text)
            try:
                chunk_embeddings = model.encode(chunks)
            except Exception as e:
                print(f"[*] Embedding error: {e}")
            if not topic:
                topic = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
        
        if not topic:
            topic = "General Subject"

        # Determine number of concepts based on available time
        num_concepts = 2 if "5" in time_available else (3 if "15" in time_available or "20" in time_available else 4)

        # Generate Concepts
        concepts = []
        if chunks and chunk_embeddings is not None:
            plan_text = make_lesson_plan(chunks, chunk_embeddings, topic, num_concepts=num_concepts)
            concepts = [line.split('.', 1)[-1].strip() for line in plan_text.split('\n') if line.strip() and not line.startswith('#')]
        
        if not concepts:
            plan_prompt = f"Topic: {topic}. Generate {num_concepts} ordered concept titles for a {level} lesson. Respond only with a numbered list."
            plan_text = teaching.call_llm(plan_prompt)
            concepts = [line.split('.', 1)[-1].strip() for line in plan_text.split('\n') if line.strip() and not line.startswith('#')]
        
        if not concepts:
            concepts = [
                f"1. Core Intuition of {topic}",
                f"2. Practical Mechanics & Rules of {topic}",
                f"3. Real-World Applications & Edge Cases"
            ]

        # Clean concept names
        clean_concepts = []
        for c in concepts[:num_concepts]:
            c_clean = re.sub(r"^\d+[\.\-\)]\s*", "", c).strip()
            if c_clean:
                clean_concepts.append(c_clean)

        # Build each concept's payload (explanation, code/takeaways, question, audio, slide)
        concepts_data = []
        for idx, c in enumerate(clean_concepts, start=1):
            if chunks and chunk_embeddings is not None:
                explanation = teach(chunks, chunk_embeddings, c, level=level, language=language, time_available=time_available)
            else:
                explain_prompt = f"""You are a master teacher. Explain "{c}" (topic: {topic}) to a {level} student.
Goal: {objective}. Available time: {time_available}.
Respond ONLY in {language}. Do not use markdown symbols (no **, no #). Write naturally as spoken sentences."""
                explanation = teaching.call_llm(explain_prompt)

            # Generate Socratic Check Question
            question = generate_question(c, explanation, level=level, language=language)

            # Generate slide key points or code snippet
            code_pattern = re.compile(r"```(?:python|java|cpp|c|javascript)?\n(.*?)```", re.DOTALL)
            code_snippets = code_pattern.findall(explanation)
            
            audio_filename = f"audio_{session_id}_c{idx}.mp3"
            audio_path = os.path.join(STATIC_AUDIO_DIR, audio_filename)
            audio_url = f"/static/audio/{audio_filename}"

            # Generate TTS in background/sync
            generate_speech_sync(explanation, audio_path, language=language)

            # Generate Slide
            slide_filename = f"slide_{session_id}_c{idx}.png"
            slide_path = os.path.join(STATIC_SLIDES_DIR, slide_filename)
            slide_url = f"/static/slides/{slide_filename}"

            if code_snippets:
                create_code_slide(c, code_snippets[0], idx, slide_path)
            else:
                # Extract clean bullet points for slide
                bullet_prompt = f"Based on this explanation: '{explanation}', list 3 very short bullet takeaway points (5-8 words each) in {language}. One per line."
                bullet_text = teaching.call_llm(bullet_prompt)
                bullets = [re.sub(r"^[\d\.\-\*•]+\s*", "", line).strip() for line in bullet_text.split("\n") if line.strip()]
                if not bullets:
                    bullets = ["Foundational principle explained", "Key operational mechanism", "Practical intuition"]
                create_concept_slide(c, explanation, idx, slide_path, key_points=bullets)

            concepts_data.append({
                "index": idx,
                "concept": c,
                "explanation": explanation,
                "speech_text": clean_for_speech(explanation),
                "question": question,
                "audio_url": audio_url,
                "slide_url": slide_url,
                "has_code": bool(code_snippets),
                "code_snippet": code_snippets[0] if code_snippets else ""
            })

        # Generate Final Quiz
        final_quiz = generate_final_quiz(clean_concepts, level=level, language=language)

        session_obj = {
            "session_id": session_id,
            "topic": topic,
            "level": level,
            "language": language,
            "time_available": time_available,
            "objective": objective,
            "doc_text": doc_text[:2000] if doc_text else "",
            "chunks": chunks,
            "chunk_embeddings": chunk_embeddings,
            "concepts": concepts_data,
            "final_quiz": final_quiz,
            "session_log": [],
            "current_concept_idx": 0
        }

        self.active_sessions[session_id] = session_obj

        return {
            "session_id": session_id,
            "topic": topic,
            "level": level,
            "language": language,
            "time_available": time_available,
            "objective": objective,
            "total_concepts": len(concepts_data),
            "concepts": concepts_data,
            "final_quiz": final_quiz
        }

    def evaluate_concept_answer(self, session_id, concept_idx, student_answer):
        session = self.active_sessions.get(session_id)
        if not session:
            # Fallback evaluation if session expired
            eval_res = evaluate_answer_detailed(
                concept="Current Concept",
                question="Concept Question",
                student_answer=student_answer,
                original_explanation="",
                level="beginner",
                language="Hinglish"
            )
            return eval_res

        concept_info = session["concepts"][concept_idx]
        eval_result = evaluate_answer_detailed(
            concept=concept_info["concept"],
            question=concept_info["question"],
            student_answer=student_answer,
            original_explanation=concept_info["explanation"],
            level=session["level"],
            language=session["language"]
        )

        # Generate audio for reexplanation or feedback if provided
        speech_text = eval_result.get("reexplanation") or eval_result.get("feedback", "")
        reexp_audio_url = None
        if speech_text:
            audio_filename = f"audio_{session_id}_eval_c{concept_idx+1}.mp3"
            audio_path = os.path.join(STATIC_AUDIO_DIR, audio_filename)
            generate_speech_sync(speech_text, audio_path, language=session["language"])
            reexp_audio_url = f"/static/audio/{audio_filename}"

        eval_result["feedback_audio_url"] = reexp_audio_url

        # Log session interaction
        session["session_log"].append({
            "concept": concept_info["concept"],
            "question": concept_info["question"],
            "student_answer": student_answer,
            "evaluation": f"Verdict: {eval_result['verdict']}\nFeedback: {eval_result['feedback']}",
            "evaluation_data": eval_result
        })

        return eval_result

    def ask_teacher_doubt(self, session_id, question, current_concept=""):
        session = self.active_sessions.get(session_id, {})
        level = session.get("level", "beginner")
        language = session.get("language", "Hinglish")
        
        # Context from doc or concepts
        context = session.get("doc_text", "")
        if not context and session.get("concepts"):
            context = " ".join([c["explanation"] for c in session["concepts"]])

        answer = ask_teacher_contextual(
            question=question,
            current_concept=current_concept or "Current Lesson",
            lesson_context=context or "General topic principles",
            level=level,
            language=language
        )

        # Generate audio for the teacher's doubt response
        audio_filename = f"doubt_{uuid.uuid4().hex[:6]}.mp3"
        audio_path = os.path.join(STATIC_AUDIO_DIR, audio_filename)
        generate_speech_sync(answer, audio_path, language=language)

        return {
            "question": question,
            "answer": answer,
            "audio_url": f"/static/audio/{audio_filename}"
        }

    def complete_session_and_generate_report(self, session_id, quiz_results=None):
        session = self.active_sessions.get(session_id)
        topic = session.get("topic", "General Topic") if session else "General Topic"
        level = session.get("level", "beginner") if session else "beginner"
        language = session.get("language", "Hinglish") if session else "Hinglish"
        session_log = session.get("session_log", []) if session else []

        structured_report = generate_structured_report(
            session_log=session_log,
            topic=topic,
            level=level,
            language=language,
            quiz_results=quiz_results
        )

        # Update persistent profile
        updated_profile = update_profile_after_lesson(
            topic=topic,
            score=structured_report["score_percent"],
            grade=structured_report["grade"],
            language=language,
            strong_concepts=structured_report["strong_concepts"],
            weak_concepts=structured_report["weak_concepts"],
            next_topics=structured_report["next_recommended_topics"]
        )

        structured_report["updated_profile"] = updated_profile

        return structured_report

    def render_full_video(self, session_id):
        """Invoke moviepy video pipeline to compile full MP4 clip."""
        session = self.active_sessions.get(session_id)
        if not session or not session.get("concepts"):
            return None
        
        try:
            from composer import generate_multi_slide_video
            # Gather slides and audios
            slide_paths = [os.path.join(STATIC_SLIDES_DIR, f"slide_{session_id}_c{i+1}.png") for i in range(len(session["concepts"]))]
            first_audio = os.path.join(STATIC_AUDIO_DIR, f"audio_{session_id}_c1.mp3")
            output_mp4 = os.path.join(STATIC_VIDEO_DIR, f"lesson_{session_id}.mp4")

            # Check if all slides exist
            if all(os.path.exists(p) for p in slide_paths) and os.path.exists(first_audio):
                generate_multi_slide_video(
                    slides_dir=STATIC_SLIDES_DIR,
                    audio_path=first_audio,
                    output_path=output_mp4
                )
                return f"/static/video/lesson_{session_id}.mp4"
        except Exception as e:
            print(f"[*] Video render error: {e}")
        return None

# Global Singleton
engine = TeacherEngine()
