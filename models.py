import os
from sqlalchemy import create_engine, Column, String, Integer, Text, Table
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid

Base = declarative_base()

class MoodAnalysis(Base):
    __tablename__ = "mood_analysis"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thoughts = Column(Text)  # Store the list as JSON or string
    primary_emotion = Column(String)
    mood_intensity = Column(Integer)
    time_context = Column(String)
    insight = Column(Text)

# DB setup
db_path = os.getenv("SQLITE_PATH", "moodsense.db")
engine = create_engine(f"sqlite:///{db_path}", echo=False)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
