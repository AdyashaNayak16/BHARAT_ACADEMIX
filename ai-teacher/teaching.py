from groq import Groq
from dotenv import load_dotenv
import os
from retrieval import search

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: Could not get a response from the AI. Details: {str(e)}"

def teach(chunks, chunk_embeddings, query, level="beginner", language="English", time_available="20 minutes"):
    context = search(chunks, chunk_embeddings, query, top_k=1)[0]

    prompt = f"""You are a friendly teacher. You must respond ONLY in {language}. Do not use English at all, unless {language} is English. Using ONLY the information below, explain the concept to a {level} student.

Do not use markdown formatting (no **, no #, no tables, no bullet symbols). Write in plain spoken sentences, as if speaking out loud.

The student has {time_available} available for this concept. Adjust your depth and length accordingly:
- very short time (under 5 min): only the single most important idea, 2-3 sentences max
- moderate time (10-20 min): key idea plus one example
- long time (45-60 min): full explanation, multiple examples, deeper detail
- multi-day: treat this as one part of a larger study plan, keep it focused but note what comes next

Context:
{context}

Question: {query}

Explain it like a teacher would."""

    return call_llm(prompt)

def make_lesson_plan(chunks, chunk_embeddings, topic, num_concepts=3):
    top_chunks = search(chunks, chunk_embeddings, topic, top_k=num_concepts)
    combined_context = "\n\n".join(top_chunks)

    prompt = f"""You are a teacher planning a lesson on: {topic}

Using ONLY the context below, identify {num_concepts} key concepts that should be taught, in the order a beginner should learn them.

Context:
{combined_context}

Respond as a numbered list, one concept name per line, nothing else."""

    return call_llm(prompt)

def generate_question(concept, explanation, level="beginner", language="English"):
    prompt = f"""You are a teacher. You just taught this concept to a {level} student:

Concept: {concept}
Explanation: {explanation}

Now ask ONE simple question to check if the student understood. You must respond ONLY in {language}.

Rules:
- beginner: simple conceptual question, no math/jargon
- intermediate: applied question with light reasoning
- advanced: technical question requiring precise reasoning

Respond with ONLY the question, nothing else."""

    return call_llm(prompt)

def evaluate_answer(concept, question, student_answer, level="beginner", language="English"):
    prompt = f"""You are a teacher. You asked a student this question about "{concept}":

Question: {question}
Student's answer: {student_answer}

Evaluate if the answer is correct, partially correct, or incorrect. Respond ONLY in {language}.

Respond in this exact format:
Verdict: [correct/partial/incorrect]
Feedback: [one short sentence explaining why]"""

    return call_llm(prompt)

def reexplain_concept(concept, original_explanation, student_answer, level="beginner", language="English"):
    prompt = f"""You are a teacher. You explained "{concept}" to a {level} student like this:

{original_explanation}

The student then answered a question incorrectly: "{student_answer}"

This suggests a misunderstanding. Explain "{concept}" again, but use a DIFFERENT analogy or approach than before, to help fix the confusion. Respond ONLY in {language}. Do not use markdown formatting.

Keep it short and focused on fixing the likely misunderstanding."""

    return call_llm(prompt)

def teach_lesson(chunks, chunk_embeddings, topic, num_concepts=3, level="beginner", language="English", time_available="20 minutes"):
    plan_text = make_lesson_plan(chunks, chunk_embeddings, topic, num_concepts)
    concepts = [line.split('.', 1)[-1].strip() for line in plan_text.split('\n') if line.strip()]

    full_lesson = []
    for concept in concepts:
        explanation = teach(chunks, chunk_embeddings, concept, level=level, language=language, time_available=time_available)
        question = generate_question(concept, explanation, level=level, language=language)
        full_lesson.append(f"## {concept}\n{explanation}\n\n**Question:** {question}")

    return "\n\n".join(full_lesson)

def teach_lesson_json(chunks, chunk_embeddings, topic, num_concepts=3, level="beginner", language="English", time_available="20 minutes"):
    plan_text = make_lesson_plan(chunks, chunk_embeddings, topic, num_concepts)
    concepts = [line.split('.', 1)[-1].strip() for line in plan_text.split('\n') if line.strip()]

    lesson_data = []
    for concept in concepts:
        explanation = teach(chunks, chunk_embeddings, concept, level=level, language=language, time_available=time_available)
        question = generate_question(concept, explanation, level=level, language=language)
        lesson_data.append({
            "concept": concept,
            "explanation": explanation,
            "question": question,
            "level": level,
            "language": language
        })

    return lesson_data

def teach_topic_no_pdf(topic, num_concepts=3, level="beginner", language="English", time_available="20 minutes"):
    plan_prompt = f"""You are a teacher planning a lesson on: {topic}

List {num_concepts} key concepts a {level} student should learn, in the order they should learn them.

Respond as a numbered list, one concept name per line, nothing else."""

    plan_text = call_llm(plan_prompt)
    concepts = [line.split('.', 1)[-1].strip() for line in plan_text.split('\n') if line.strip()]

    full_lesson = []
    for concept in concepts:
        explain_prompt = f"""You are a friendly teacher. You must respond ONLY in {language}. Do not use English at all, unless {language} is English.

Explain "{concept}" (part of the topic: {topic}) to a {level} student.

The student has {time_available} available. Adjust depth accordingly:
- under 5 min: one key idea, 2-3 sentences
- 10-20 min: key idea plus one example
- 45-60 min: full depth, multiple examples
- multi-day: focused part of a larger plan

Explain it like a teacher would, using your own knowledge since no reference material was provided."""

        explanation = call_llm(explain_prompt)
        full_lesson.append(f"## {concept}\n{explanation}")

    return "\n\n".join(full_lesson)