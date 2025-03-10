import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Use OpenAI client

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MoodRequest(BaseModel):
    thoughts: list[str]  # Expecting a list of three sentences

def analyze_mood_openai(thoughts):
    prompt = (
        f"The user shared these thoughts: {'. '.join(thoughts)}.\n\n"
        f"Analyze their mood and return the response in JSON format with these keys:\n"
        f"- 'primary_emotion': The dominant emotion (e.g., Joy, Anxiety, Frustration, Optimism, etc.).\n"
        f"- 'mood_intensity': A number from 1 to 10 representing emotional intensity.\n"
        f"- 'time_context': Identify whether thoughts are past-focused, present-focused, or future-focused.\n"
        f"- 'insight': Provide a short, meaningful emotional analysis, addressing the user directly using 'You' (e.g., 'You are experiencing...', 'Your thoughts indicate...').\n\n"
        f"Ensure the response is structured as JSON without any additional text."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI that provides structured mood analysis in JSON format, always addressing the user directly."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.8
    )

    import json
    try:
        mood_data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        mood_data = {"primary_emotion": "Unknown", "mood_intensity": "N/A", "time_context": "N/A", "insight": "Could not process response."}

    return mood_data

@app.post("/analyze-mood")
def analyze_mood(request: MoodRequest):
    mood_data = analyze_mood_openai(request.thoughts)
    return {
        "primary_emotion": mood_data.get("primary_emotion", ""),
        "mood_intensity": mood_data.get("mood_intensity", ""),
        "time_context": mood_data.get("time_context", ""),
        "insight": mood_data.get("insight", "")
    }
