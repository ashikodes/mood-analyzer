import os
import logging
import time
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import NoResultFound
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import json
from models import MoodAnalysis, SessionLocal  # Import the MoodAnalysis model and SessionLocal

load_dotenv()  # Load API key from .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Use OpenAI client

app = FastAPI()

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("moodsense")


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
    logger.info("Analyzing mood for request...")
    try:
        # mood_data = analyze_mood_openai(request.thoughts)

        mood_data = {
            "primary_emotion": "Confusion - 3",
            "mood_intensity": 1,
            "time_context": "Present-focused",
            "insight": "Your message seems to be incomplete, causing a bit of confusion. It's important to express your thoughts fully to better understand your emotions."
        }

        # Save to database
        db: Session = SessionLocal()
        entry = MoodAnalysis(
            thoughts=json.dumps(request.thoughts),  # Convert list to string
            primary_emotion=mood_data.get("primary_emotion", ""),
            mood_intensity=int(mood_data.get("mood_intensity", 0)),
            time_context=mood_data.get("time_context", ""),
            insight=mood_data.get("insight", "")
        )
        db.add(entry)
        db.commit()
        mood_data["id"] = entry.id  # Add the generated ID to the response
        mood_data["thoughts"] = request.thoughts  # Include the original thoughts in the response

        time.sleep(3)  # Simulate processing time
        return mood_data;
        # return {
        #     "primary_emotion": mood_data.get("primary_emotion", ""),
        #     "mood_intensity": mood_data.get("mood_intensity", ""),
        #     "time_context": mood_data.get("time_context", ""),
        #     "insight": mood_data.get("insight", "")
        # }
    except Exception as e:
        logger.error(f"Error analyzing mood: {e}")
        raise HTTPException(status_code=500, detail="Error processing request")

@app.get("/results/{analysis_id}")
def get_mood_analysis(analysis_id: str):
    db = SessionLocal()
    try:
        entry = db.query(MoodAnalysis).filter(MoodAnalysis.id == analysis_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Mood analysis not found")
    
    time.sleep(1)

    return {
        "id": entry.id,
        "thoughts": json.loads(entry.thoughts),  # convert string back to list
        "primary_emotion": entry.primary_emotion,
        "mood_intensity": entry.mood_intensity,
        "time_context": entry.time_context,
        "insight": entry.insight
    }