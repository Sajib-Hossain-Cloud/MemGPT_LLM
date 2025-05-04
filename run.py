"""
Script to run the FastAPI server.
"""

import uvicorn
from config.config import Config

if __name__ == "__main__":
    # Validate configuration settings
    Config.validate()
    
    # Run the server
    uvicorn.run(
        "app.api:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=Config.DEBUG
    ) 