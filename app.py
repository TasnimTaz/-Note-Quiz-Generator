import streamlit as st
from api_calling import note_generator, audio_transcription, quize_generator
from PIL import Image

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Note & Quiz Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Note Summary & Quiz Generator", anchor=False)
st.markdown("Upload up to **3 images** of your notes to generate a structured summary and quiz.")
st.divider()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    images = st.file_uploader(
        "Upload photos of your notes",
        type=["JPEG", "JPG", "PNG"],
        accept_multiple_files=True
    )

    if images:
        if len(images) > 3:
            st.error("⚠️ You can upload a maximum of 3 images.")
            images = None
        else:
            st.subheader("📷 Uploaded Images")
            cols = st.columns(len(images))
            for i, per_image in enumerate(images):
                with cols[i]:
                    try:
                        st.image(per_image, use_container_width=True)
                    except Exception:
                        st.warning(f"Could not preview image {i+1}.")

    difficulty = st.selectbox(
        "Quiz Difficulty",
        ("Easy", "Medium", "Hard"),
        index=None,
        placeholder="Select difficulty..."
    )

    button = st.button("🚀 Generate Notes & Quiz", type="primary", use_container_width=True)


# ── Main Logic ────────────────────────────────────────────────────────────────
if button:
    has_error = False

    if not images:
        st.error("⚠️ You must upload at least 1 image.")
        has_error = True

    if not difficulty:
        st.error("⚠️ You must select a difficulty.")
        has_error = True

    if not has_error:
        pil_images = []
        for img in images:
            try:
                pil_img = Image.open(img)
                pil_images.append(pil_img)
            except Exception as e:
                st.error(f"⚠️ Could not open '{img.name}': {e}")
                has_error = True
                break

    if not has_error:

        # ── Note Generation ───────────────────────────────────────────────
        generated_notes = None
        detected_lang = "en"

        with st.container(border=True):
            st.subheader("📝 Your Note Summary")
            with st.spinner("AI is writing your notes..."):
                try:
                    generated_notes, detected_lang = note_generator(pil_images)
                    st.markdown(generated_notes)
                except RuntimeError as e:
                    st.error(f"⚠️ Note generation failed: {e}")

        # ── Audio Transcription ───────────────────────────────────────────
        if generated_notes:
            with st.container(border=True):
                st.subheader("🔊 Audio Transcription")
                with st.spinner("AI is generating your audio..."):
                    try:
                        audio_buffer = audio_transcription(generated_notes, lang=detected_lang)
                        st.audio(audio_buffer, format="audio/mp3")
                    except (RuntimeError, ValueError) as e:
                        st.error(f"⚠️ Audio generation failed: {e}")

        # ── Quiz Generation ───────────────────────────────────────────────
        with st.container(border=True):
            st.subheader(f"🧠 Quiz — {difficulty} Difficulty")
            with st.spinner("AI is generating your quiz..."):
                try:
                    quizzes = quize_generator(pil_images, difficulty, lang=detected_lang)
                    st.markdown(quizzes)
                except RuntimeError as e:
                    st.error(f"⚠️ Quiz generation failed: {e}")