import os
import sys
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure backend/ is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

# Temporary file paths for testing to isolate from main user files
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "data"))
TEST_HISTORY_PATH = os.path.join(TEST_DATA_DIR, "test_history.json")
TEST_FEEDBACK_PATH = os.path.join(TEST_DATA_DIR, "test_feedback.json")

# Clean leftover test files if any
for path in [TEST_HISTORY_PATH, TEST_FEEDBACK_PATH]:
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass

# Import application under patches so endpoints use the test JSON paths
with patch("app.routes.endpoints.HISTORY_PATH", TEST_HISTORY_PATH), \
     patch("app.routes.endpoints.FEEDBACK_PATH", TEST_FEEDBACK_PATH):
    
    from app.main import app
    client = TestClient(app)

    @patch("app.routes.endpoints.analyzer._load_pipeline")
    @patch("app.routes.endpoints.generator._load_pipeline")
    def test_endpoints(mock_gen_pipe, mock_ana_pipe):
        # Mock backend pipelines to use quick fallback models
        from app.routes.endpoints import analyzer, generator
        analyzer._failed_loading = True
        generator._failed_loading = True

        # 1. Test /analyze-event
        res = client.post("/api/v1/analyze-event", json={
            "description": "AI for Sustainable Cities",
            "candidate_themes": ["Artificial Intelligence", "Sustainability & Climate Change"]
        })
        assert res.status_code == 200
        data = res.json()
        assert "themes" in data
        assert "Artificial Intelligence" in data["themes"]

        # 2. Test /generate-conversation
        res = client.post("/api/v1/generate-conversation", json={
            "event_description": "AI for Sustainable Cities",
            "interests": ["climate change", "urban planning"],
            "goals": "find collaborators"
        })
        assert res.status_code == 200
        data = res.json()
        assert "id" in data
        assert len(data["starters"]) == 3
        session_id = data["id"]

        # 3. Test /fact-check
        res = client.post("/api/v1/fact-check", json={"query": "blockchain in healthcare"})
        assert res.status_code == 200
        data = res.json()
        assert data["found"] is True
        assert "summary" in data

        # 4. Test /feedback
        res = client.post("/api/v1/feedback", json={
            "starter_id": f"{session_id}_0",
            "rating": "up"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"

        # 5. Test /history
        res = client.get("/api/v1/history")
        assert res.status_code == 200
        history = res.json()
        assert len(history) > 0
        assert history[0]["event_description"] == "AI for Sustainable Cities"
        assert history[0]["starters_feedback"][f"{session_id}_0"]["rating"] == "up"

        # Cleanup test files after verification
        for path in [TEST_HISTORY_PATH, TEST_FEEDBACK_PATH]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
