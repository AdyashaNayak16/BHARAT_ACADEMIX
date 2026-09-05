# Bharat AcademiX (भारत एकेडमिक्स) — 24/7 Adaptive AI Teacher

**Bharat AcademiX** is a unified, interactive AI Teacher platform built for personalized, adaptive education across multiple Indian and global languages. It seamlessly unites RAG document processing, Socratic dialogue, real-time misconception detection, neural voice synthesis (Edge-TTS), dynamic visual slides, and rich diagnostic learning reports.

---

## 🌟 Key Features

1. **Smart Lesson Studio & Document Ingestion**
   - Ingest any topic or upload study material (PDF, DOCX, TXT, Markdown).
   - Personalize by student mastery level (**Beginner**, **Intermediate**, **Advanced**).
   - Multilingual teaching support: **Hinglish, English (Indian Accent), Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada**.
   - Flexible duration (**5m Sprint, 15m Focus, 30m Deep Dive, 45m Masterclass**).
   - Learning objectives: **Concept Mastery, Exam / Competitive Prep, Quick Revision, Doubt Clearing**.

2. **Interactive AI Teacher Classroom**
   - **AI Avatar & Audio Deck**: Synchronized animated avatar with live lip movement, voice equalizer wave visualizer, and multilingual Edge-TTS neural speech playback.
   - **Visual Slide Deck**: Live generated visual cards and syntax-highlighted code blocks with key takeaways.
   - **Real-time Synced Subtitles & Transcript**: Accessible bilingual captions during lessons.

3. **True Adaptive Socratic Loop**
   - `Lesson Concept` → `Teacher Question` → `Student Answer (Text or Voice Speech-to-Text)` → `AI Diagnosis`
   - **Deep Misconception Detection**: Identifies the exact mental model gap (e.g. boundary confusion, reference errors).
   - **Remediation & Alternative Analogies**: Re-explains using fresh intuitive analogies.
   - **Targeted Retry Question**: Checks understanding before advancing.

4. **Contextual "Ask Guru AI" (Doubt Solver)**
   - Instant doubt resolution side drawer grounded in the current lesson and uploaded documents.
   - Responds with spoken voice and concise explanations.

5. **Comprehensive Final Assessment & Learning Report**
   - Post-lesson mastery quiz.
   - Visual score wheel & grade assignment.
   - Breakdown of **Strong Concepts** vs **Concepts Needing Revision**.
   - Chronological **Misconception Diagnosis Log**.
   - Actionable 3-step **Revision Roadmap**.
   - **Personalized Next Topics** with one-click lesson launcher.

6. **Student Progress & Profile Tracking**
   - Tracks XP, learning streaks, average mastery, and history of completed topics.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r ai-teacher/requirements.txt
pip install -r video_pipeline/requirements.txt
pip install flask
```

### 2. (Optional) Set Groq API Key
You can add your key in `.env` or in the in-app Settings modal:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```
*(If no API key is provided, the platform seamlessly uses its built-in pedagogical teacher engine.)*

### 3. Launch the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📁 Project Architecture

```
BHARAT_ACADEMIX/
├── ai-teacher/             # RAG retrieval, Socratic teaching logic, assessment engine
│   ├── ingest.py           # Multi-format document ingestion (PDF, DOCX, TXT)
│   ├── retrieval.py        # Semantic chunking and hybrid similarity search
│   ├── teaching.py         # Multi-model LLM caller, Socratic evaluation & re-explanation
│   ├── assessment.py       # Diagnostic report generator and learning analytics
│   ├── session.py          # Session logging & state representation
│   └── main.py             # CLI entry point
├── video_pipeline/         # Multimedia assets, TTS, and video synthesis
│   ├── tts.py              # Multilingual Edge-TTS neural voice synthesis
│   ├── slide_generator.py  # Concept & code card visual generator (PIL)
│   ├── composer.py         # MoviePy multi-slide video concatenation
│   └── lesson_parser.py    # Lesson payload cleanup & code extraction
├── backend/
│   ├── teacher_engine.py   # Unified controller orchestrating AI + TTS + slides + adaptive loop
│   └── student_profile.py  # Persistent student progress and mastery tracking
├── static/
│   ├── css/style.css       # Modern dark slate glassmorphism design system
│   ├── js/app.js           # Client-side state machine, speech recognition & audio engine
│   ├── slides/             # Generated concept slide images
│   ├── audio/              # Generated Edge-TTS audio files
│   └── video/              # Generated lesson videos
├── templates/
│   └── index.html          # Unified single-page web application
├── app.py                  # Flask web server & REST API
└── README.md
```
