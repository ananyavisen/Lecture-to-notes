from pathlib import Path

from extractor import extract_text_from_docx
from processor import clean_text
from transcriber import transcribe_audio
from llm import generate_notes
from generator import create_docx


INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

OUTPUT_FILE = OUTPUT_DIR / "smart_notes.docx"


SUPPORTED_AUDIO = {
    ".mp3",
    ".mp4",
    ".m4a",
    ".wav",
    ".webm",
    ".ogg",
}


def get_input_file():
    """
    Find the first supported lecture file in the input directory.
    """

    files = [
        file
        for file in INPUT_DIR.iterdir()
        if file.is_file()
    ]

    if not files:
        raise FileNotFoundError(
            "No lecture file found in the input directory."
        )

    for file in files:

        if file.suffix.lower() == ".docx":
            return file

        if file.suffix.lower() in SUPPORTED_AUDIO:
            return file

    raise ValueError(
        "Unsupported file type. "
        "Please provide a .docx or supported audio file."
    )


def get_transcript(input_file):
    """
    Convert the input file into plain transcript text.
    """

    extension = input_file.suffix.lower()

    if extension == ".docx":

        print("Input type: DOCX")
        print("Extracting transcript...")

        transcript = extract_text_from_docx(
            str(input_file)
        )

    elif extension in SUPPORTED_AUDIO:

        print("Input type: Audio")
        print("Transcribing audio using Whisper...")

        transcript = transcribe_audio(
            str(input_file)
        )

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return transcript


def main():

    print("=" * 50)
    print("       LECTURE → SMART NOTES")
    print("=" * 50)

    # -----------------------------------
    # 1. Find input
    # -----------------------------------

    input_file = get_input_file()

    print(f"\nInput file: {input_file}")

    # -----------------------------------
    # 2. Extract / transcribe
    # -----------------------------------

    transcript = get_transcript(input_file)

    if not transcript.strip():
        raise ValueError(
            "No transcript text could be extracted."
        )

    print(
        f"Transcript obtained "
        f"({len(transcript)} characters)."
    )

    # -----------------------------------
    # 3. Clean transcript
    # -----------------------------------

    print("\nCleaning transcript...")

    transcript = clean_text(transcript)

    print("Transcript cleaned.")

    # -----------------------------------
    # 4. Generate smart notes
    # -----------------------------------

    print("\nGenerating smart notes using Groq...")

    notes = generate_notes(transcript)

    print("Smart notes generated.")

    # -----------------------------------
    # 5. Generate DOCX
    # -----------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nCreating Smart Notes document...")

    create_docx(
        notes,
        str(OUTPUT_FILE)
    )

    # -----------------------------------
    # 6. Finished
    # -----------------------------------

    print("\n" + "=" * 50)
    print("SUCCESS")
    print("=" * 50)

    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()