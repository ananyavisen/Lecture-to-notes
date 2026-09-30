import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# Allow imports from the app directory
APP_DIR = Path(__file__).resolve().parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from extractor import extract_text_from_docx
from processor import clean_text
from transcriber import transcribe_audio
from llm import generate_notes
from generator import create_docx


# -----------------------------------
# Configuration
# -----------------------------------

st.set_page_config(
    page_title="Record Lecture, Automate Notes",
    page_icon="📝",
    layout="wide"
)


SUPPORTED_AUDIO = {
    ".mp3",
    ".mp4",
    ".m4a",
    ".wav",
    ".webm",
    ".ogg",
}


# -----------------------------------
# Helper functions
# -----------------------------------

def get_transcript(uploaded_file):
    """
    Convert uploaded DOCX/audio file into transcript text.
    """

    extension = Path(uploaded_file.name).suffix.lower()

    if extension == ".docx":

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        try:
            transcript = extract_text_from_docx(temp_path)

        finally:
            os.unlink(temp_path)

        return transcript

    elif extension in SUPPORTED_AUDIO:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        try:
            transcript = transcribe_audio(temp_path)

        finally:
            os.unlink(temp_path)

        return transcript

    else:

        raise ValueError(
            "Unsupported file type."
        )


def generate_smart_notes(uploaded_file):

    # -----------------------------------
    # 1. Transcript
    # -----------------------------------

    with st.status(
        "Processing lecture...",
        expanded=True
    ) as status:

        st.write("Reading lecture...")

        transcript = get_transcript(uploaded_file)

        if not transcript.strip():
            raise ValueError(
                "No transcript could be extracted."
            )

        st.write(
            f"Transcript obtained "
            f"({len(transcript):,} characters)."
        )

        # -----------------------------------
        # 2. Clean
        # -----------------------------------

        st.write("Cleaning transcript...")

        transcript = clean_text(transcript)

        # -----------------------------------
        # 3. LLM
        # -----------------------------------

        st.write("Generating smart notes with Groq...")

        notes = generate_notes(transcript)

        # -----------------------------------
        # 4. DOCX
        # -----------------------------------

        st.write("Creating Smart Notes document...")

        output_dir = Path(tempfile.mkdtemp())

        output_file = (
            output_dir
            / f"{Path(uploaded_file.name).stem}_smart_notes.docx"
        )

        create_docx(
            notes,
            str(output_file)
        )

        status.update(
            label="Smart notes generated successfully!",
            state="complete",
            expanded=False
        )

    return notes, output_file, transcript


# -----------------------------------
# Header
# -----------------------------------

st.title("Record Lectures, Automate Notes")

st.write(
    "No more hassle of writing and hearing together."
    "Focus on listening, no more worries for notes."
)


# -----------------------------------
# File upload
# -----------------------------------

uploaded_file = st.file_uploader(
    "Upload your lecture",
    type=[
        "docx",
        "mp3",
        "mp4",
        "m4a",
        "wav",
        "webm",
        "ogg"
    ],
    help="Upload a DOCX transcript or an audio lecture."
)


# -----------------------------------
# Generate button
# -----------------------------------

if uploaded_file:

    st.info(
        f"Selected: **{uploaded_file.name}**"
    )

    if st.button(
        "Generate Smart Notes",
        type="primary",
        use_container_width=True
    ):

        try:

            notes, output_file, transcript = (
                generate_smart_notes(uploaded_file)
            )

            st.session_state["notes"] = notes
            st.session_state["output_file"] = output_file
            st.session_state["transcript"] = transcript

        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )


# -----------------------------------
# Display results
# -----------------------------------

if "notes" in st.session_state:

    notes = st.session_state["notes"]

    st.divider()

    st.header(notes.get("title", "Smart Notes"))

    # -----------------------------------
    # Sections
    # -----------------------------------

    for section in notes.get("sections", []):

        section_number = section.get(
            "number",
            ""
        )

        section_title = section.get(
            "title",
            ""
        )

        st.subheader(
            f"{section_number}. {section_title}"
        )

        for subsection in section.get(
            "subsections",
            []
        ):

            subsection_title = subsection.get(
                "title",
                ""
            )

            content = subsection.get(
                "content",
                ""
            )

            st.markdown(
                f"**{subsection_title}**"
            )

            st.write(content)

    # -----------------------------------
    # Workflows
    # -----------------------------------

    workflows = notes.get(
        "workflows",
        []
    )

    if workflows:

        st.divider()

        st.subheader("Workflows")

        for workflow in workflows:

            st.markdown(
                f"- {workflow}"
            )

    # -----------------------------------
    # Important Takeaways
    # -----------------------------------

    takeaways = notes.get(
        "important_takeaways",
        []
    )

    if takeaways:

        st.divider()

        st.subheader(
            "Important Takeaways"
        )

        for takeaway in takeaways:

            st.markdown(
                f"- {takeaway}"
            )

    # -----------------------------------
    # Common Mistakes
    # -----------------------------------

    mistakes = notes.get(
        "common_mistakes",
        []
    )

    if mistakes:

        st.divider()

        st.subheader(
            "Common Beginner Mistakes"
        )

        for mistake in mistakes:

            st.markdown(
                f"- {mistake}"
            )

    # -----------------------------------
    # Download
    # -----------------------------------

    st.divider()

    output_file = st.session_state[
        "output_file"
    ]

    with open(output_file, "rb") as file:

        st.download_button(
            label="Download Smart Notes (.docx)",
            data=file,
            file_name=output_file.name,
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            type="primary",
            use_container_width=True
        )