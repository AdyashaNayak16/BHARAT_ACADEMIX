from ingest import load_pdf_text
from retrieval import chunk_text, model
from session import run_interactive_lesson, save_lesson_json
def process_uploaded_pdf(pdf_path, topic, level="beginner", language="English", time_available="20 minutes"):
    text = load_pdf_text(pdf_path)
    chunks = chunk_text(text)
    chunk_embeddings = model.encode(chunks)
    result = run_interactive_lesson(chunks, chunk_embeddings, topic, level=level, language=language, time_available=time_available)
    save_lesson_json(result)
    return result
def process_topic_only(topic, level="beginner", language="English", time_available="20 minutes"):
    from teaching import teach_topic_no_pdf
    lesson = teach_topic_no_pdf(topic, level=level, language=language, time_available=time_available)
    print(lesson)
    return lesson

if __name__ == "__main__":
    text = load_pdf_text("sample_chapter.pdf")
    chunks = chunk_text(text)
    chunk_embeddings = model.encode(chunks)

    result = run_interactive_lesson(chunks, chunk_embeddings, "the main topic of this chapter", num_concepts=2, level="beginner", language="English", time_available="20 minutes")
    save_lesson_json(result)