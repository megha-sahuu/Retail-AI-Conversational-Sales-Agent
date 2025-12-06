from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.logging import setup_logging
from .api.v1.routes_chat import router as chat_router

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)

# 🔹 CORS setup – allow frontend (Vite) to call this API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # you can put ["*"] during dev if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 API routes
app.include_router(chat_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
