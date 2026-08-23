import streamlit as st


# ============================================================
# SPEECH HTML
# ============================================================

SPEECH_HTML = """
<div class="speech-container">

    <div class="speech-controls">

        <span id="speech-status">
            🎤 Starting microphone...
        </span>

    </div>

</div>
"""


# ============================================================
# SPEECH CSS
# ============================================================

SPEECH_CSS = """
.speech-container {
    width: 100%;
    font-family: sans-serif;
}

.speech-controls {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

#speech-status {
    color: #aaa;
    font-size: 14px;
}
"""


# ============================================================
# SPEECH JAVASCRIPT
# ============================================================

SPEECH_JS = """
export default function(component) {

    const {
        parentElement,
        setStateValue
    } = component;


    const status =
        parentElement.querySelector(
            "#speech-status"
        );


    let recorder = null;

    let recording = false;

    let timer = null;

    let microphoneStream = null;


    // ========================================================
    // SEND AUDIO TO PYTHON
    // ========================================================

    function sendAudio(blob) {

        const reader =
            new FileReader();


        reader.onloadend =
            function() {

                const base64Audio =
                    reader.result;


                setStateValue(
                    "audio",
                    base64Audio
                );
            };


        reader.readAsDataURL(blob);
    }


    // ========================================================
    // RECORD ONE 10-SECOND CHUNK
    // ========================================================

    function recordChunk() {

        if (!recording) {
            return;
        }


        navigator.mediaDevices
            .getUserMedia({
                audio: true
            })

            .then(function(stream) {

                microphoneStream =
                    stream;


                recorder =
                    new MediaRecorder(
                        stream,
                        {
                            mimeType:
                                "audio/webm"
                        }
                    );


                const chunks = [];


                // --------------------------------------------
                // Collect audio data
                // --------------------------------------------

                recorder.ondataavailable =
                    function(event) {

                        if (
                            event.data &&
                            event.data.size > 0
                        ) {

                            chunks.push(
                                event.data
                            );
                        }
                    };


                // --------------------------------------------
                // Chunk finished
                // --------------------------------------------

                recorder.onstop =
                    function() {

                        // Stop microphone tracks
                        if (
                            microphoneStream
                        ) {

                            microphoneStream
                                .getTracks()
                                .forEach(
                                    track =>
                                        track.stop()
                                );

                            microphoneStream =
                                null;
                        }


                        // Create audio blob
                        const blob =
                            new Blob(
                                chunks,
                                {
                                    type:
                                        "audio/webm"
                                }
                            );


                        // Send only valid, non-trivial audio.
                        // Very small blobs are almost always silence
                        // or background noise, which is exactly what
                        // causes Whisper to hallucinate stock phrases
                        // like "thank you" or "next video" — so skip
                        // sending them at all.
                        if (
                            blob.size > 8000
                        ) {

                            sendAudio(
                                blob
                            );
                        }


                        recorder = null;


                        // Continue listening
                        if (
                            recording
                        ) {

                            setTimeout(
                                function() {

                                    recordChunk();

                                },
                                200
                            );
                        }

                    };


                // --------------------------------------------
                // Start recording
                // --------------------------------------------

                recorder.start();


                status.textContent =
                    "🟢 Listening...";


                setStateValue(
                    "recording",
                    true
                );


                // --------------------------------------------
                // Stop after 10 seconds
                // --------------------------------------------

                timer =
                    setTimeout(
                        function() {

                            if (
                                recorder &&
                                recorder.state ===
                                    "recording"
                            ) {

                                recorder.stop();
                            }

                        },
                        8000
                    );

            })

            .catch(function(error) {

                console.error(
                    "Microphone error:",
                    error
                );


                status.textContent =
                    "❌ Microphone permission denied";


                setStateValue(
                    "recording",
                    false
                );

            });
    }


    // ========================================================
    // START SPEECH AUTOMATICALLY
    // ========================================================

    async function startSpeech() {

        try {

            // Ask for microphone permission
            const stream =
                await navigator.mediaDevices
                    .getUserMedia({
                        audio: true
                    });


            // Stop this temporary stream.
            // recordChunk() will create the actual stream.
            stream
                .getTracks()
                .forEach(
                    track =>
                        track.stop()
                );


            recording = true;


            status.textContent =
                "🟢 Listening...";


            setStateValue(
                "recording",
                true
            );


            // Start first chunk
            recordChunk();


        } catch (error) {

            console.error(
                "Microphone permission error:",
                error
            );


            status.textContent =
                "❌ Microphone access denied";


            setStateValue(
                "recording",
                false
            );
        }
    }


    // ========================================================
    // START AUTOMATICALLY
    // ========================================================

    startSpeech();


    // ========================================================
    // CLEANUP
    // ========================================================

    return () => {

        recording = false;


        if (timer) {

            clearTimeout(
                timer
            );

            timer = null;
        }


        if (
            recorder &&
            recorder.state ===
                "recording"
        ) {

            recorder.stop();
        }


        recorder = null;


        if (
            microphoneStream
        ) {

            microphoneStream
                .getTracks()
                .forEach(
                    track =>
                        track.stop()
                );

            microphoneStream = null;
        }


        setStateValue(
            "recording",
            false
        );
    };
}
"""


# ============================================================
# STREAMLIT COMPONENT
# ============================================================

speech_component = st.components.v2.component(
    "projectviva_speech",
    html=SPEECH_HTML,
    css=SPEECH_CSS,
    js=SPEECH_JS,
)


# ============================================================
# COMPONENT FUNCTION
# ============================================================


def speech_component_ui(key="speech_component"):

    return speech_component(key=key)
