"""
utils.py
Utility functions for logging, config, and other helpers.
"""

from loguru import logger
import os
from dotenv import load_dotenv
import sys

def setup_logging():
    """
    Configures logging for the agentic framework.
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file handler for agent logs
    os.makedirs("output", exist_ok=True)
    logger.add(
        "output/agent.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 MB",
        retention="7 days",
        level="DEBUG"
    )
    
    logger.info("Logging initialized.")


def load_config():
    """
    Loads environment variables from .env and returns as a dict.
    """
    load_dotenv()
    config = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "UPLOAD_TARGET": os.getenv("UPLOAD_TARGET", "local"),
        # Add more as needed
    }
    return config
