import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.database import init_db
from backend.app.api.health import router as health_router
from backend.app.api.chat import router as chat_router
from backend.app.api.conversations import router as conversations_router
from backend.app.api.documents import router as documents_router
from backend.app.api.search import router as search_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    try:
        init_db()
        logger.info(f"{settings.APP_NAME} backend started successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Shutting down backend...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Beginner-friendly, modular Multimodal AI Chatbot with RAG, Web Search, and Emotional Assistance",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration to support Streamlit and external frontend callers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)")
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"{request.method} {request.url.path} FAILED after {duration_ms:.1f}ms: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred while processing your request."}
        )

# Register routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(documents_router)
app.include_router(search_router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs_url": "/docs",
        "health_check": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
