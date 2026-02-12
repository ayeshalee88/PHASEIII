"""
Main entry point for the Todo API backend server
"""
from src.app import app
import uvicorn
import sys
import os

# Add the backend directory to the Python path to ensure all imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_dirs=["."],  # Reload when files in current directory change
        log_level="info"
    )