import os
import time

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def transcribe_audio(audio_path):

    start_time = time.perf_counter()

    with open(audio_path, "rb") as audio_file:

        transcription = client.audio.transcriptions.create(
            file=(audio_path, audio_file.read()),
            model="whisper-large-v3-turbo",
            response_format="json",
            temperature=0.0
        )

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    print(f"Transcription time: {elapsed:.2f} seconds")

    return transcription.text