# 🤖  AI Project Presentation & Technical Interviewer

> An AI-powered presentation assessment and technical interview system that understands a student's project presentation, builds a searchable knowledge base from screen content and speech, generates context-aware technical questions, captures spoken answers, and produces one final interview evaluation.

---

## 📌 Overview

**AI Project Presentation** is an AI-based technical interview platform built around a simple idea:

> **Understand the student's project first, then interview them about what they actually presented.**

During a presentation, the system captures two forms of evidence:

- 🖥️ **Presentation screen content**
- 🎤 **Student speech**

The screen is analyzed using a vision-capable **Qwen LLM**, while speech is converted to text using **Whisper**. Both sources are stored as presentation knowledge and converted into embeddings using **all-MiniLM-L6-v2**. FAISS is then used for semantic retrieval.

After the presentation, the system:

1. Builds the presentation knowledge base.
2. Generates a technical Question 1.
3. Collects the student's answer.
4. Generates Question 2.
5. Collects the student's answer.
6. Generates Question 3.
7. Collects the student's answer.
8. Evaluates the **complete three-question interview once**.
9. Displays the final score and feedback.

The system intentionally does **not** provide individual Q1/Q2/Q3 scores. Evaluation is performed at the end using the complete interview.

---

# 🎯 Objectives

AI project presentation is designed to:

- Understand the student's actual project before interviewing.
- Extract useful technical information from presentation slides.
- Capture the student's verbal explanation.
- Combine screen and speech evidence into a searchable RAG knowledge base.
- Generate project-specific technical questions.
- Support voice-based answers.
- Evaluate technical understanding across the complete interview.
- Provide a final score and actionable feedback.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │       STUDENT        │
                         │   Project Presentation│
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │   Screen Share   │                │    Microphone    │
        │ getDisplayMedia  │                │ getUserMedia     │
        └────────┬─────────┘                └────────┬─────────┘
                 │                                   │
                 ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │ Screenshot Frame │                │   Audio Chunk    │
        └────────┬─────────┘                └────────┬─────────┘
                 │                                   │
                 ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │ Qwen Vision LLM  │                │ Whisper STT      │
        │ qwen/qwen3.6-27b │                │ whisper-large-   │
        │                  │                │ v3-turbo         │
        └────────┬─────────┘                └────────┬─────────┘
                 │                                   │
                 └────────────────┬──────────────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │ Presentation Knowledge  │
                     │                         │
                     │ Screen + Speech         │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │ Sentence Embeddings     │
                     │  all-MiniLM-L6-v2       │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │          FAISS          │
                     │    Vector Retrieval     │
                     └────────────┬────────────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                     ▼                         ▼
            ┌──────────────────┐      ┌────────────────────┐
            │ Question         │      │ Final Evaluation   │
            │ Generation       │      │                    │
            │ GPT-OSS-20B      │      │ GPT-OSS-20B        │
            └────────┬─────────┘      └─────────┬──────────┘
                     │                          │
                     ▼                          │
             ┌───────────────┐                  │
             │ Q1 → Q2 → Q3  │                  │
             └───────┬───────┘                  │
                     │                          │
                     ▼                          │
             ┌───────────────┐                  │
             │ Student Voice │──────────────────┘
             │ Answers       │
             └───────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │    FINAL EVALUATION     │
                     │                         │
                     │ Semantic Score          │
                     │ Technical Score         │
                     │ Final Score             │
                     │ Strengths                │
                     │ Improvements             │
                     │ Feedback                 │
                     └─────────────────────────┘
```

---

# 🔄 End-to-End Workflow

```text
    START
    │
    ▼
    Start Presentation
    │
    ▼
    Reset Previous Session
    │
    ▼
    Share Presentation Screen
    │
    ├───────────────► Capture Screen Frames
    │
    └───────────────► Capture Speech
                            │
                            ▼
                    Whisper Transcription
                            │
                            ▼
                    Add Speech to RAG
    │
    ▼
    I'm Done Presenting
    │
    ▼
    Analyze Final Presentation Screen
    │
    ▼
    Add Screen Analysis to RAG
    │
    ▼
    Build FAISS Knowledge Base
    │
    ▼
    Generate Question 1
    │
    ▼
    Student Answers Q1
    │
    ▼
    Generate Question 2
    │
    ▼
    Student Answers Q2
    │
    ▼
    Generate Question 3
    │
    ▼
    Student Answers Q3
    │
    ▼
    Evaluate All 3 Answers Together
    │
    ▼
    Final Score + Feedback
    │
    ▼
    COMPLETED


---

# 🧩 Application Architecture

The application is divided into two major layers:

```text
┌─────────────────────────────────────────┐
│             Streamlit UI                │
│                                         │
│ Presentation + Interview + Results      │
└───────────────────┬─────────────────────┘
                    │ HTTP
                    ▼
┌─────────────────────────────────────────┐
│             FastAPI Backend             │
│                                         │
│ Vision / STT / RAG / LLM / TTS / Eval   │
└─────────────────────────────────────────┘
```

---

# 🖥️ Frontend — Streamlit

### Main file

```text
app.py
```

The Streamlit application controls the complete user experience.

### Responsibilities

- Presentation UI
- Start/stop presentation workflow
- Screen-share component
- Microphone component
- Live transcript
- Presentation analysis display
- Interview question display
- Question audio playback
- Voice answer capture
- Interview progression
- Final evaluation display
- Session-state management

---

# 🔀 Streamlit Application Stages

The UI is controlled through four stages:

```text
ready
  ↓
presenting
  ↓
interviewing
  ↓
completed
```

## Stage 1 — `ready`

The student sees the welcome screen and starts the presentation.

The application resets previous presentation/interview state before starting a new session.

---

## Stage 2 — `presenting`

The student:

1. Shares their screen.
2. Presents the project.
3. Explains the project verbally.

The application captures:

```text
Screen → Presentation evidence
Speech → Transcript evidence
```

---

## Stage 3 — `interviewing`

After clicking:

```text
✅ I'm Done Presenting — Start Interview
```

the presentation capture UI is stopped and the interview begins.

The system prepares the interview knowledge and generates Question 1.

The question is displayed as text.

If TTS succeeds, the UI also provides:

```text
🔊 Play Question
```

If TTS fails, the text question remains available.

---

## Stage 4 — `completed`

After the student completes all three questions, the final evaluation is displayed.

The final screen contains:

- Semantic relevance
- Technical evaluation
- Final score
- Strengths
- Areas for improvement
- Final feedback

---

# 🖥️ Screen Capture

### File

```text
screen_share.py
```

Screen sharing is implemented using a Streamlit custom component with browser JavaScript.

The browser uses:

```javascript
navigator.mediaDevices.getDisplayMedia()
```

to request screen-sharing permission.

### Screen pipeline

```text
Presentation Screen
       ↓
Browser getDisplayMedia()
       ↓
Video Stream
       ↓
Canvas
       ↓
JPEG Frame
       ↓
Streamlit
       ↓
FastAPI /analyze-screen
```

### Frame capture

The component periodically captures presentation frames.

The captured frame is resized and encoded as JPEG before being sent to the Streamlit application.

### Duplicate screen detection

The application uses perceptual hashing to avoid treating the same slide as a new screen.

```text
Frame
  ↓
Perceptual Hash
  ↓
Compare with previous hashes
  ↓
Duplicate?
 ┌───────┴───────┐
Yes              No
 │                │
Skip              Store
```

This reduces unnecessary processing of identical presentation screens.

---

# 🎤 Speech Capture

### File

```text
speech.py
```

The browser requests microphone access using:

```javascript
navigator.mediaDevices.getUserMedia({
    audio: true
})
```

Audio is recorded using:

```text
MediaRecorder
```

and transmitted as WebM audio.

### Speech pipeline

```text
Student Voice
      ↓
Browser Microphone
      ↓
MediaRecorder
      ↓
WebM Audio
      ↓
FastAPI /transcribe
      ↓
Whisper
      ↓
Transcript
      ↓
Presentation RAG
```

---

# 🗣️ Speech-to-Text

### Model

```text
whisper-large-v3-turbo
```

The backend sends recorded speech to Groq's transcription API.

Non-empty transcripts are added to the RAG knowledge base as:

```text
source_type = "speech"
```

The frontend also uses audio hashing and transcript comparison to reduce duplicate processing.

---

# 👁️ Presentation Vision Analysis

### Endpoint

```text
POST /analyze-screen
```

The final presentation screenshot is sent to the FastAPI backend.

The backend:

1. Reads the image.
2. Converts it to RGB.
3. Converts it to JPEG.
4. Encodes it as Base64.
5. Sends the image + vision prompt to the Qwen LLM.
6. Stores the resulting analysis in the RAG system.

### Vision model

```text
qwen/qwen3.6-27b
```

### What the vision model extracts

The prompt asks the model to identify:

1. Important text
2. Code
3. Tables
4. Charts / graphs
5. Diagrams / architecture
6. Images
7. Technologies
8. Overall understanding

The model is instructed:

- Use only information visible on the screen.
- Do not invent details.
- Mark unclear information as unclear.
- Focus on information useful for a technical interview.

### Vision pipeline

```text
Final Screenshot
      ↓
JPEG
      ↓
Base64
      ↓
Qwen Vision LLM
      ↓
Structured Screen Analysis
      ↓
Presentation RAG
```

---

# 🧠 Presentation RAG

### File

```text
presentation_rag.py
```

The RAG system combines information from:

```text
Screen Analysis
      +
Speech Transcripts
```

Each document stores:

```python
{
    "text": "...",
    "source_type": "screen" | "speech",
    "source_id": None,
    "timestamp": "..."
}
```

---

# 🔢 Embedding Model

The RAG system uses:

```text
all-MiniLM-L6-v2
```

Documents are converted into normalized embeddings:

```python
model.encode(
    texts,
    normalize_embeddings=True
)
```

Normalization allows cosine similarity to be efficiently represented using inner product in FAISS.

---

# 🔎 FAISS Vector Retrieval

The vector database uses:

```text
FAISS
```

with:

```python
faiss.IndexFlatIP()
```

### Retrieval flow

```text
Query
  ↓
all-MiniLM-L6-v2 embeddings
  ↓
Normalized Vector
  ↓
FAISS Inner Product Search
  ↓
Top-K Documents
  ↓
Relevant Presentation Context
```

The RAG layer supports configurable `top_k` retrieval.

---

# 💾 Vector Database Persistence

The vector database is stored in:

```text
presentation_vector_db/
```

with:

```text
index.faiss
documents.json
```

### `index.faiss`

Stores the FAISS vector index.

### `documents.json`

Stores the original documents and metadata.

---

# 🤖 Technical Question Generation

### Endpoint

```text
POST /generate-question
```

The system first retrieves relevant presentation evidence.

The retrieval query focuses on:

```text
technical decisions
implementation
architecture
methods
technologies
results
challenges
```

The retrieved context is passed to the LLM.

### Model

```text
openai/gpt-oss-20b
```

### Question-generation behavior

The LLM is instructed to:

- Ask one technical question.
- Use only the student's presented evidence.
- Support projects from any domain.
- Avoid assuming technologies that were not presented.
- Return only the question.

### Pipeline

```text
Presentation RAG
      ↓
Top-K Relevant Context
      ↓
GPT-OSS-20B
      ↓
Technical Question
```

---

# 🔊 Text-to-Speech

### Endpoint

```text
POST /speak-question
```

### Model

```text
canopylabs/orpheus-v1-english
```

### Voice

```text
hannah
```

### Output

```text
WAV
```

The generated audio is Base64 encoded and returned to Streamlit.

The current implementation limits the question text sent to TTS to approximately 200 characters.

### TTS behavior

```text
Question Generated
       ↓
       TTS
    ┌──┴──┐
 Success  Failure
   │        │
Audio     Text Question
   │        │
Play      Continue
Button    Interview
```

TTS is therefore optional and does not block the interview.

---

# 🎯 Interview Flow

AI project presentation conducts exactly **3 technical questions**.

## Q1

Generated after the presentation knowledge is prepared.

```text
Presentation Evidence
       ↓
FAISS Retrieval
       ↓
GPT-OSS-20B
       ↓
Question 1
```

The student answers using voice.

---

## Q2

After Q1 is answered:

```text
Q1 Answer
   ↓
Generate Q2
```

---

## Q3

After Q2 is answered:

```text
Q2 Answer
   ↓
Generate Q3
```

---

## Final Evaluation

After Q3 is answered:

```text
Q1 + Answer 1
Q2 + Answer 2
Q3 + Answer 3
       ↓
Complete Interview Evaluation
```

There are **no individual question scores**.

---

# 📊 Final Evaluation Architecture

The final evaluation contains two independent components:

```text
                    Complete Interview
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     Semantic Evaluation        Technical Evaluation
              │                         │
              ▼                         ▼
     all-MiniLM-L6-v2           GPT-OSS-20B
              │                         │
              └────────────┬────────────┘
                           ▼
                      Final Score
```

---

# 🧠 Semantic Evaluation

### Model

```text
all-MiniLM-L6-v2
```

This model is used specifically for the final semantic evaluation.

The three student answers are combined:

```text
Answer 1 + Answer 2 + Answer 3
```

The retrieved presentation context is also embedded.

Cosine similarity is calculated between:

```text
Complete Student Answers
          vs
Retrieved Presentation Context
```

The similarity is mapped to a 0–10 semantic score:

```python
semantic_score = ((similarity + 1) / 2) * 10
```

The value is clipped to the 0–10 range.

---

# 🧑‍💻 Technical Evaluation

The complete interview is evaluated by:

```text
openai/gpt-oss-20b
```

The evaluator considers:

1. Technical correctness
2. Relevance to the questions
3. Depth of understanding
4. Completeness
5. Ability to explain the student's own project
6. Consistency across all three answers

The evaluator is explicitly instructed to:

- Evaluate the interview as a whole.
- Not provide individual question scores.
- Not reward keyword matching alone.
- Not invent information.
- Penalize vague or technically incorrect answers.
- Provide one final technical score.

---

# 🏆 Final Score

The final score combines semantic and technical evaluation:

```text
30% Semantic Score
+
70% Technical Score
```

Formula:

```python
final_score = (
    semantic_score * 0.30
    + technical_score * 0.70
)
```

The result is rounded to one decimal place.

---

# 📋 Final Evaluation Output

The completed screen presents:

```text
┌─────────────────────────────────────┐
│          FINAL EVALUATION            │
├─────────────────────────────────────┤
│ Semantic Relevance                  │
│             X.X / 10                │
│                                     │
│ Technical Evaluation                │
│             X.X / 10                │
│                                     │
│ Final Score                         │
│             X.X / 10                │
├─────────────────────────────────────┤
│ Strengths                           │
│ • ...                               │
│ • ...                               │
│                                     │
│ Areas for Improvement               │
│ • ...                               │
│ • ...                               │
│                                     │
│ Final Feedback                      │
│ ...                                 │
└─────────────────────────────────────┘
```

---

# 🧰 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI Provider | Groq |
| Vision LLM | `qwen/qwen3.6-27b` |
| Question Generation | `openai/gpt-oss-20b` |
| Final Technical Evaluation | `openai/gpt-oss-20b` |
| Speech-to-Text | `whisper-large-v3-turbo` |
| Text-to-Speech | `canopylabs/orpheus-v1-english` |
| TTS Voice | `hannah` |
| RAG Embeddings | `all-MiniLM-L6-v2` |
| Semantic Evaluation | `all-MiniLM-L6-v2` |
| Vector Search | FAISS |
| Image Processing | Pillow |
| Computer Vision Utilities | OpenCV |
| Screen Deduplication | ImageHash |
| Speech Recording | Browser MediaRecorder |
| Screen Capture | Browser getDisplayMedia |
| Microphone Capture | Browser getUserMedia |
| Numerical Processing | NumPy |
| Data Processing | Pandas |
| Environment Variables | python-dotenv |
| API Server | Uvicorn |

---

# 📁 Project Structure

```text
AI_project_presentation/
│
├── app.py
│   └── Streamlit frontend and interview workflow
│
├── main.py
│   └── FastAPI backend and AI endpoints
│
├── presentation_rag.py
│   └── Embeddings, FAISS index and retrieval
│
├── screen_share.py
│   └── Browser screen-sharing component
│
├── speech.py
│   └── Browser microphone/audio component
│
├── requirements.txt
│   └── Python dependencies
│
├── .env
│   └── Groq API key
│
└── presentation_vector_db/
    ├── index.faiss
    └── documents.json
```

---

# 🔌 FastAPI API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Backend health check |
| `POST` | `/analyze-screen` | Analyze presentation screenshot |
| `POST` | `/transcribe` | Convert speech to text |
| `POST` | `/build-knowledge` | Build FAISS knowledge base |
| `POST` | `/reset-presentation` | Clear presentation RAG memory |
| `POST` | `/generate-question` | Generate one technical question |
| `POST` | `/speak-question` | Convert question to speech |
| `POST` | `/evaluate-interview` | Evaluate the complete 3-question interview |

---

# 🔗 API Data Flow

```text
/analyze-screen
      ↓
Qwen Vision
      ↓
Screen Evidence
      ↓
RAG


/transcribe
      ↓
Whisper
      ↓
Speech Evidence
      ↓
RAG


/build-knowledge
      ↓
all-MiniLM-L6-v2 Embeddings
      ↓
FAISS


/generate-question
      ↓
FAISS Retrieval
      ↓
GPT-OSS-20B
      ↓
Question


/speak-question
      ↓
Orpheus TTS
      ↓
WAV Audio


/evaluate-interview
      ↓
FAISS Retrieval
      ↓
all-MiniLM-L6-v2
      +
GPT-OSS-20B
      ↓
Final Score
```

---

# ⚙️ Requirements

## Software

- Python 3.x
- Streamlit
- FastAPI
- Uvicorn
- Groq API access
- Modern browser with microphone support
- Modern browser with screen-sharing support

## Python Dependencies

The project uses the dependencies specified in `requirements.txt`.

Important runtime packages include:

```text
streamlit
fastapi
uvicorn
python-dotenv
requests
numpy
pandas
opencv-python
Pillow
ImageHash
sentence-transformers
faiss-cpu
groq
soundfile
easyocr
```

> **Dependency note:** the supplied source imports `faiss` and `imagehash`, so a fresh environment should have `faiss-cpu` and `ImageHash` installed. The supplied requirements also contain `chromadb`, but the current `PresentationRAG` implementation uses FAISS rather than ChromaDB.

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

The backend loads the environment using:

```python
from dotenv import load_dotenv

load_dotenv()
```

The Groq client is initialized with:

```python
Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
```

### Security

Never commit the `.env` file.

Recommended `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
presentation_vector_db/
```

---

# 🚀 Installation

## 1. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

If FAISS/ImageHash are missing:

```bash
pip install faiss-cpu ImageHash
```

---

# ▶️ Running the Application

ProjectViva requires **two processes**.

## Terminal 1 — FastAPI Backend

```bash
cd D:\AI_project_presentation
.venv\Scripts\activate
uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
  "status": "online",
  "service": "AI Project Presentation"
}
```

---

## Terminal 2 — Streamlit Frontend

```bash
cd D:\AI_project_presentation
.venv\Scripts\activate
streamlit run app.py
```

Open the Streamlit URL shown in the terminal, typically:

```text
http://localhost:8501
```

Both FastAPI and Streamlit must remain running.

---

# 🌐 Browser Permissions

The application requires browser permissions for:

### Screen sharing

Allow:

```text
Screen / Window / Browser Tab
```

### Microphone

Allow:

```text
Microphone
```

Without these permissions, presentation capture and voice answers cannot function correctly.

---

# 🧠 Session State

The Streamlit frontend uses session state to control the interview lifecycle.

Important state variables include:

```text
stage
question
question_audio
question_number
answer_transcript
interview_history
interview_prepared
final_evaluation_started
final_evaluation
latest_screen
screen_analysis
transcript
processed_screen_hashes
unique_screen_count
```

### `stage`

Controls the current UI:

```text
ready
presenting
interviewing
completed
```

### `interview_prepared`

Prevents the initial interview preparation from being unnecessarily repeated.

### `interview_history`

Stores the completed interview Q&A pairs.

Example:

```python
{
    "question": "...",
    "answer": "..."
}
```

### `final_evaluation_started`

Protects the final evaluation from duplicate execution.

---

# 🛡️ Duplicate Processing Protection

## Screen duplicate protection

Perceptual hashing is used to detect repeated screens.

```text
Screenshot
   ↓
Perceptual Hash
   ↓
Compare Previous Hashes
   ↓
Duplicate?
```

## Audio duplicate protection

Audio payloads are hashed before transcription.

```text
Audio Chunk
    ↓
MD5 Hash
    ↓
Compare Previous Audio
    ↓
Already Processed?
```

## Transcript duplicate protection

Normalized transcript text is compared with the previous transcript before appending it.

---

# 🧹 Presentation Reset

When a new presentation starts, previous session information is cleared.

This prevents information from a previous student/presentation from being reused.

The backend also exposes:

```text
POST /reset-presentation
```

which clears the presentation RAG state.

---

# 🛡️ Error Handling

## TTS Failure

TTS is optional.

If audio generation fails:

```text
Question remains visible as text
        ↓
Student can continue
```

---

## STT Failure

The transcription endpoint returns a structured error response instead of crashing the complete application.

---

## Question Generation Failure

If Question 1 or a subsequent question cannot be generated, the application reports the error instead of silently continuing with an empty question.

---

## Final Evaluation Failure

The final evaluation is protected by a state flag so the application does not repeatedly submit the same evaluation request.

---

# 📈 Performance Considerations

The system reduces unnecessary AI processing through:

### Periodic screen capture

Screens are sampled rather than continuously analyzed.

### Perceptual screen deduplication

Identical frames are not treated as new presentation evidence.

### Top-K retrieval

Only relevant documents are retrieved from FAISS.

### Normalized embeddings

Normalized vectors allow efficient cosine-similarity retrieval using FAISS inner product.

### Final-only evaluation

The expensive technical evaluation happens once after all three answers are collected.

---

# 🔒 Security Considerations

This project is primarily designed for local/demo use.

For production deployment, consider adding:

- Authentication
- Authorization
- API authentication
- HTTPS
- Rate limiting
- Secure secret management
- User/session isolation
- Secure file handling
- Request validation
- Monitoring and structured logging

Never expose the Groq API key in source code or GitHub.

---

# ⚠️ Current Limitations

1. AI functionality depends on Groq model availability and API limits.
2. Vision, STT, TTS, question generation and evaluation may be affected by provider rate limits.
3. Screen and microphone capture require browser permissions.
4. The current application is designed around a local Streamlit + FastAPI deployment.
5. There is no authentication system.
6. The RAG store is presentation-session oriented.
7. The interview currently contains exactly three questions.
8. Final evaluation is performed after all three answers are collected.
9. Individual Q1/Q2/Q3 scores are intentionally not generated.
10. TTS is optional; text remains available if audio generation fails.
11. The current RAG implementation uses FAISS even though `chromadb` may appear in the supplied dependency list.
12. `faiss-cpu` and `ImageHash` should be explicitly included in the final production requirements if they are not already present.

---

# 💡 Key Design Decisions

## Why Vision + Speech?

A presentation contains information in both:

```text
Slides / Screen
+
Student Explanation
```

Using both sources gives the interviewer more context about the project.

---

## Why RAG?

The interviewer should ask questions based on the student's actual project rather than unrelated generic questions.

RAG allows the system to retrieve relevant presentation evidence before generating questions or evaluating answers.

---

## Why all-MiniLM-L6-v2 Embeddings?

The embedding model:

```text
all-MiniLM-L6-v2
```

converts presentation evidence into semantic vectors, enabling retrieval based on meaning rather than exact keyword matching.

---

## Why FAISS?

FAISS provides fast vector similarity search and works well with normalized embeddings and inner-product similarity.

---

## Why Qwen for Vision?

The vision stage requires the model to interpret presentation screenshots and identify technical information such as:

- Architecture
- Code
- Technologies
- Tables
- Charts
- Project descriptions

The implementation therefore uses:

```text
qwen/qwen3.6-27b
```

for screen analysis.

---

## Why GPT-OSS-20B?

GPT-OSS-20B is used for the reasoning-heavy interview tasks:

```text
Presentation Context
        ↓
GPT-OSS-20B
        ↓
Technical Questions
```

and:

```text
Complete Interview
        ↓
GPT-OSS-20B
        ↓
Technical Evaluation
```

---

## Why all-MiniLM-L6-v2?

The final evaluation uses:

```text
all-MiniLM-L6-v2
```

for the semantic component.

It provides a separate semantic similarity signal between:

```text
Student's complete answers
          vs
Presentation evidence
```

This semantic score is then combined with the LLM-based technical score.

---

# 🔮 Future Improvements

Potential improvements include:

- Adaptive difficulty based on previous answers
- More flexible interview length
- Stronger history-aware question generation
- Structured JSON model outputs
- Better retry/backoff handling for rate limits
- Streaming model responses
- Authentication
- Persistent user profiles
- Database-backed interview sessions
- Production object storage
- Docker deployment
- Cloud deployment
- Automated tests
- Monitoring and observability
- Interview analytics dashboard
- Configurable AI models
- Evaluation calibration using human-reviewed interviews

---

# 🧪 Example Interview Journey

```text
Student starts AI project presentation
          ↓
Shares project presentation
          ↓
Explains project
          ↓
Screen + Speech captured
          ↓
Student clicks "I'm Done Presenting"
          ↓
Qwen analyzes final screen
          ↓
Speech + Screen become presentation knowledge
          ↓
all-MiniLM-L6-v2 embeddings
          ↓
FAISS retrieval
          ↓
GPT-OSS-20B generates Q1
          ↓
Student answers
          ↓
GPT-OSS-20B generates Q2
          ↓
Student answers
          ↓
GPT-OSS-20B generates Q3
          ↓
Student answers
          ↓
all-MiniLM-L6-v2 semantic evaluation
          +
GPT-OSS-20B technical evaluation
          ↓
30% Semantic + 70% Technical
          ↓
Final Score + Feedback
```

---

# 📌 Quick Reference

### Backend

```bash
uvicorn main:app --reload
```

### Frontend

```bash
streamlit run app.py
```

### Backend URL

```text
http://127.0.0.1:8000
```

### Streamlit URL

```text
http://localhost:8501
```

### Vision

```text
qwen/qwen3.6-27b
```

### Question Generation

```text
openai/gpt-oss-20b
```

### Final Technical Evaluation

```text
openai/gpt-oss-20b
```

### Speech-to-Text

```text
whisper-large-v3-turbo
```

### Text-to-Speech

```text
canopylabs/orpheus-v1-english
```

### RAG Embeddings

```text
all-MiniLM-L6-v2
```

### Semantic Evaluation

```text
all-MiniLM-L6-v2
```

### Vector Database

```text
FAISS IndexFlatIP
```

---

# 👩‍💻 Project Summary

**Project Name:** AI project presentation
**Application Type:** AI-powered project presentation and technical interview system  
**Frontend:** Streamlit  
**Backend:** FastAPI  
**AI Provider:** Groq  
**Architecture:** Vision + Speech + RAG + LLM + TTS + Semantic Evaluation  
**Interview Length:** 3 technical questions  
**Evaluation Strategy:** One final combined evaluation  
**Final Score:** 30% semantic + 70% technical

---

## ⭐ Core Pipeline

```text
SCREEN + SPEECH
       ↓
QWEN VISION + WHISPER
       ↓
PRESENTATION KNOWLEDGE
       ↓
all-MiniLM-L6-v2 EMBEDDINGS
       ↓
FAISS RETRIEVAL
       ↓
GPT-OSS-20B
       ↓
3 TECHNICAL QUESTIONS
       ↓
VOICE ANSWERS
       ↓
WHISPER
       ↓
COMPLETE INTERVIEW
       ↓
all-MiniLM-L6-v2
       +
GPT-OSS-20B
       ↓
30% SEMANTIC + 70% TECHNICAL
       ↓
FINAL SCORE + FEEDBACK
```
