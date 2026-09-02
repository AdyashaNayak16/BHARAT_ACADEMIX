# AI Teacher — RAG & Adaptive Teaching Engine

This is the AI/LLM core for the AI Teacher project. It handles understanding material, planning lessons, teaching interactively, and adapting to the student.

## What it does
- Reads a PDF and teaches from it, OR teaches any topic directly (no PDF needed)
- Builds a structured lesson plan (ordered concepts, not random order)
- Personalizes teaching by level (beginner/intermediate/advanced), language, and time available
- Asks the student questions during the lesson
- Evaluates answers and re-explains concepts differently if the student is wrong
- Generates a final learning report (score, strengths, weak areas, recommendation)
- Outputs everything as JSON for the video and frontend modules to use

## Files
- `ingest.py` — reads PDF files into text
- `retrieval.py` — chunks text and finds relevant pieces for a question (RAG retrieval)
- `teaching.py` — core teaching logic: explaining, questioning, evaluating, re-explaining
- `assessment.py` — generates the final learning report
- `session.py` — runs a full interactive lesson session and saves the output
- `main.py` — entry point that ties everything together

## Setup
1. Install dependencies:pip install -r requirements.txt
2. Create a `.env` file with your Groq API key:GROQ_API_KEY=your_key_here
## Running it
python main.py
This runs a sample interactive lesson using `sample_chapter.pdf`.

## For integration (Person 2 / Person 3)
Use these two entry-point functions in `main.py`:

- `process_uploaded_pdf(pdf_path, topic, level, language, time_available)` — for PDF-based lessons
- `process_topic_only(topic, level, language, time_available)` — for topic-only lessons (no PDF)

Both return structured lesson data (see `sample_output.json` for the exact shape).

## Known limitations
- No knowledge graph yet — retrieval is embedding-based similarity only
- Currently console-based interaction (`input()`) — frontend will need to replace this with real UI input
