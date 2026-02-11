# schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime


class TimeAvailability(BaseModel):
    per_day_hours: int = Field(..., ge=1, le=24)


class StudentProfile(BaseModel):
    user_id: str
    course_name: str
    experience_level: Literal["beginner", "intermediate", "advanced"]
    custom_topics: List[str] = Field(default_factory=list)
    goal: str
    preferred_learning_style: Literal["theory", "practical", "mixed"]
    time_availability: TimeAvailability


class LearningPathCreateRequest(BaseModel):
    user_id: str
    course_name: str
    experience_level: Literal["beginner", "intermediate", "advanced"]
    custom_topics: List[str] = Field(default_factory=list)
    goal: str
    preferred_learning_style: Literal["theory", "practical", "mixed"]
    time_availability: TimeAvailability


class TopicBase(BaseModel):
    id: str
    name: str
    order: int
    difficulty: Literal["easy", "medium", "hard"]
    estimated_time_hours: float
    completed: bool = False
    submodules: List[Dict] = Field(default_factory=list)


class LearningPathResponse(BaseModel):
    id: str
    title: str
    description: str
    course_name: str
    goal: str
    student_profile: StudentProfile
    topics: List[Dict]
    progress: Dict
    status: Literal["draft", "active", "archived"] = "draft"
    createdAt: str
    updatedAt: str


class TopicContentGenerateRequest(BaseModel):
    topic_id: str
    topic_name: str
    course_name: str
    experience_level: Literal["beginner", "intermediate", "advanced"]
    submodules: List[Dict]


class TopicContentResponse(BaseModel):
    topic_id: str
    topic_name: str
    content: List[Dict]
