import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from api.auth import router as auth_router
from api.tasks import router as tasks_router
from api.chat import router as chat_router
from core.middleware import add_exception_handlers

# Import database configuration
from database.config import create_db_and_tables

app = FastAPI(
    title="Todo API",
    description="API for the Todo application",
    version="1.0.0"
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://todoapp-frontend-lime.vercel.app/")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        FRONTEND_URL,
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
add_exception_handlers(app)

# Initialize database tables
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Routers
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
