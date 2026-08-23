import streamlit as st
from screen_share import screen_share
import base64
import time
from io import BytesIO
from PIL import Image
import imagehash
import requests
import hashlib
from speech import speech_component_ui


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Project Presentation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "stage" not in st.session_state:
    st.session_state.stage = "ready"

if "question_generating" not in st.session_state:
    st.session_state.question_generating = False

if "question" not in st.session_state:
    st.session_state.question = ""

if "question_audio" not in st.session_state:
    st.session_state.question_audio = ""

if "question_number" not in st.session_state:
    st.session_state.question_number = 0

if "answer_transcript" not in st.session_state:
    st.session_state.answer_transcript = ""

if "last_answer_audio_hash" not in st.session_state:
    st.session_state.last_answer_audio_hash = ""

if "final_evaluation_started" not in st.session_state:
    st.session_state.final_evaluation_started = False

if "interview_prepared" not in st.session_state:
    st.session_state.interview_prepared = False

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "interview_history" not in st.session_state:
    st.session_state.interview_history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "retrieved_context" not in st.session_state:
    st.session_state.retrieved_context = ""

if "final_evaluation" not in st.session_state:
    st.session_state.final_evaluation = None

if "score" not in st.session_state:
    st.session_state.score = None

if "processed_screen_hashes" not in st.session_state:
    st.session_state.processed_screen_hashes = []

if "unique_screen_count" not in st.session_state:
    st.session_state.unique_screen_count = 0

if "is_new_screen" not in st.session_state:
    st.session_state.is_new_screen = False

if "screen_analysis" not in st.session_state:
    st.session_state.screen_analysis = ""

if "latest_screen" not in st.session_state:
    st.session_state.latest_screen = None


# ============================================================
# FASTAPI SCREEN ANALYSIS
# ============================================================

FASTAPI_URL = "http://127.0.0.1:8000"


def speak_question(question):

    response = requests.post(
        f"{FASTAPI_URL}/speak-question", json={"question": question}, timeout=60
    )

    response.raise_for_status()

    return response.json()


def reset_presentation():

    response = requests.post(f"{FASTAPI_URL}/reset-presentation", timeout=30)

    response.raise_for_status()

    return response.json()


def build_knowledge():

    response = requests.post(f"{FASTAPI_URL}/build-knowledge", timeout=60)

    response.raise_for_status()

    return response.json()


def generate_question():

    response = requests.post(f"{FASTAPI_URL}/generate-question", timeout=60)

    response.raise_for_status()

    return response.json().get("question", "")


def evaluate_interview(questions, answers):

    response = requests.post(
        f"{FASTAPI_URL}/evaluate-interview",
        json={"questions": questions, "answers": answers},
        timeout=120,
    )

    response.raise_for_status()
    return response.json()


def analyze_screen(image):

    buffer = BytesIO()

    image.save(buffer, format="JPEG", quality=85)

    buffer.seek(0)

    files = {"file": ("screen.jpg", buffer, "image/jpeg")}

    response = requests.post(f"{FASTAPI_URL}/analyze-screen", files=files, timeout=60)

    response.raise_for_status()

    return response.json()["analysis"]


def transcribe_audio(audio_data):

    if not audio_data:
        return ""

    try:
        # Remove data URL prefix
        if "," in audio_data:
            audio_data = audio_data.split(",", 1)[1]

        audio_bytes = base64.b64decode(audio_data)

        response = requests.post(
            "http://127.0.0.1:8000/transcribe",
            files={"file": ("speech.webm", audio_bytes, "audio/webm")},
            timeout=60,
        )

        response.raise_for_status()

        result = response.json()

        return result.get("text", "")

    except Exception as e:
        st.error(f"STT error: {e}")

        return ""


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI PROJECT PRESENTATION")
st.caption("Adaptive AI Technical Interviewer")

st.divider()


# ============================================================
# STAGE 1 — READY
# ============================================================

if st.session_state.stage == "ready":
    st.markdown("## 👋 Welcome")

    st.write(
        "Present your project naturally while ProjectViva observes "
        "your presentation and speech. After your presentation, "
        "the AI will conduct an adaptive technical interview."
    )

    st.markdown("### How it works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🖥️")
        st.markdown("**1. Present**")
        st.caption("Share your screen and explain your project.")

    with col2:
        st.markdown("### 🎤")
        st.markdown("**2. Answer**")
        st.caption("Answer AI questions naturally using your voice.")

    with col3:
        st.markdown("### 📊")
        st.markdown("**3. Get Feedback**")
        st.caption("Receive scores and detailed feedback.")

    st.divider()

    if st.button("🚀 Start Presentation", use_container_width=True, type="primary"):
        try:
            # Clear previous presentation from backend RAG
            reset_presentation()

            # Clear previous UI data
            st.session_state.transcript = ""
            st.session_state.screen_analysis = ""
            st.session_state.processed_screen_hashes = []
            st.session_state.unique_screen_count = 0
            st.session_state.question_number = 0
            st.session_state.interview_history = []
            st.session_state.question = ""
            st.session_state.question_audio = ""
            st.session_state.answer_transcript = ""
            st.session_state.last_answer_audio_hash = ""
            st.session_state.final_evaluation_started = False
            st.session_state.final_evaluation = None
            st.session_state.interview_prepared = False
            st.session_state.interview_started = False
            st.session_state.is_new_screen = False
            st.session_state.latest_screen = None

            if "latest_unique_screen" in st.session_state:
                st.session_state.latest_unique_screen = None

            if "last_audio_hash" in st.session_state:
                st.session_state.last_audio_hash = ""

            if "last_transcript" in st.session_state:
                st.session_state.last_transcript = ""

            st.session_state.stage = "presenting"

            st.rerun()

        except Exception as e:
            st.error(f"Could not start presentation: {e}")


# ============================================================
# STAGE 2 — PRESENTATION
# ============================================================

elif st.session_state.stage == "presenting":
    # Status
    st.success("🟢 PRESENTATION MODE")

    st.info(
        "Share your screen and start presenting your project. "
        "The AI will listen and understand your presentation "
        "but will not interrupt you."
    )

    st.divider()

    # --------------------------------------------------------
    # MAIN PRESENTATION AREA
    # --------------------------------------------------------

    left, right = st.columns([1.6, 1])

    # ========================================================
    # SCREEN AREA
    # ========================================================

    with left:
        st.subheader("🖥️ Your Presentation")

        screen_result = screen_share(key="presentation_screen")
        # ==========================================
        # RECEIVE SCREENSHOT
        # ==========================================

        if screen_result.frame:
            try:
                # ==========================================
                # 1. BASE64 → IMAGE
                # ==========================================

                base64_data = screen_result.frame.split(",", 1)[1]

                image_bytes = base64.b64decode(base64_data)

                captured_image = Image.open(BytesIO(image_bytes)).convert("RGB")

                st.session_state.latest_screen = captured_image

                # ==========================================
                # 2. CREATE PERCEPTUAL HASH
                # ==========================================

                current_hash = imagehash.phash(captured_image)

                # ==========================================
                # 3. COMPARE WITH PREVIOUS SCREEN
                # ==========================================

                is_new_screen = True

                for previous_hash in st.session_state.processed_screen_hashes:
                    difference = current_hash - previous_hash

                    if difference <= 5:
                        is_new_screen = False
                        break

                # ==========================================
                # 4. HANDLE NEW SCREEN
                # ==========================================

                if is_new_screen:
                    st.session_state.unique_screen_count += 1

                    st.session_state.is_new_screen = True

                    st.session_state.latest_unique_screen = captured_image

                    st.session_state.processed_screen_hashes.append(current_hash)

                else:
                    st.session_state.is_new_screen = False

            except Exception as e:
                st.error(f"Could not process captured screen: {e}")

        # =========================================
        # STATUS
        # =========================================

        if st.session_state.is_new_screen:
            st.success("🆕 New screen detected")

        else:
            st.info("🔁 Duplicate screen — skipped")

        st.caption(f"Unique screens detected: {st.session_state.unique_screen_count}")

        # ==========================================
        # DISPLAY CAPTURED SCREEN
        # ==========================================

        if (
            "latest_screen" in st.session_state
            and st.session_state.latest_screen is not None
        ):
            st.image(st.session_state.latest_screen, use_container_width=True)

        else:
            st.info("📺 Share your screen to see the presentation.")

        st.caption(
            "Share PowerPoint, PDF, Word, browser, "
            "VS Code, or any other visible screen."
        )

    # ========================================================
    # PRESENTATION ANALYSIS
    # ========================================================

    with right:
        st.subheader("🧠 Presentation Analysis")

        st.markdown("**Screen Analysis**")

        if st.session_state.screen_analysis:
            st.success("🟢 Screen content analyzed")

        else:
            st.info("Waiting for screen content...")

        st.markdown("**Detected Content**")

        if "screen_analysis" in st.session_state:
            st.text(st.session_state.screen_analysis)

        else:
            st.write("• No content detected yet")

        st.markdown("**🎤 Speech Status**")

        if screen_result and screen_result.sharing:
            speech_result = speech_component_ui(key="presentation_speech")
        else:
            speech_result = None

        st.info("🖥️ Share your screen first. Microphone will start automatically.")

        # ==========================================
        # SPEECH TRANSCRIPTION
        # ==========================================

        if "transcript" not in st.session_state:
            st.session_state.transcript = ""

        if "last_audio_hash" not in st.session_state:
            st.session_state.last_audio_hash = ""

        if "last_transcript" not in st.session_state:
            st.session_state.last_transcript = ""

        if speech_result:
            audio_data = speech_result.get("audio", "")

            if audio_data:
                import hashlib

                audio_hash = hashlib.md5(audio_data.encode()).hexdigest()

                # Process only a new audio chunk
                if audio_hash != st.session_state.last_audio_hash:
                    st.session_state.last_audio_hash = audio_hash

                    transcript = transcribe_audio(audio_data)

                    if transcript:
                        # Normalize text for duplicate detection
                        clean_text = " ".join(transcript.lower().split())

                        last_text = " ".join(
                            st.session_state.last_transcript.lower().split()
                        )

                        # Don't append the same transcription again
                        if clean_text != last_text:
                            if st.session_state.transcript:
                                st.session_state.transcript += " "

                            st.session_state.transcript += transcript

                            st.session_state.last_transcript = transcript

                        st.info("Waiting for speech...")

                    st.divider()

    # ========================================================
    # LIVE TRANSCRIPT
    # ========================================================

    st.subheader("🎤 Live Presentation Transcript")

    if st.session_state.transcript:
        st.text_area(
            "Student Speech",
            value=st.session_state.transcript,
            height=180,
            disabled=True,
        )

    else:
        st.info("🎤 Start speaking to generate transcript...")

    st.divider()

    # ========================================================
    # RAG MEMORY
    # ========================================================

    with st.expander("🧠 Presentation Knowledge Base"):
        st.write(
            "Screen content and speech transcripts "
            "are stored in the backend RAG system."
        )

        st.info("✓ Screen → Vision → Embeddings → FAISS")

        st.info("✓ Speech → Whisper → Embeddings → FAISS")

        st.info("✓ Done Presenting → Retrieval → Interview Question")

    st.divider()

    # ========================================================
    # END PRESENTATION
    # ========================================================

    st.warning("Finished presenting your project?")

    if st.button(
        "✅ I'm Done Presenting — Start Interview",
        use_container_width=True,
        type="primary",
    ):
        try:
            if st.session_state.latest_screen is None:
                st.error("Please share your presentation screen before finishing.")
                st.stop()

            st.session_state.stage = "interviewing"
            st.session_state.interview_started = False
            st.rerun()

        except Exception as e:
            st.error(f"Could not start the interview: {e}")


# ============================================================
# STAGE 3 — INTERVIEW
# ============================================================

elif st.session_state.stage == "interviewing":
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False

    if not st.session_state.interview_started:
        st.success("🟣 INTERVIEW MODE")

        st.info(
            "Your presentation has been captured and the knowledge base "
            "is ready to build. Click below when you're ready to begin "
            "the technical interview."
        )

        if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
            st.session_state.interview_started = True
            st.rerun()

        st.divider()

        left, right = st.columns([1.25, 1])

        with left:
            st.subheader("🖥️ Presentation Context")

            if st.session_state.latest_screen is not None:
                st.image(st.session_state.latest_screen, use_container_width=True)
            else:
                st.info("No presentation screen captured.")

            st.write("")

            with st.expander("🔎 Retrieved Context", expanded=True):
                st.markdown(
                    """
                    **Screen**

                    • Project architecture

                    • Model / technology information

                    **Speech**

                    • Student's explanation
                    """
                )

        with right:
            st.subheader("🤖 AI Interviewer")
            st.info("Ready to generate your first question.")

        st.divider()

        st.subheader("📋 Interview Progress")

        q1, q2, q3 = st.columns(3)

        with q1:
            st.metric("Questions", "0 / 3")

        with q2:
            st.metric("Difficulty", "Adaptive")

        with q3:
            st.metric("Questions Completed", "0 / 3")

        st.stop()

    if not st.session_state.interview_prepared:
        if st.session_state.get("interview_prep_started", False):
            started_at = st.session_state.get("interview_prep_started_at", 0)

            if time.time() - started_at > 10:
                # The previous attempt never finished within a
                # reasonable time — treat it as dead and retry.
                st.session_state.interview_prep_started = False
                st.rerun()

            st.info("🧠 Still preparing your interview, please wait…")

            if st.button("Retry now"):
                st.session_state.interview_prep_started = False
                st.rerun()

            time.sleep(1)
            st.rerun()

        st.session_state.interview_prep_started = True
        st.session_state.interview_prep_started_at = time.time()

        try:
            with st.spinner("🧠 Preparing your interview..."):
                # Analyze final presentation screen ONCE
                analysis = analyze_screen(st.session_state.latest_screen)

                st.session_state.screen_analysis = analysis

                # Build knowledge ONCE
                build_knowledge()

                # Generate Question 1 ONCE
                question = generate_question()

                if not question:
                    st.error("Could not generate Question 1.")
                    st.session_state.interview_prep_started = False
                    st.stop()

                st.session_state.question_number = 1
                st.session_state.question = question
                st.session_state.question_audio = ""

                # TTS is optional
                try:
                    tts_result = speak_question(question)

                    if tts_result.get("success"):
                        st.session_state.question_audio = tts_result.get("audio", "")

                except Exception as e:
                    print("TTS failed:", e)

                st.session_state.interview_prepared = True
            st.rerun()

        except Exception as e:
            st.session_state.interview_prep_started = False
            st.error(f"Interview preparation failed: {e}")
            st.exception(e)
            st.stop()

    # Question 1 is prepared before entering this stage, exactly once.
    if not st.session_state.question:
        st.error("Question 1 is not available. Please restart the presentation.")
        st.stop()

    st.success("🟣 INTERVIEW MODE")

    st.info(
        "Your presentation has been captured. "
        "The AI will now ask context-aware technical questions. "
        "Answer naturally using your voice."
    )

    # --------------------------------------------------------
    # MAIN INTERVIEW AREA
    # --------------------------------------------------------

    left, right = st.columns([1.25, 1])

    # ========================================================
    # LEFT — PRESENTATION / CONTEXT
    # ========================================================

    with left:
        st.subheader("🖥️ Presentation Context")

        if st.session_state.latest_screen is not None:
            st.image(st.session_state.latest_screen, use_container_width=True)
        else:
            st.info("No presentation screen captured.")

        st.write("")

        with st.expander("🔎 Retrieved Context", expanded=True):
            st.markdown(
                """
                **Screen**

                • Project architecture

                • Model / technology information

                **Speech**

                • Student's explanation

                **Previous Answer**

                • Relevant interview response
                """
            )
    # ========================================================
    # RIGHT — AI INTERVIEWER
    # ========================================================

    with right:
        st.subheader("🤖 AI Interviewer")

        st.markdown(f"### 🤖 AI Question {st.session_state.question_number} / 3")

        st.info(st.session_state.question)

        # ==========================================
        # PLAY AI QUESTION
        # ==========================================

        if st.session_state.question_audio:
            audio_id = "ai_question_audio"

            audio_html = f"""
            <audio id="{audio_id}" preload="auto">
                <source
                    src="data:audio/wav;base64,{st.session_state.question_audio}"
                    type="audio/wav"
                >
            </audio>

            <button
                onclick="
                    document.getElementById('{audio_id}').play();
                "
                style="
                    width:100%;
                    padding:10px;
                    border-radius:8px;
                    border:1px solid #444;
                    background:#11151c;
                    color:white;
                    cursor:pointer;
                    font-size:16px;
                "
            >
                🔊 Play Question
            </button>
            """

            st.components.v1.html(audio_html, height=60)

        else:
            st.caption("🔊 Audio unavailable — please read the question above.")

        # ========================================================
        # STUDENT ANSWER
        # ========================================================

        st.markdown("### 🎤 Your Answer")

        st.info(
            "Speak your answer naturally. "
            "Your speech will automatically be converted to text."
        )

        answer_result = speech_component_ui(key="interview_answer")

        # ========================================================
        # AUDIO → WHISPER → TEXT
        # ========================================================

        if answer_result:
            audio_data = answer_result.get("audio", "")

            if audio_data:
                answer_hash = hashlib.md5(audio_data.encode()).hexdigest()

                # Process each audio chunk only once
                if answer_hash != st.session_state.last_answer_audio_hash:
                    st.session_state.last_answer_audio_hash = answer_hash

                    new_answer = transcribe_audio(audio_data)

                    if new_answer:
                        if st.session_state.answer_transcript:
                            st.session_state.answer_transcript += " "

                        st.session_state.answer_transcript += new_answer

        # ========================================================
        # SHOW TRANSCRIPT
        # ========================================================

        st.text_area(
            "Answer transcript",
            value=st.session_state.answer_transcript,
            height=130,
            disabled=True,
            label_visibility="collapsed",
        )

        # ========================================================
        # SUBMIT ANSWER
        # ========================================================

        if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
            answer = st.session_state.answer_transcript.strip()

            if not answer:
                st.warning("Please speak your answer first.")

            else:
                already_recorded = (
                    len(st.session_state.interview_history)
                    >= st.session_state.question_number
                )

                if not already_recorded:
                    st.session_state.interview_history.append(
                        {"question": st.session_state.question, "answer": answer}
                    )

                # =================================================
                # NEXT QUESTION OR FINAL EVALUATION
                # =================================================

                if st.session_state.question_number < 3:
                    try:
                        with st.spinner("🤖 Generating next question..."):
                            next_question = generate_question()

                        if next_question:
                            st.session_state.question_number += 1
                            st.session_state.question = next_question
                            st.session_state.question_audio = ""

                            try:
                                tts_result = speak_question(next_question)

                                if tts_result.get("success"):
                                    st.session_state.question_audio = tts_result.get(
                                        "audio", ""
                                    )

                            except Exception as e:
                                print("TTS failed:", e)

                            st.session_state.answer_transcript = ""
                            st.session_state.last_answer_audio_hash = ""

                            st.rerun()

                        else:
                            st.error("Could not generate next question.")

                    except Exception as e:
                        st.error(f"Could not generate next question: {e}")

                else:
                    # =============================================
                    # ALL 3 QUESTIONS FINISHED — FINAL EVALUATION
                    # =============================================

                    if st.session_state.get("final_evaluation_started", False):
                        started_at = st.session_state.get(
                            "final_evaluation_started_at", 0
                        )

                        if time.time() - started_at > 20:
                            st.session_state.final_evaluation_started = False
                            st.rerun()

                        st.info(
                            "🧠 Still preparing your final evaluation, please wait…"
                        )

                        if st.button("Retry evaluation now"):
                            st.session_state.final_evaluation_started = False
                            st.rerun()

                        time.sleep(1)
                        st.rerun()

                    st.session_state.final_evaluation_started = True
                    st.session_state.final_evaluation_started_at = time.time()

                    questions = [
                        item["question"] for item in st.session_state.interview_history
                    ]

                    answers = [
                        item["answer"] for item in st.session_state.interview_history
                    ]

                    try:
                        with st.spinner(
                            "🧠 Preparing your final interview evaluation..."
                        ):
                            result = evaluate_interview(questions, answers)

                        if result.get("success"):
                            st.session_state.final_evaluation = result
                            st.session_state.stage = "completed"
                            st.rerun()

                        else:
                            st.session_state.final_evaluation_started = False
                            st.error(result.get("error", "Final evaluation failed."))

                    except Exception as e:
                        st.session_state.final_evaluation_started = False
                        st.error(f"Final evaluation failed: {e}")
    # ========================================================
    # INTERVIEW HISTORY
    # ========================================================

    st.subheader("📋 Interview Progress")

    q1, q2, q3 = st.columns(3)

    with q1:
        st.metric("Questions", f"{st.session_state.question_number} / 3")

    with q2:
        st.metric("Difficulty", "Adaptive")

    with q3:
        st.metric(
            "Questions Completed", f"{len(st.session_state.interview_history)} / 3"
        )

    st.divider()


# ============================================================
# STAGE 4 — COMPLETED
# ============================================================

elif st.session_state.stage == "completed":
    st.success("🔵 INTERVIEW COMPLETED")

    st.markdown("## 📊 Final Evaluation")

    st.write("The AI has evaluated your presentation and interview responses.")

    st.divider()

    # ========================================================
    # REAL INTERVIEW SCORES
    # ========================================================

    final_eval = st.session_state.final_evaluation

    if final_eval:
        semantic_score = final_eval.get("semantic_score", 0)

        technical_score = final_eval.get("technical_score", 0)

        final_score = final_eval.get("final_score", 0)

        evaluation_text = final_eval.get("evaluation", "")

    else:
        semantic_score = 0
        technical_score = 0
        final_score = 0
        evaluation_text = "No evaluation available."

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Semantic Relevance", f"{semantic_score:.1f} / 10")

    with col2:
        st.metric("Technical Evaluation", f"{technical_score:.1f} / 10")

    with col3:
        st.metric("Final Score", f"{final_score:.1f} / 10")

    st.divider()

    st.subheader("🧠 Final Interview Feedback")

    st.write(evaluation_text)

    # --------------------------------------------------------
    # OVERALL SCORE
    # --------------------------------------------------------

    st.markdown("### 🏆 Overall Score")

    overall_score = final_score

    st.markdown(
        f'<div style="text-align:center;padding:30px;border-radius:15px;'
        f'background-color:#172235;border:1px solid #334;">'
        f'<div style="font-size:55px;font-weight:bold;">'
        f"{overall_score:.1f} / 10</div>"
        f'<div style="color:#aaa;margin-top:8px;">'
        f"Evidence-Grounded Technical Evaluation</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # RESTART
    # --------------------------------------------------------

    if st.button("🔄 Start New Interview", use_container_width=True):
        st.session_state.clear()
        st.rerun()
