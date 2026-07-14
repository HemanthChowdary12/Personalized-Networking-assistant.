import logging
import random
from typing import List, Optional

logger = logging.getLogger(__name__)

class TopicGenerator:
    def __init__(self):
        self._pipeline = None
        self._failed_loading = False

    def _load_pipeline(self):
        if self._pipeline is not None or self._failed_loading:
            return

        try:
            from transformers import pipeline
            logger.info("Initializing GPT-2 text-generation pipeline...")
            # Use gpt2-medium or gpt2. Let's use 'gpt2' as specified (GPT-2 Small)
            self._pipeline = pipeline(
                "text-generation",
                model="gpt2",
                max_new_tokens=40,
                pad_token_id=50256  # GPT-2 EOS token ID
            )
            logger.info("GPT-2 pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load GPT-2 text generation pipeline: {e}. Falling back to NLP template generator.")
            self._failed_loading = True

    def generate(self, event_description: str, themes: List[str], interests: List[str], goals: Optional[str] = None) -> List[str]:
        """
        Generate 2-3 tailored conversation starters.
        Combines GPT-2 text generation with NLP 5-step sales/engagement process templates for professional structure.
        """
        self._load_pipeline()
        
        starters = []
        primary_theme = themes[0] if themes else "this event"
        interest_str = ", ".join(interests) if interests else "networking"
        goal_str = goals or "exchanging ideas and making connections"

        # 1. Generate one creative starter using GPT-2 if available
        gpt_starter = None
        if self._pipeline is not None:
            try:
                # Craft a highly structured few-shot prompt for GPT-2 to follow
                prompt = (
                    f"Create a short, professional networking icebreaker question.\n"
                    f"Event: Tech Innovation Summit\n"
                    f"Interests: AI, start-ups\n"
                    f"Goal: find clients\n"
                    f"Icebreaker: \"I've been tracking the AI startup space recently. What's the biggest challenge you're seeing for early-stage companies scaling their engineering?\"\n"
                    f"---\n"
                    f"Event: Climate Action Forum\n"
                    f"Interests: solar power, sustainability\n"
                    f"Goal: learn about new technologies\n"
                    f"Icebreaker: \"With solar power expanding so quickly, I'm really curious about grid integration. What technologies are you most excited about right now?\"\n"
                    f"---\n"
                    f"Event: {event_description[:100]}\n"
                    f"Interests: {interest_str}\n"
                    f"Goal: {goal_str}\n"
                    f"Icebreaker: \""
                )
                
                outputs = self._pipeline(
                    prompt, 
                    num_return_sequences=1, 
                    temperature=0.7, 
                    top_k=50, 
                    top_p=0.9,
                    do_sample=True
                )
                
                generated_text = outputs[0]["generated_text"]
                # Extract what was generated after our prompt's "Icebreaker: \""
                if "Icebreaker: \"" in generated_text:
                    parts = generated_text.split("Icebreaker: \"")
                    # Get the last part, extract everything until the closing quote
                    candidate = parts[-1].split('"')[0].strip()
                    if len(candidate) > 20 and ("?" in candidate or "." in candidate):
                        gpt_starter = candidate
            except Exception as e:
                logger.error(f"Error during GPT-2 text generation: {e}")

        # If GPT-2 generated a valid starter, add it!
        if gpt_starter:
            starters.append(gpt_starter)

        # 2. Use NLP 5-Step Sales Process to craft structured templates to ensure premium quality
        # Step 1: Establish Rapport / Connect
        rapport_options = [
            f"Hi! I noticed the event page highlighted '{primary_theme}'. I'm really passionate about {interest_str}—what aspects of the theme are you focusing on today?",
            f"Hello! I'm trying to meet people here interested in {interest_str}. What brought you to this session on '{primary_theme}'?"
        ]
        
        # Step 2 & 3: Identify Need / Propose Solution (Value-oriented exploration)
        explore_options = [
            f"With all the discussion surrounding '{primary_theme}', how do you see {interest_str} changing the industry in the next few years?",
            f"I find that in the context of {primary_theme}, {interest_str} is becoming a major bottleneck. Are you experiencing that in your work as well?"
        ]

        # Step 5: Close / Action Oriented (Goal-aligned hook)
        goal_options = [
            f"I'm attending today with the goal to {goal_str} in the {interest_str} space. Do you have any recommendations on panel discussions or people I should connect with?",
            f"It's great to connect. Since I'm looking to {goal_str}, I'd love to know what challenges you're currently trying to solve in {interest_str}."
        ]

        # Assemble the rest of the starters
        starters.append(random.choice(rapport_options))
        starters.append(random.choice(explore_options))
        
        # If GPT-2 didn't work, add a goal-aligned one to make it 3 starters
        if len(starters) < 3:
            starters.append(random.choice(goal_options))

        # Ensure they are unique and capped at 3
        unique_starters = []
        for s in starters:
            if s not in unique_starters:
                unique_starters.append(s)
        
        # If we got less than 3, fill with a goal starter
        if len(unique_starters) < 3:
            unique_starters.append(random.choice(goal_options))

        return unique_starters[:3]
