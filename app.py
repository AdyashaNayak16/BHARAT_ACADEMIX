import os
import sys
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Add paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "ai-teacher"))
sys.path.insert(0, os.path.join(BASE_DIR, "video_pipeline"))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from teacher_engine import engine
from student_profile import load_profile
import teaching

load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "Bharat AcademiX AI Teacher",
        "version": "2.0.0"
    })

@app.route("/api/profile", methods=["GET"])
def get_profile():
    profile = load_profile()
    return jsonify(profile)

@app.route("/api/settings/key", methods=["POST"])
def update_key():
    data = request.get_json() or {}
    key = data.get("api_key", "").strip()
    if key:
        teaching.set_groq_api_key(key)
        return jsonify({"status": "success", "message": "Groq API key updated successfully."})
    return jsonify({"status": "error", "message": "No key provided."}), 400

@app.route("/api/lesson/create", methods=["POST"])
def create_lesson():
    try:
        topic = request.form.get("topic", "").strip()
        level = request.form.get("level", "beginner").strip()
        language = request.form.get("language", "Hinglish").strip()
        time_available = request.form.get("time_available", "20 minutes").strip()
        objective = request.form.get("objective", "Concept Mastery").strip()

        file_path = None
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(saved_path)
                file_path = saved_path

        if not topic and not file_path:
            topic = "Recursion in Python"

        lesson_data = engine.create_lesson(
            topic=topic,
            file_path=file_path,
            level=level,
            language=language,
            time_available=time_available,
            objective=objective
        )

        return jsonify(lesson_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/lesson/evaluate", methods=["POST"])
def evaluate_answer():
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")
        concept_idx = int(data.get("concept_idx", 0))
        student_answer = data.get("student_answer", "").strip()

        if not student_answer:
            return jsonify({"error": "Student answer is required"}), 400

        result = engine.evaluate_concept_answer(session_id, concept_idx, student_answer)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/lesson/ask", methods=["POST"])
def ask_doubt():
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")
        question = data.get("question", "").strip()
        current_concept = data.get("current_concept", "")

        if not question:
            return jsonify({"error": "Question is required"}), 400

        response = engine.ask_teacher_doubt(session_id, question, current_concept)
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/lesson/complete", methods=["POST"])
def complete_lesson():
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")
        quiz_results = data.get("quiz_results", [])

        report = engine.complete_session_and_generate_report(session_id, quiz_results)
        return jsonify(report)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/video/render", methods=["POST"])
def render_video():
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")
        video_url = engine.render_full_video(session_id)
        if video_url:
            return jsonify({"video_url": video_url})
        return jsonify({"error": "Could not render video. Ensure lesson assets are ready."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("==================================================")
    print(" [>] BHARAT ACADEMIX - AI TEACHER APPLICATION")
    print(" Running on: http://localhost:5000")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
