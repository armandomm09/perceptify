import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Boolean, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

engine = create_engine(os.getenv("DB_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DetectionImage(Base):
    
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    

class BeltReading(Base):
    
        
    __tablename__ = "belt_reading"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    gyro_x=Column(Float, nullable=True)
    gyro_y=Column(Float, nullable=True)
    gyro_z=Column(Float, nullable=True)
    accel_x=Column(Float, nullable=True)
    accel_y=Column(Float, nullable=True)
    accel_z=Column(Float, nullable=True)
    fall=Column(Boolean, nullable=True)
    
    def __str__(self):
        return f"""Reading {self.id} at {self.timestamp}
            gyro_x: {self.gyro_x}
            gyro_y: {self.gyro_y}
            gyro_z: {self.gyro_z}
            accel_x: {self.accel_x}
            accel_y: {self.accel_y}
            accel_z: {self.accel_z}
            {"There has been a fall" if self.fall else "No falls detected"}
        """
    
    
class FallCameraReading(Base):
    __tablename__ = "fall_detection"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    fall_detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=True)
    num_people_detected = Column(Integer, nullable=False)
    img_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    # image = relationship("DetectionImage", back_populates="fall_readings")
    
    def __str__(self):
        return f"""Reading {self.id} at {self.timestamp}
        {f"has {self.num_people_detected} detections\n with {self.confidence}% of certainty" if self.fall_detected else "has no detections"}
        """
    
    def alert(self, timestamp=None):
        return (
            f"🚨 Fall Alert! 🚨\n"
            f"Time: {timestamp if timestamp else self.timestamp}\n"
            f"Confidence: {self.confidence}%\n"
            f"Number of people detected: {self.num_people_detected}"
        )
    
class EmotionDetection(Base):
    __tablename__ = "emotion_detection"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    img_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    dominant_emotion = Column(String(20), nullable=False)
    angry_probability = Column(Float, nullable=False)
    disgust_probability = Column(Float, nullable=False)
    fear_probability = Column(Float, nullable=False)
    happy_probability = Column(Float, nullable=False)
    neutral_probability = Column(Float, nullable=False)
    sad_probability = Column(Float, nullable=False)
    surprise_probability = Column(Float, nullable=False)
    video_id = Column(Integer, nullable=True)
    
    def __str__(self):
        return f"""
    Emotion detection at {self.timestamp}
        with {self.dominant_emotion} as dominant emotion:
            angry: {self.angry_probability}
            disgust: {self.disgust_probability}
            fear: {self.fear_probability}
            happy: {self.happy_probability}
            neutral: {self.neutral_probability}
            sad: {self.sad_probability}
        video number at {self.video_id}
        """
   
class EmotionDetectionVideo(Base):
    __tablename__ = "emotion_videos"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
     
    
Base.metadata.create_all(bind=engine)