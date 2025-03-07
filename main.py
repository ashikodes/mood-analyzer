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
        f"Analyze their mood based on these thoughts and provide:\n"
        f"- **Primary Emotion:** Identify the dominant emotion (e.g., Joy, Anxiety, Frustration, Optimism, etc.).\n"
        f"- **Mood Intensity:** Rate the intensity on a scale of 1 to 10.\n"
        f"- **Time Context:** Determine if the thoughts are mostly past-focused, present-focused, or future-focused.\n"
        f"- **Emotions, Motivations, Suggested Actions:** Provide structured emotional insights."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI that deeply analyzes emotions and provides structured insights."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.8
    )

    return response.choices[0].message.content.strip()

@app.post("/analyze-mood")
def analyze_mood(request: MoodRequest):
    insight = analyze_mood_openai(request.thoughts)
    return {"insight": insight}
