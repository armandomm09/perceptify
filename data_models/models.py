import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

engine = create_engine(os.getenv("DB_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    
    def __str__(self):
        return f"""Reading {self.id} at {self.timestamp}
            gyro_x: {self.gyro_x}
            gyro_y: {self.gyro_y}
            gyro_z: {self.gyro_z}
            accel_x: {self.accel_x}
            accel_y: {self.accel_y}
            accel_z: {self.accel_z}
        """
    
class FallCameraReading(Base):
    __tablename__ = "fall_detection"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    fall_detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=True)
    num_people_detected = Column(Integer, nullable=False)
    
    def __str__(self):
        return f"""Reading {self.id} at {self.timestamp}
        {f"has {self.num_people_detected} detections\n with {self.confidence}% of certainty" if self.fall_detected else "has no detections"}
        """
    
    
Base.metadata.create_all(bind=engine)