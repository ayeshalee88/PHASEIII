from fastapi import HTTPException, status

class TodoException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class UserNotFoundException(TodoException):
    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User with id {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class TaskNotFoundException(TodoException):
    def __init__(self, task_id: str):
        super().__init__(
            detail=f"Task with id {task_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class UnauthorizedAccessException(TodoException):
    def __init__(self):
        super().__init__(
            detail="Unauthorized access",
            status_code=status.HTTP_403_FORBIDDEN
        )

class DuplicateEmailException(TodoException):
    def __init__(self):
        super().__init__(
            detail="A user with this email already exists",
            status_code=status.HTTP_400_BAD_REQUEST
        )

class InvalidCredentialsException(TodoException):
    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )