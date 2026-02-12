from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from core.exceptions import TodoException

async def todo_exception_handler(request: Request, exc: TodoException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

def add_exception_handlers(app):
    app.add_exception_handler(TodoException, todo_exception_handler)
    return app