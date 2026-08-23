import os
import base64
import numpy as np
from io import BytesIO

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from groq import Groq
from PIL import Image
from presentation_rag import PresentationRAG
from sentence_transformers import SentenceTransformer

load_dotenv()

app = FastAPI(title="AI Project Presentation", version="1.0")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

rag = PresentationRAG()

semantic_model = SentenceTransformer("all-MiniLM-L6-v2")


@app.get("/")
def home():

    return {"status": "online", "service": "AI Project Presentation"}


@app.post("/analyze-screen")
async def analyze_screen(file: UploadFile = File(...)):

    # -----------------------------------------
    # Read uploaded image
    # -----------------------------------------

    image_bytes = await file.read()

    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    # -----------------------------------------
    # Convert image → base64
    # -----------------------------------------

    buffer = BytesIO()

    image.save(buffer, format="JPEG", quality=85)

    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # -----------------------------------------
    # Vision prompt
    # -----------------------------------------

    prompt = """
You are analyzing a student's project presentation.

Analyze everything useful that is visible on this
presentation screen.

Extract and organize:

1. TEXT
   Important visible text.

2. CODE
   If code is visible, identify the important code,
   programming language and what it appears to do.

3. TABLES
   Identify the table and important values.

4. CHARTS / GRAPHS
   Identify chart type, labels, values and important trends.

5. DIAGRAMS / ARCHITECTURE
   Explain components and relationships.

6. IMAGES
   Describe images that are relevant to the project.

7. TECHNOLOGIES
   Identify frameworks, libraries, models, databases,
   APIs and tools.

8. OVERALL UNDERSTANDING
   Explain what this screen is communicating.

Rules:
- Only use information visible on the screen.
- Do not invent details.
- If something is unclear, say "unclear".
- Focus on information useful for a technical interview.
"""

    # -----------------------------------------
    # Groq Vision
    # -----------------------------------------

    response = groq_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        temperature=0.1,
    )

    analysis = response.choices[0].message.content or ""

    # Remove Qwen's internal reasoning
    if "</think>" in analysis:
        analysis = analysis.split("</think>", 1)[1]

    analysis = analysis.strip()
    rag.add_document(text=analysis, source_type="screen")

    return {"success": True, "analysis": analysis}


# ==========================================
# SPEECH TO TEXT
# ==========================================


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):

    # Whisper is known to hallucinate stock captioning phrases when fed
    # short or near-silent audio (e.g. pauses between sentences). The
    # client already skips tiny audio blobs before sending, but this is
    # a second safety net: drop the transcript if it's just one of these
    # well-known boilerplate hallucinations and nothing else.
    HALLUCINATED_PHRASES = {
        "thank you.",
        "thank you",
        "thanks for watching",
        "thanks for watching!",
        "i'm going to go to the next one.",
        "i'm going to go to the next one",
        "i'm going to go to the next slide.",
        "i'm going to go to the next slide",
        "i'm going to go to the next video.",
        "i'm going to go to the next video",
        "i'm going to go ahead and get some more.",
        "i'm going to go ahead and get some more",
        "i'm going to go ahead and get started.",
        "okay.",
        "yes.",
        ".",
        "...",
    }

    try:
        audio_bytes = await file.read()

        transcription = groq_client.audio.transcriptions.create(
            file=("speech.webm", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="json",
            language="en",
            temperature=0.0,
        )

        text = transcription.text.strip()

        # Discard known hallucination boilerplate (case-insensitive,
        # ignoring surrounding punctuation/whitespace).
        if text.lower().strip() in HALLUCINATED_PHRASES:
            print("DROPPED (likely hallucination):", text)
            return {"success": True, "text": ""}

        if text:
            rag.add_document(text=text, source_type="speech")

        print("TRANSCRIPT:", text)

        return {"success": True, "text": text}

    except Exception as e:
        print("STT ERROR:", e)

        return {"success": False, "text": "", "error": str(e)}


@app.post("/build-knowledge")
async def build_knowledge():

    rag.build()

    return {"success": True, "documents": len(rag.documents)}


@app.post("/reset-presentation")
async def reset_presentation():

    rag.clear()

    return {"success": True, "message": "Previous presentation data cleared"}


@app.post("/generate-question")
async def generate_question():

    retrieved = rag.retrieve(
        query=(
            "important technical decisions, "
            "implementation, architecture, "
            "methods, technologies, results "
            "and challenges"
        ),
        top_k=6,
    )

    context = "\n\n".join(item["text"] for item in retrieved)

    prompt = f"""
You are an adaptive technical interviewer.

The student has presented a project.

Use the following retrieved evidence:

{context}

Ask ONE technical question based only
on what the student actually presented.

The project can be from ANY domain.

Do not assume any particular technology.

Return only the question.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    question = response.choices[0].message.content or ""

    if "</think>" in question:
        question = question.split("</think>", 1)[1]

    return {"success": True, "question": question.strip()}


# =========================================================
# TEXT TO SPEECH
# =========================================================


@app.post("/speak-question")
async def speak_question(data: dict):

    try:
        question = data.get("question", "").strip()

        if not question:
            return {"success": False, "audio": "", "error": "No question provided"}

        # Orpheus supports max 200 characters
        question = question[:200]

        response = groq_client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice="hannah",
            input=question,
            response_format="wav",
        )

        audio_bytes = response.read()

        import base64

        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return {"success": True, "audio": audio_base64}

    except Exception as e:
        print("TTS ERROR:", e)

        return {"success": False, "audio": "", "error": str(e)}


# =========================================================
# SEMANTIC INTERVIEW EVALUATION
# =========================================================


@app.post("/evaluate-interview")
async def evaluate_interview(data: dict):

    try:
        questions = data.get("questions", [])
        answers = data.get("answers", [])

        if len(questions) != 3 or len(answers) != 3:
            return {
                "success": False,
                "error": "Exactly 3 questions and 3 answers are required.",
            }

        # =================================================
        # 1. RETRIEVE PRESENTATION CONTEXT
        # =================================================

        retrieved = rag.retrieve(query=" ".join(questions), top_k=5)

        context = "\n\n".join(item["text"] for item in retrieved)

        if not context:
            context = "No presentation context was retrieved."

        # =================================================
        # 2. BUILD COMPLETE INTERVIEW
        # =================================================

        interview_text = ""

        for i in range(3):
            interview_text += f"""

QUESTION {i + 1}:
{questions[i]}

STUDENT ANSWER {i + 1}:
{answers[i]}

"""

        # =================================================
        # 3. SEMANTIC SCORE FOR COMPLETE INTERVIEW
        # =================================================

        answer_text = " ".join(answers)

        answer_embedding = semantic_model.encode(answer_text, normalize_embeddings=True)

        context_embedding = semantic_model.encode(context, normalize_embeddings=True)

        similarity = float(np.dot(answer_embedding, context_embedding))

        semantic_score = max(0, min(10, ((similarity + 1) / 2) * 10))

        # =================================================
        # 4. FINAL TECHNICAL EVALUATION
        # =================================================

        prompt = f"""
You are a strict but fair senior technical interviewer.

Evaluate the student's COMPLETE 3-question technical interview.

Use ONLY:
1. The presentation evidence
2. The questions asked
3. The student's answers

PRESENTATION EVIDENCE:

{context}

COMPLETE INTERVIEW:

{interview_text}

Evaluate the student's overall performance across all three answers.

Consider:

1. Technical correctness
2. Relevance to the questions
3. Depth of understanding
4. Completeness
5. Ability to explain their own project
6. Consistency across answers

Important rules:

- Evaluate the interview as a WHOLE.
- Do NOT give individual question scores.
- Do NOT give Question 1, Question 2 or Question 3 scores.
- Do NOT invent information.
- Do NOT reward keyword matching alone.
- If an answer is vague, lower the overall score.
- If technically incorrect, lower the overall score.
- Base your evaluation on the provided presentation evidence.
- Give ONE final technical score.

Return EXACTLY this format:

TECHNICAL_SCORE: X

STRENGTHS:
- ...
- ...
- ...

AREAS_FOR_IMPROVEMENT:
- ...
- ...
- ...

FEEDBACK:
...

Each TECHNICAL_SCORE must be between 0 and 10.
"""

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1200,
        )

        evaluation = response.choices[0].message.content or ""

        # =================================================
        # 5. CLEAN MODEL RESPONSE
        # =================================================

        if "</think>" in evaluation:
            evaluation = evaluation.split("</think>", 1)[1]

        evaluation = evaluation.strip()

        # =================================================
        # 6. EXTRACT TECHNICAL SCORE
        # =================================================

        import re

        match = re.search(
            r"TECHNICAL_SCORE:\s*(\d+(?:\.\d+)?)", evaluation, re.IGNORECASE
        )

        if match:
            technical_score = float(match.group(1))

        else:
            technical_score = 0.0

        technical_score = max(0, min(10, technical_score))

        # =================================================
        # 7. FINAL SCORE
        # =================================================

        final_score = round((semantic_score * 0.30 + technical_score * 0.70), 1)

        return {
            "success": True,
            "semantic_similarity": round(similarity, 3),
            "semantic_score": round(semantic_score, 1),
            "technical_score": round(technical_score, 1),
            "final_score": final_score,
            "evaluation": evaluation,
        }

    except Exception as e:
        print("FINAL EVALUATION ERROR:", e)

        return {"success": False, "error": str(e)}
