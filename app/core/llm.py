from typing import List, Literal, Optional
from pydantic import BaseModel
import os

try:
    import httpx  # only needed if Groq API is used
except ImportError:
    httpx = None  # fallback if not installed


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMClient:
    """
    LLM client with automatic fallback:
    
    ✔ If GROQ_API_KEY exists and httpx is installed:
        → Uses Groq LLaMA model (FREE real LLM)
    
    ✔ If no key OR httpx missing:
        → Uses offline heuristic response (prevents backend crashes)
    """

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.base_url = "https://api.groq.com/openai/v1"

        # Enable Groq only if: key exists + httpx installed
        self.groq_enabled = bool(self.api_key and httpx is not None)

    async def chat(self, history: List[Message]) -> str:
        """
        Chooses best mode automatically:
        - Groq LLaMA (free) → if available
        - Offline fallback → if no API key
        """
        if self.groq_enabled:
            try:
                return await self._chat_groq(history)
            except Exception as e:
                print("GROQ failed → falling back to offline mode:", e)

        return self._offline_reply(history)

    async def _chat_groq(self, history: List[Message]) -> str:
        """
        Actual call to Groq ChatCompletion API.
        """
        system_message = Message(
            role="system",
            content=(
                "You are an AI retail sales assistant. You help customers with "
                "product suggestions, outfit ideas, inventory checks, payments, "
                "returns, and store availability. Be clear, concise and helpful."
            ),
        )

        messages = [system_message] + history

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [m.model_dump() for m in messages],
                    "temperature": 0.4,
                },
            )

        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _offline_reply(self, history: List[Message]) -> str:
        """
        Safe fallback when no LLM or key is available.
        Always returns a helpful retail-style reply.
        Never crashes backend.
        """
        last_user_msg = ""

        # Find last user message
        for m in reversed(history):
            if m.role == "user":
                last_user_msg = m.content.lower().strip()
                break

        if not last_user_msg:
            return "Hello! Tell me what you're shopping for today."

        text = last_user_msg

        # Very small intent detection
        if "beach" in text or "vacation" in text:
            return (
                "Looking for vacation outfits? I can suggest lightweight shirts, "
                "shorts and dresses. Want options under a specific budget?"
            )

        if "budget" in text:
            return (
                "Sure! Tell me your budget and I’ll recommend the best outfits "
                "that match your style."
            )

        if "office" in text or "formal" in text:
            return (
                "For office wear, I can recommend shirts, trousers and blazers. "
                "Would you like something premium or budget-friendly?"
            )

        if "return" in text or "exchange" in text:
            return "I can help with returns or exchanges. What item would you like to return?"

        # Generic fallback
        return (
            "Understood. I can help you with recommendations, stock, offers, "
            "payments and reservations. Try: 'Suggest outfits under 3000'."
        )

def get_llm_client() -> LLMClient:
    """
    Small helper so other modules can do:
        from app.core.llm import get_llm_client
    and get a ready-to-use LLMClient instance.
    """
    return LLMClient()
