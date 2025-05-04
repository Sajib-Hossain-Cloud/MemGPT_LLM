"""
Application configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API")
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # API Settings
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # Rate Limiting
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))  # requests per minute
    
    @classmethod
    def validate(cls):
        """Validate required configuration settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables. Set the OPENAI_API environment variable.") 