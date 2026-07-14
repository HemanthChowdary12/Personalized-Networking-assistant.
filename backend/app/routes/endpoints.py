import os
import json
import uuid
import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.models import (
    EventAnalysisRequest, EventAnalysisResponse,
    ConversationRequest, ConversationResponse,
    FactCheckRequest, FactCheckResponse,
    FeedbackRequest, FeedbackResponse
)
from app.services.event_analyzer import EventAnalyzer
from app.services.topic_generator import TopicGenerator
from app.services.fact_checker import FactChecker

router = APIRouter()

# Instantiate services
analyzer = EventAnalyzer()
generator = TopicGenerator()
checker = FactChecker()

# Paths to persistence files
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def _read_json_file(file_path: str) -> List[Any]:
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []

def _write_json_file(file_path: str, data: List[Any]):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {e}")

@router.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Personalized Networking Assistant API"
    }

@router.post("/analyze-event", response_model=EventAnalysisResponse)
async def analyze_event(payload: EventAnalysisRequest):
    try:
        themes = analyzer.analyze(payload.description, payload.candidate_themes)
        return EventAnalysisResponse(
            description=payload.description,
            themes=themes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-conversation", response_model=ConversationResponse)
async def generate_conversation(payload: ConversationRequest):
    try:
        # 1. Analyze the event description to extract themes
        themes = analyzer.analyze(payload.event_description)
        
        # 2. Generate conversation starters based on extracted themes and user details
        starters = generator.generate(
            event_description=payload.event_description,
            themes=themes,
            interests=payload.interests,
            goals=payload.goals
        )
        
        # 3. Formulate the response
        response_id = f"session_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.datetime.now().isoformat()
        
        response = ConversationResponse(
            id=response_id,
            starters=starters,
            themes=themes,
            timestamp=timestamp
        )
        
        # 4. Log the output in history.json
        history = _read_json_file(HISTORY_PATH)
        history_item = {
            "id": response_id,
            "timestamp": timestamp,
            "event_description": payload.event_description,
            "interests": payload.interests,
            "goals": payload.goals,
            "themes": themes,
            "starters": starters
        }
        history.insert(0, history_item)  # Keep newest first
        _write_json_file(HISTORY_PATH, history)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(payload: FactCheckRequest):
    try:
        result = checker.verify_fact(payload.query)
        return FactCheckResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    try:
        if payload.rating not in ["up", "down"]:
            raise HTTPException(status_code=400, detail="Rating must be 'up' or 'down'")
            
        feedback_list = _read_json_file(FEEDBACK_PATH)
        feedback_item = {
            "starter_id": payload.starter_id,
            "rating": payload.rating,
            "comments": payload.comments,
            "timestamp": datetime.datetime.now().isoformat()
        }
        feedback_list.append(feedback_item)
        _write_json_file(FEEDBACK_PATH, feedback_list)
        
        return FeedbackResponse(
            status="success",
            message=f"Feedback recorded for starter: {payload.starter_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history() -> List[Dict[str, Any]]:
    # Reads the generated starter sessions and matches them with any feedback recorded
    history = _read_json_file(HISTORY_PATH)
    feedback = _read_json_file(FEEDBACK_PATH)
    
    # Map feedback by starter_id (e.g. session_abc_index)
    feedback_map = {}
    for fb in feedback:
        feedback_map[fb["starter_id"]] = {
            "rating": fb["rating"],
            "comments": fb.get("comments")
        }
        
    # Append feedback status to history items
    enriched_history = []
    for item in history:
        enriched_item = item.copy()
        session_id = item["id"]
        starters_feedback = {}
        for idx in range(len(item["starters"])):
            starter_id = f"{session_id}_{idx}"
            starters_feedback[starter_id] = feedback_map.get(starter_id, {"rating": None, "comments": None})
        enriched_item["starters_feedback"] = starters_feedback
        enriched_history.append(enriched_item)
        
    return enriched_history
