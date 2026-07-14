from pydantic import BaseModel, Field
from typing import List, Optional

class EventAnalysisRequest(BaseModel):
    description: str = Field(..., description="Description of the event to analyze")
    candidate_themes: Optional[List[str]] = Field(
        None, description="Optional custom candidate themes/labels for zero-shot classification"
    )

class EventAnalysisResponse(BaseModel):
    description: str
    themes: List[str] = Field(..., description="Extracted themes/topics from the description")

class ConversationRequest(BaseModel):
    event_description: str = Field(..., description="Description of the networking event")
    interests: List[str] = Field(..., description="User's interests to tailor the conversation starters")
    goals: Optional[str] = Field(None, description="User's career or networking goals (e.g., finding clients, job hunt)")

class ConversationResponse(BaseModel):
    id: str = Field(..., description="Unique ID for this recommendation batch")
    starters: List[str] = Field(..., description="Generated conversation starters")
    themes: List[str] = Field(..., description="Themes extracted from the event")
    timestamp: str = Field(..., description="Timestamp of when the starters were generated")

class FactCheckRequest(BaseModel):
    query: str = Field(..., description="Search query/fact to verify on Wikipedia")

class FactCheckResponse(BaseModel):
    query: str
    found: bool = Field(..., description="Whether a matching Wikipedia article was found")
    summary: str = Field(..., description="Summarized explanation of the topic")
    url: str = Field(..., description="Link to the Wikipedia source article")

class FeedbackRequest(BaseModel):
    starter_id: str = Field(..., description="The ID of the generated starter session")
    rating: str = Field(..., description="Feedback rating, e.g., 'up' or 'down'")
    comments: Optional[str] = Field(None, description="Optional text feedback or comments")

class FeedbackResponse(BaseModel):
    status: str = Field(default="success")
    message: str
