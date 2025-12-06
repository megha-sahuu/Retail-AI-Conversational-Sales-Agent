from typing import List
from ..domain.models import Product, CustomerProfile
from ..core.llm import LLMClient, Message


class RecommendationAgent:
    """
    AI-powered recommendation engine.
    The LLM interprets the user's intent and extracts:
        - preferred product categories
        - style preference
        - budget
        - any extra filters
    """

    def __init__(self, products: List[Product], llm: LLMClient):
        self._products = products
        self.llm = llm

    async def recommend(
        self,
        message: str,
        customer: CustomerProfile,
        budget: float | None = None
    ) -> List[Product]:

        # ----------------------------------------------------------
        # 1) Ask LLM to extract shopping intent (category + style)
        # ----------------------------------------------------------
        prompt = f"""
You are an AI retail recommendation expert.

The user said: "{message}"

Your task:
1. Identify the product categories the user is looking for 
   (shirt, dress, shorts, jeans, kurta, t-shirt, etc.)
2. Identify optional style keywords 
   (casual, formal, beachwear, partywear, summer, sporty, etc.)
3. Identify an approximate budget if mentioned.

ONLY RETURN a JSON with keys:
{{
  "categories": ["category1", "category2"],
  "styles": ["style1", "style2"],
  "budget": number or null
}}

Examples:
Input: "Suggest outfits for a beach vacation under 3000"
Output:
{{
  "categories": ["shirt", "shorts", "dress"],
  "styles": ["beach", "summer"],
  "budget": 3000
}}
"""

        intent_raw = await self.llm.chat([
            Message(role="system", content="You extract shopping intent."),
            Message(role="user", content=prompt),
        ])

        # Try parsing LLM output
        import json
        try:
            intent = json.loads(intent_raw)
        except Exception:
            # fallback if LLM replies in plain text
            intent = {"categories": [], "styles": [], "budget": budget}

        extracted_categories = [c.lower() for c in intent.get("categories", [])]
        extracted_styles = [s.lower() for s in intent.get("styles", [])]
        extracted_budget = intent.get("budget") or budget

        # ----------------------------------------------------------
        # 2) Score products using AI signals
        # ----------------------------------------------------------
        scored = []

        for p in self._products:
            score = 0

            # Category match
            if extracted_categories:
                if any(cat in p.category.lower() for cat in extracted_categories):
                    score += 3

            # Style match (we check product name & category)
            if extracted_styles:
                if any(style in p.name.lower() or style in p.category.lower()
                       for style in extracted_styles):
                    score += 2

            # Price / budget constraint
            if extracted_budget is not None and p.price > extracted_budget:
                continue

            scored.append((score, p))

        # ----------------------------------------------------------
        # 3) Sort by AI relevance
        # ----------------------------------------------------------
        scored.sort(key=lambda x: x[0], reverse=True)

        # ----------------------------------------------------------
        # 4) If AI gave no meaningful matches → fallback
        # ----------------------------------------------------------
        if not scored or all(s == 0 for s, _ in scored):
            fallback = [
                p for p in self._products
                if extracted_budget is None or p.price <= extracted_budget
            ]
            fallback = sorted(fallback, key=lambda p: p.price)
            return fallback[:5]

        # ----------------------------------------------------------
        # 5) Return Top 5 smart recommendations
        # ----------------------------------------------------------
        return [p for _, p in scored[:5]]
