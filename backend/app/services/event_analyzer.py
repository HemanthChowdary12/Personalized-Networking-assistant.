import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)

DEFAULT_CANDIDATE_THEMES = [
    "Artificial Intelligence",
    "Sustainability & Climate Change",
    "Blockchain & Cryptography",
    "Healthcare & Biotech",
    "Urban Planning & Smart Cities",
    "Finance & Venture Capital",
    "Software Development",
    "Marketing & Growth"
]

class EventAnalyzer:
    def __init__(self):
        self._pipeline = None
        self._failed_loading = False

    def _load_pipeline(self):
        if self._pipeline is not None or self._failed_loading:
            return

        try:
            # Lazy import to speed up startup
            from transformers import pipeline
            logger.info("Initializing DistilBERT zero-shot classification pipeline...")
            self._pipeline = pipeline(
                "zero-shot-classification",
                model="typeform/distilbert-base-uncased-mnli"
            )
            logger.info("DistilBERT zero-shot classification pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Hugging Face zero-shot classification pipeline: {e}. Falling back to keyword-based analyzer.")
            self._failed_loading = True

    def analyze(self, description: str, candidate_themes: Optional[List[str]] = None) -> List[str]:
        """
        Analyze event description and extract relevant themes.
        Uses DistilBERT zero-shot classification if available, otherwise falls back to a keyword-based rule system.
        """
        if not description or not description.strip():
            return []

        themes = candidate_themes or DEFAULT_CANDIDATE_THEMES
        self._load_pipeline()

        if self._pipeline is not None:
            try:
                result = self._pipeline(description, candidate_labels=themes)
                # Filter labels with score > 0.25, or at least return the top 2
                scores = result.get("scores", [])
                labels = result.get("labels", [])
                
                extracted = []
                for label, score in zip(labels, scores):
                    if score > 0.25:
                        extracted.append(label)
                
                # Ensure we return at least the top theme if none scored above threshold
                if not extracted and labels:
                    extracted.append(labels[0])
                
                return extracted[:3]  # Return top 3 themes max
            except Exception as e:
                logger.error(f"Error during DistilBERT inference: {e}. Using keyword fallback.")

        # Fallback keyword analyzer
        return self._fallback_analyze(description, themes)

    def _fallback_analyze(self, description: str, candidate_themes: List[str]) -> List[str]:
        """
        Fallback keyword-based theme extraction.
        """
        text = description.lower()
        matched = []

        # Simple mapping dictionary for standard themes and common keywords
        keyword_map = {
            "Artificial Intelligence": ["ai", "artificial intelligence", "machine learning", "deep learning", "nlp", "llm", "neural", "transformers", "gpt"],
            "Sustainability & Climate Change": ["climate", "sustainability", "sustainable", "carbon", "green", "energy", "solar", "wind", "environment"],
            "Blockchain & Cryptography": ["blockchain", "crypto", "cryptocurrency", "bitcoin", "ethereum", "web3", "ledger"],
            "Healthcare & Biotech": ["health", "healthcare", "biotech", "medical", "medicine", "clinical", "hospital", "patient"],
            "Urban Planning & Smart Cities": ["urban", "city", "cities", "planning", "smart cities", "infrastructure", "transportation"],
            "Finance & Venture Capital": ["finance", "venture", "capital", "funding", "invest", "investment", "fintech", "startup"],
            "Software Development": ["software", "development", "programming", "coding", "web dev", "developer", "engineering"],
            "Marketing & Growth": ["marketing", "growth", "sales", "branding", "seo", "social media", "customer"]
        }

        # Check user-provided labels vs standard ones
        for theme in candidate_themes:
            # Check direct match
            clean_theme = theme.lower()
            if clean_theme in text:
                matched.append(theme)
                continue

            # Check keywords mapping if it's one of our defaults
            keywords = keyword_map.get(theme, [])
            if not keywords:
                # If custom label, do a simple regex substring match
                words = re.findall(r'\w+', clean_theme)
                keywords = [w for w in words if len(w) > 3]

            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text):
                    matched.append(theme)
                    break

        # If nothing matched, default to the first candidate theme
        if not matched and candidate_themes:
            matched.append(candidate_themes[0])

        return matched[:3]
