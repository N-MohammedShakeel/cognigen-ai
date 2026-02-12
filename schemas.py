# ---------------------------------------------------------
# schemas.py — ALIGNED WITH NEW NOTEBOOK STRUCTURE
# ---------------------------------------------------------

from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Union, Any
from datetime import datetime


# ---------------------------------------------------------
# TIME + PROFILE
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# NOTEBOOK CELL (MATCHES MONGODB SCHEMA)
# ---------------------------------------------------------
class NotebookCell(BaseModel):
    type: Literal[
        "markdown",
        "code",
        "resource",
        "image",
        "diagram",
        "separator"
    ]

    # Flexible payload depending on type
    content: Union[str, List[Dict[str, Any]], Dict[str, Any]]

    title: Optional[str] = None
    language: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# SUBMODULE CONTENT RESPONSE
# ---------------------------------------------------------
class SubmoduleContent(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    cells: List[NotebookCell]
    miniQuiz: List[Dict] = Field(default_factory=list)
    contentVersion: int = 2
    generatedAt: datetime


# ---------------------------------------------------------
# CONTENT GENERATION REQUEST
# ---------------------------------------------------------
class TopicContentGenerateRequest(BaseModel):
    topic_id: str
    topic_name: str
    course_name: str
    experience_level: Literal["beginner", "intermediate", "advanced"]
    submodules: List[Dict]


# ---------------------------------------------------------
# CONTENT GENERATION RESPONSE
# ---------------------------------------------------------
class TopicContentResponse(BaseModel):
    topic_id: str
    topic_name: str
    content: List[SubmoduleContent]
    summary: Optional[Dict] = None


# ---------------------------------------------------------
# LEARNING PATH RESPONSE
# ---------------------------------------------------------
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
