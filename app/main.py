from extractor import extract_text_from_docx
from processor import clean_text
from llm import generate_notes
from generator import create_docx


INPUT_FILE = "input/lecture.docx"
OUTPUT_FILE = "output/smart_notes.docx"


def main():

    print("Reading lecture transcript...")

    transcript = extract_text_from_docx(INPUT_FILE)

    print("Transcript extracted.")

    transcript = clean_text(transcript)

    print("Transcript cleaned.")

    print("Generating smart notes...")

    notes = generate_notes(transcript)

    print("Smart notes generated.")

    create_docx(
        notes,
        OUTPUT_FILE
    )

    print("Done!")


if __name__ == "__main__":
    main()