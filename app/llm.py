import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


SYSTEM_PROMPT = """
You are an expert lecture-to-study-notes converter.

Your job is to convert a raw lecture transcript into concise,
well-structured technical study notes.

The transcript may contain:
- Teacher explanations
- Student questions
- Repetitions
- Greetings
- Jokes
- Conversational noise
- Examples
- Analogies
- Important technical details

Your job is to preserve the important educational content while
removing unnecessary conversational material.

Create notes that are:
- Clear
- Technically accurate
- Concise but sufficiently detailed
- Easy to revise before an exam or interview
- Organized logically according to the lecture

Use numbered major sections.

For each major topic, create only the subsections that are actually
useful and supported by the transcript. Possible subsections include:

- What it is
- Key concepts
- How it works
- Example
- Analogy
- Important distinction
- Advantages
- Limitations
- Practical notes
- Rule of thumb

Do NOT create empty or irrelevant subsections.

Preserve important technical terminology from the lecture.

If the lecturer gives a workflow, represent it clearly using arrows,
for example:

Source → Pipeline → Lakehouse → Notebook → Power BI

At the end, include:
- Important takeaways
- Common mistakes

Do not include greetings, student chatter, jokes, or irrelevant
conversation in the final notes.

Return ONLY valid JSON.
Do not use Markdown.
Do not add explanations outside the JSON.

Use exactly this JSON structure:

{
    "title": "string",
    "sections": [
        {
            "number": 1,
            "title": "string",
            "subsections": [
                {
                    "title": "string",
                    "content": "string"
                }
            ]
        }
    ],
    "workflows": [
        "string"
    ],
    "important_takeaways": [
        "string"
    ],
    "common_mistakes": [
        "string"
    ]
}
"""


def generate_notes(transcript):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Convert the following lecture transcript into smart study notes.

LECTURE TRANSCRIPT:

{transcript}
"""
            }
        ]
    )

    content = response.choices[0].message.content

    return json.loads(content)