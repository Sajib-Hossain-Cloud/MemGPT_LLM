"""
API initialization.
"""

from fastapi import FastAPI
from config.config import Config
from app.api.routes import router as agent_router

app = FastAPI(
    title="Letta-like Agent OS",
    description="A memory-powered agent operating system inspired by Letta",
    version="0.1.0"
)

# Add API prefix from config
app.include_router(agent_router, prefix=Config.API_PREFIX)

@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {
        "message": "Welcome to the Agent OS API",
        "version": "0.1.0",
        "docs_url": "/docs"
    } 