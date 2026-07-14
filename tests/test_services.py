import os
import sys
import pytest

# Ensure backend/ is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.event_analyzer import EventAnalyzer
from app.services.topic_generator import TopicGenerator
from app.services.fact_checker import FactChecker

def test_event_analyzer_fallback():
    analyzer = EventAnalyzer()
    analyzer._failed_loading = True  # force keyword fallback path
    
    themes = analyzer.analyze("AI for Sustainable Cities", ["Artificial Intelligence", "Sustainability & Climate Change"])
    assert "Artificial Intelligence" in themes
    assert "Sustainability & Climate Change" in themes

def test_topic_generator_fallback():
    generator = TopicGenerator()
    generator._failed_loading = True  # force fallback path
    
    starters = generator.generate(
        event_description="AI for Sustainable Cities",
        themes=["Artificial Intelligence", "Sustainability & Climate Change"],
        interests=["climate change", "urban planning"],
        goals="find collaboration partners"
    )
    assert len(starters) == 3
    for s in starters:
        assert isinstance(s, str)
        assert len(s) > 10

def test_fact_checker_mock():
    checker = FactChecker()
    # Test fallback mocks
    res = checker.verify_fact("blockchain in healthcare")
    assert res["found"] is True
    assert "healthcare" in res["summary"].lower() or "blockchain" in res["summary"].lower()
    
    res_not_found = checker.verify_fact("nonexistent buzzword 12345")
    assert res_not_found["found"] is False
