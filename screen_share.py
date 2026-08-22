import streamlit as st


SCREEN_SHARE_HTML = """
<div class="screen-share-container">

    <div class="controls">
        <button id="share-btn">
            🖥️ Share Screen
        </button>

        <button id="stop-btn" disabled>
            ⏹ Stop Sharing
        </button>

        <span id="status">
            Not sharing
        </span>
    </div>

    <video
        id="screen-video"
        autoplay
        playsinline
        muted
    ></video>

    <canvas
    id="capture-canvas"
    style="display:none;"
    ></canvas>

</div>
"""


SCREEN_SHARE_CSS = """
.screen-share-container {
    width: 100%;
    font-family: sans-serif;
}

.controls {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}

button {
    padding: 10px 18px;
    border-radius: 8px;
    border: 1px solid #555;
    background: #262730;
    color: white;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background: #3a3b45;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

#status {
    color: #aaa;
    font-size: 14px;
}

#screen-video {
    width: 100%;
    min-height: 350px;
    max-height: 600px;
    object-fit: contain;
    background: #0e1117;
    border: 2px solid #444;
    border-radius: 10px;
}
"""


SCREEN_SHARE_JS = """
export default function(component) {

    const { parentElement, setStateValue } = component;

    const shareButton =
        parentElement.querySelector("#share-btn");

    const stopButton =
        parentElement.querySelector("#stop-btn");

    const video =
        parentElement.querySelector("#screen-video");

    const canvas =
        parentElement.querySelector("#capture-canvas");

    const status =
        parentElement.querySelector("#status");

    let stream = null;
    let captureInterval = null;


    // ==========================================
    // START SCREEN SHARE
    // ==========================================

    async function startScreenShare() {

        try {

            status.textContent =
                "Requesting screen access...";

            stream =
                await navigator.mediaDevices.getDisplayMedia({
                    video: true,
                    audio: false
                });

            video.srcObject = stream;

            await video.play();

            shareButton.disabled = true;
            stopButton.disabled = false;

            status.textContent =
                "🟢 Screen sharing active";


            // Tell Python sharing has started
            setStateValue(
                "sharing",
                true
            );


            // Start capturing screenshots
            startCapture();


            // Detect when user stops sharing
            const track =
                stream.getVideoTracks()[0];

            track.addEventListener(
                "ended",
                stopScreenShare
            );


        } catch (error) {

            console.error(error);

            status.textContent =
                "❌ Screen sharing cancelled";

            setStateValue(
                "sharing",
                false
            );
        }
    }


    // ==========================================
    // CAPTURE SCREEN FRAME
    // ==========================================

    function startCapture() {

        captureInterval =
            setInterval(() => {

                if (
                    !stream ||
                    video.readyState < 2 ||
                    video.videoWidth === 0
                ) {
                    return;
                }


                // Smaller image = faster transfer
                const width = 1000;

                const height =
                    Math.round(
                        video.videoHeight /
                        video.videoWidth *
                        width
                    );


                canvas.width = width;
                canvas.height = height;


                const context =
                    canvas.getContext("2d");


                // Copy current screen into canvas
                context.drawImage(
                    video,
                    0,
                    0,
                    width,
                    height
                );


                // Convert screenshot to JPEG
                const image =
                    canvas.toDataURL(
                        "image/jpeg",
                        0.65
                    );


                // Send screenshot to Python
                setStateValue(
                    "frame",
                    image
                );


            }, 2000);   // capture every 2 seconds
    }


    // ==========================================
    // STOP SCREEN SHARE
    // ==========================================

    function stopScreenShare() {

        if (captureInterval) {

            clearInterval(
                captureInterval
            );

            captureInterval = null;
        }


        if (stream) {

            stream
                .getTracks()
                .forEach(
                    track => track.stop()
                );

            stream = null;
        }


        video.srcObject = null;

        shareButton.disabled = false;
        stopButton.disabled = true;

        status.textContent =
            "Screen sharing stopped";


        setStateValue(
            "sharing",
            false
        );

        setStateValue(
            "frame",
            ""
        );
    }


    // ==========================================
    // BUTTON EVENTS
    // ==========================================

    shareButton.onclick =
        startScreenShare;

    stopButton.onclick =
        stopScreenShare;


    // ==========================================
    // CLEANUP
    // ==========================================

    return () => {

        if (captureInterval) {

            clearInterval(
                captureInterval
            );
        }

        if (stream) {

            stream
                .getTracks()
                .forEach(
                    track => track.stop()
                );
        }
    };
}
"""


# Register the Streamlit V2 component
screen_share_component = st.components.v2.component(
    "projectviva_screen_share",
    html=SCREEN_SHARE_HTML,
    css=SCREEN_SHARE_CSS,
    js=SCREEN_SHARE_JS,
)


def on_sharing_change():
    pass


def on_frame_change():
    pass


def screen_share(key="screen_share"):

    return screen_share_component(
        key=key,
        default={"sharing": False, "frame": ""},
        on_sharing_change=on_sharing_change,
        on_frame_change=on_frame_change,
    )
