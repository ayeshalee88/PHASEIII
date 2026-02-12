"""
MCP Server for Todo AI Chatbot
Exposes task operations as tools for OpenAI Agents
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime
from shared_database import get_session, get_direct_session
from backend.models.task_models import Task, TaskCreate, TaskUpdate, TaskResponse


class ChatRequest(BaseModel):
    message: str
    userId: str


class AddTaskRequest(BaseModel):
    title: str
    description: str = ""
    user_id: str


class ListTasksRequest(BaseModel):
    user_id: str


class UpdateTaskRequest(BaseModel):
    task_position: int
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None


class CompleteTaskRequest(BaseModel):
    task_position: int
    user_id: str
    completed: bool = True


class DeleteTaskRequest(BaseModel):
    task_position: int
    user_id: str


# Use lifespan without table creation
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # No database initialization needed - backend handles it


app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add this to handle preflight requests properly
    max_age=3600,  # Cache preflight requests for 1 hour
)

def get_user_tasks(user_id: str) -> List[Task]:
    """Get all tasks for a specific user"""
    with next(get_session()) as session:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        return tasks


def get_task_by_position(user_id: str, position: int) -> Tuple[Task, int]:
    """Get a specific task by its position in the user's task list (1-indexed)"""
    with next(get_session()) as session:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()

        if position < 1 or position > len(tasks):
            raise HTTPException(status_code=404, detail=f"Task at position {position} not found")

        # Return the task at the specified position (1-indexed) and its actual index
        return tasks[position - 1], position - 1


def get_task_by_id(task_id: str, user_id: str) -> Task:
    """Get a specific task for a user"""
    with next(get_session()) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        return task


@app.post("/tools/add_task")
async def add_task_tool(request: AddTaskRequest) -> Dict[str, Any]:
    """
    Add a new task
    Args:
        request: Contains title, description, and user_id
    Returns:
        Created task object
    """
    print(f"DEBUG: add_task_tool called with - title: '{request.title}', description: '{request.description}', user_id: '{request.user_id}'")

    if not request.title or not request.title.strip():
        print(f"DEBUG: Validation failed - title is empty or blank")
        raise HTTPException(status_code=400, detail="Title is required")

    if not request.user_id:
        print(f"DEBUG: Validation failed - user_id is empty")
        raise HTTPException(status_code=400, detail="User ID is required")

    print(f"DEBUG: Attempting to create task for user_id: '{request.user_id}'")

    # Use the generator properly with next() and ensure proper cleanup
    session_gen = get_session()
    session = next(session_gen)
    try:
        # Create the task
        db_task = Task(
            title=request.title,
            description=request.description,
            user_id=request.user_id,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        print(f"DEBUG: Task created successfully - ID: {db_task.id}, Title: '{db_task.title}', User ID: '{db_task.user_id}'")

        # Convert to response format
        task_response = TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            user_id=db_task.user_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )

        return {"success": True, "task": task_response.dict()}
    except Exception as e:
        print(f"FULL ERROR in add_task_tool: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
    finally:
        # Properly close the generator to trigger the finally block in get_session
        try:
            next(session_gen)
        except StopIteration:
            pass


@app.post("/tools/list_tasks")
async def list_tasks_tool(request: ListTasksRequest) -> Dict[str, Any]:
    """
    List all tasks for a user
    Args:
        request: Contains user_id to filter tasks
    Returns:
        List of tasks with position numbers and summary statistics
    """
    print(f"DEBUG: list_tasks_tool called with user_id: '{request.user_id}'")

    if not request.user_id:
        print(f"DEBUG: Validation failed - user_id is empty")
        raise HTTPException(status_code=400, detail="User ID is required")

    # Use the generator properly with next() and ensure proper cleanup
    session_gen = get_session()
    session = next(session_gen)
    try:
        statement = select(Task).where(Task.user_id == request.user_id)
        tasks = session.exec(statement).all()
        
        print(f"DEBUG: Found {len(tasks)} tasks for user_id: '{request.user_id}'")

        # Separate tasks by completion status
        pending_tasks = []
        completed_tasks = []

        for idx, task in enumerate(tasks, 1):
            task_data = TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                user_id=task.user_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            ).dict()
            # Add position number to the task data
            task_data['position'] = idx

            if task.completed:
                completed_tasks.append(task_data)
            else:
                pending_tasks.append(task_data)

        # Convert tasks to response format with position numbers
        task_list = []
        for task in pending_tasks:
            task_list.append(task)
        for task in completed_tasks:
            task_list.append(task)

        print(f"DEBUG: Returning {len(task_list)} tasks with {len(pending_tasks)} pending and {len(completed_tasks)} completed")

        # Return structured data with summary information
        return {
            "success": True,
            "tasks": task_list,
            "summary": {
                "total": len(tasks),
                "pending": len(pending_tasks),
                "completed": len(completed_tasks)
            },
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks
        }
    except Exception as e:
        print(f"FULL ERROR in list_tasks_tool: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")
    finally:
        # Properly close the generator to trigger the finally block in get_session
        try:
            next(session_gen)
        except StopIteration:
            pass


@app.post("/tools/update_task")
async def update_task_tool(request: UpdateTaskRequest) -> Dict[str, Any]:
    """
    Update an existing task by position
    Args:
        request: Contains task_position, user_id, title (optional), and description (optional)
    Returns:
        Updated task object
    """
    print(f"DEBUG: update_task_tool called with task_position: {request.task_position}, user_id: '{request.user_id}', title: '{request.title}', description: '{request.description}'")

    if not request.user_id:
        print(f"DEBUG: Validation failed - user_id is empty")
        raise HTTPException(status_code=400, detail="User ID is required")

    if request.title is None and request.description is None:
        print(f"DEBUG: Validation failed - no fields to update")
        raise HTTPException(status_code=400, detail="At least one field (title or description) must be provided for update")

    # Use the generator properly with next() and ensure proper cleanup
    session_gen = get_session()
    session = next(session_gen)
    try:
        # Get all tasks for the user to find the one at the specified position
        statement = select(Task).where(Task.user_id == request.user_id)
        tasks = session.exec(statement).all()

        if request.task_position < 1 or request.task_position > len(tasks):
            raise HTTPException(status_code=404, detail=f"Task at position {request.task_position} not found")

        # Get the task at the specified position (1-indexed)
        db_task = tasks[request.task_position - 1]

        print(f"DEBUG: Found task at position {request.task_position}, actual task ID: {db_task.id}")

        # Update the task
        if request.title is not None:
            db_task.title = request.title
        if request.description is not None:
            db_task.description = request.description

        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Convert to response format
        task_response = TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            user_id=db_task.user_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )

        print(f"DEBUG: Task updated successfully - ID: {db_task.id}, Position: {request.task_position}")
        return {"success": True, "task": task_response.dict()}
    except Exception as e:
        print(f"FULL ERROR in update_task_tool: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
    finally:
        # Properly close the generator to trigger the finally block in get_session
        try:
            next(session_gen)
        except StopIteration:
            pass


@app.post("/tools/complete_task")
async def complete_task_tool(request: CompleteTaskRequest) -> Dict[str, Any]:
    """
    Mark a task as complete or incomplete by position
    Args:
        request: Contains task_position, user_id, and completed status
    Returns:
        Updated task object
    """
    print(f"DEBUG: complete_task_tool called with task_position: {request.task_position}, user_id: '{request.user_id}', completed: {request.completed}")

    if not request.user_id:
        print(f"DEBUG: Validation failed - user_id is empty")
        raise HTTPException(status_code=400, detail="User ID is required")

    # Use the generator properly with next() and ensure proper cleanup
    session_gen = get_session()
    session = next(session_gen)
    try:
        # Get all tasks for the user to find the one at the specified position
        statement = select(Task).where(Task.user_id == request.user_id)
        tasks = session.exec(statement).all()

        if request.task_position < 1 or request.task_position > len(tasks):
            raise HTTPException(status_code=404, detail=f"Task at position {request.task_position} not found")

        # Get the task at the specified position (1-indexed)
        db_task = tasks[request.task_position - 1]
        print(f"DEBUG: Found task at position {request.task_position}, actual task ID: {db_task.id}")

        # Update completion status
        db_task.completed = request.completed
        db_task.updated_at = datetime.utcnow()

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Convert to response format
        task_response = TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            user_id=db_task.user_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )

        print(f"DEBUG: Task completion status updated successfully - ID: {db_task.id}, Position: {request.task_position}, Completed: {request.completed}")
        return {"success": True, "task": task_response.dict()}
    except Exception as e:
        print(f"FULL ERROR in complete_task_tool: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating task completion: {str(e)}")
    finally:
        # Properly close the generator to trigger the finally block in get_session
        try:
            next(session_gen)
        except StopIteration:
            pass


@app.post("/tools/delete_task")
async def delete_task_tool(request: DeleteTaskRequest) -> Dict[str, Any]:
    """
    Delete a task by position
    Args:
        request: Contains task_position and user_id
    Returns:
        Success confirmation
    """
    print(f"DEBUG: delete_task_tool called with task_position: {request.task_position}, user_id: '{request.user_id}'")

    if not request.user_id:
        print(f"DEBUG: Validation failed - user_id is empty")
        raise HTTPException(status_code=400, detail="User ID is required")

    # Use the generator properly with next() and ensure proper cleanup
    session_gen = get_session()
    session = next(session_gen)
    try:
        # Get all tasks for the user to find the one at the specified position
        statement = select(Task).where(Task.user_id == request.user_id)
        tasks = session.exec(statement).all()

        if request.task_position < 1 or request.task_position > len(tasks):
            raise HTTPException(status_code=404, detail=f"Task at position {request.task_position} not found")

        # Get the task at the specified position (1-indexed)
        db_task = tasks[request.task_position - 1]
        task_id = db_task.id
        print(f"DEBUG: Found task at position {request.task_position}, actual task ID: {task_id}")

        # Delete the task
        session.delete(db_task)
        session.commit()

        print(f"DEBUG: Task deleted successfully - ID: {task_id}, Position: {request.task_position}")
        return {"success": True, "message": f"Task at position {request.task_position} deleted successfully"}
    except Exception as e:
        print(f"FULL ERROR in delete_task_tool: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")
    finally:
        # Properly close the generator to trigger the finally block in get_session
        try:
            next(session_gen)
        except StopIteration:
            pass


# Health check endpoint for debugging
@app.get("/health")
async def health_check():
    from shared_database import get_current_engine
    engine = get_current_engine()
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table";'))
        tables = [row[0] for row in result]
    return {"status": "healthy", "database_url": str(engine.url), "tables": tables}

# Define the available tools for the AI agent
def get_available_tools():
    """Return the list of available tools for the AI agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "The task title"},
                        "description": {"type": "string", "description": "The task description"},
                        "user_id": {"type": "string", "description": "The user's ID"}
                    },
                    "required": ["title", "user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The task ID to update"},
                        "title": {"type": "string", "description": "The new task title"},
                        "description": {"type": "string", "description": "The new task description"},
                        "completed": {"type": "boolean", "description": "Whether the task is completed"},
                        "user_id": {"type": "string", "description": "The user's ID"}
                    },
                    "required": ["task_id", "user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The task ID to delete"},
                        "user_id": {"type": "string", "description": "The user's ID"}
                    },
                    "required": ["task_id", "user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Get all tasks for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "toggle_task_completion",
                "description": "Mark a task as complete or incomplete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "The task ID to update"},
                        "completed": {"type": "boolean", "description": "Whether the task is completed"},
                        "user_id": {"type": "string", "description": "The user's ID"}
                    },
                    "required": ["task_id", "completed", "user_id"]
                }
            }
        }
    ]


@app.post("/api/chat")
async def chat_endpoint(
    request: ChatRequest,
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Chat endpoint for AI interactions
    Args:
        request: Contains message and userId
        authorization: Authorization header (optional)
    Returns:
        AI response with potential tool calls
    """
    print(f"DEBUG: chat_endpoint called with message: '{request.message}', userId: '{request.userId}', auth: {authorization}")

    try:
        user_message_lower = request.message.lower()
        
        # Determine if the user wants to perform a task operation
        response_data = {
            "conversation_id": f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.userId}",
            "message": "",
            "tool_calls": [],  # Will be populated with actual tool call structures
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Simple rule-based detection of task operations
        if any(word in user_message_lower for word in ["add", "create", "new"]):
            # Extract task title from message
            import re
            # Look for task title after action words
            match = re.search(r'(?:add|create|new)\s+(?:a\s+)?(?:task\s+)?"?([^"]+)"?', request.message, re.IGNORECASE)
            if match:
                task_title = match.group(1).strip()
                
                # Create a tool call structure for the frontend to process
                tool_call = {
                    "id": f"call_create_{datetime.utcnow().strftime('%H%M%S%f')}",
                    "function": {
                        "name": "create_task",
                        "arguments": json.dumps({
                            "title": task_title,
                            "description": "",
                            "user_id": request.userId
                        })
                    },
                    "type": "function"
                }
                
                response_data["tool_calls"].append(tool_call)
                response_data["message"] = f"I'll create a task for you: '{task_title}'"
            else:
                response_data["message"] = "What would you like to name your new task?"
        
        elif any(word in user_message_lower for word in ["view", "see", "list", "show", "my"]):
            # Create a tool call structure for getting tasks
            tool_call = {
                "id": f"call_get_{datetime.utcnow().strftime('%H%M%S%f')}",
                "function": {
                    "name": "get_tasks",
                    "arguments": json.dumps({
                        "user_id": request.userId
                    })
                },
                "type": "function"
            }
            
            response_data["tool_calls"].append(tool_call)
            response_data["message"] = "I'll show you your tasks."
        
        elif any(word in user_message_lower for word in ["complete", "done", "finish"]):
            # Look for task reference in message
            import re
            # Look for task identifier after completion words
            match = re.search(r'(?:complete|done|finish)\s+(?:task\s+)?(?:number\s+|#)?(\d+|"[^"]+"|\w+)', request.message, re.IGNORECASE)
            if match:
                task_ref = match.group(1).strip()
                
                # For simplicity, we'll assume the user wants to mark the first task as complete
                # In a real implementation, you'd need to map the reference to a specific task ID
                all_tasks = get_user_tasks(request.userId)
                
                if all_tasks:
                    # Find the first pending task
                    pending_task = None
                    for task in all_tasks:
                        if not task.completed:
                            pending_task = task
                            break
                    
                    if pending_task:
                        # Create a tool call structure for toggling task completion
                        tool_call = {
                            "id": f"call_toggle_{datetime.utcnow().strftime('%H%M%S%f')}",
                            "function": {
                                "name": "toggle_task_completion",
                                "arguments": json.dumps({
                                    "task_id": pending_task.id,
                                    "user_id": request.userId,
                                    "completed": True
                                })
                            },
                            "type": "function"
                        }
                        
                        response_data["tool_calls"].append(tool_call)
                        response_data["message"] = f"I'll mark '{pending_task.title}' as complete!"
                    else:
                        response_data["message"] = "You don't have any pending tasks to complete."
                else:
                    response_data["message"] = "You don't have any tasks to complete."
            else:
                response_data["message"] = "Which task would you like to mark as complete?"
        
        elif any(word in user_message_lower for word in ["delete", "remove"]):
            # Look for task reference in message
            import re
            match = re.search(r'(?:delete|remove)\s+(?:task\s+)?(?:number\s+|#)?(\d+|"[^"]+"|\w+)', request.message, re.IGNORECASE)
            if match:
                task_ref = match.group(1).strip()
                
                # For simplicity, we'll assume the user wants to delete the first task
                # In a real implementation, you'd need to map the reference to a specific task ID
                all_tasks = get_user_tasks(request.userId)
                
                if all_tasks:
                    # Use the first task
                    task_to_delete = all_tasks[0]
                    
                    # Create a tool call structure for deleting the task
                    tool_call = {
                        "id": f"call_delete_{datetime.utcnow().strftime('%H%M%S%f')}",
                        "function": {
                            "name": "delete_task",
                            "arguments": json.dumps({
                                "task_id": task_to_delete.id,
                                "user_id": request.userId
                            })
                        },
                        "type": "function"
                    }
                    
                    response_data["tool_calls"].append(tool_call)
                    response_data["message"] = f"I'll delete the task '{task_to_delete.title}'!"
                else:
                    response_data["message"] = "You don't have any tasks to delete."
            else:
                response_data["message"] = "Which task would you like to delete?"
        
        elif any(greeting in user_message_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            response_data["message"] = "Hello! I'm your AI assistant for managing tasks. You can ask me to add, view, update, or complete tasks."
        else:
            response_data["message"] = "I'm here to help you manage your tasks. You can ask me to add, view, update, or complete tasks."
        
        # Format response to be cleaner
        if response_data["tool_calls"]:
            # If there are tool calls, return a cleaner response
            return {
                "conversation_id": response_data["conversation_id"],
                "message": response_data["message"],
                "tool_calls": response_data["tool_calls"],
                "timestamp": response_data["timestamp"]
            }
        else:
            # If no tool calls, just return the message
            return {
                "conversation_id": response_data["conversation_id"],
                "message": response_data["message"],
                "timestamp": response_data["timestamp"]
            }

    except Exception as e:
        print(f"FULL ERROR in chat_endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/api/execute_tool")
async def execute_tool(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a specific tool call
    Args:
        request: Contains tool name and arguments
    Returns:
        Result of the tool execution
    """
    try:
        tool_name = request.get("name")
        arguments_str = request.get("arguments", "{}")
        
        # Parse the arguments string as JSON
        import json
        arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
        
        print(f"DEBUG: Executing tool '{tool_name}' with arguments: {arguments}")
        
        if tool_name == "create_task":
            # Call the add_task_tool function
            request_obj = AddTaskRequest(
                title=arguments.get("title", ""),
                description=arguments.get("description", ""),
                user_id=arguments.get("user_id")
            )
            result = await add_task_tool(request_obj)
            # Return cleaner output
            if result.get("success"):
                task = result.get("task", {})
                return {"result": f"✅ Task added: {task.get('title', 'Untitled Task')}"}
            else:
                return {"result": f"❌ Failed to add task: {result.get('detail', 'Unknown error')}"}
            
        elif tool_name == "get_tasks":
            # Call the list_tasks_tool function
            request_obj = ListTasksRequest(user_id=arguments.get("user_id"))
            result = await list_tasks_tool(request_obj)
            # Return cleaner output
            if result.get("success"):
                tasks = result.get("tasks", [])
                pending_count = result.get("summary", {}).get("pending", 0)
                completed_count = result.get("summary", {}).get("completed", 0)
                
                if tasks:
                    task_list = []
                    for task in tasks:
                        status = "✅" if task.get("completed") else "📝"
                        task_list.append(f"{status} {task.get('position', '')}. {task.get('title', 'Untitled Task')}")
                    
                    return {
                        "result": f"You have {len(tasks)} tasks:\n" + "\n".join(task_list) + 
                                 f"\n\nSummary: {pending_count} pending, {completed_count} completed"
                    }
                else:
                    return {"result": "You don't have any tasks yet."}
            else:
                return {"result": f"❌ Failed to retrieve tasks: {result.get('detail', 'Unknown error')}"}
            
        elif tool_name == "update_task":
            # For update_task, we need to find the actual task ID first
            # This is a simplified implementation - in reality, you'd need to map the task reference to an ID
            user_id = arguments.get("user_id")
            task_id = arguments.get("task_id")

            # If we have a task_id, we need to find its position
            if task_id and user_id:
                # Get all tasks for the user to find the position of the specified task
                with next(get_session()) as session:
                    statement = select(Task).where(Task.user_id == user_id)
                    all_tasks = session.exec(statement).all()

                    task_position = None
                    for idx, task in enumerate(all_tasks, 1):
                        if task.id == task_id:
                            task_position = idx
                            break

                    if task_position:
                        request_obj = UpdateTaskRequest(
                            task_position=task_position,
                            user_id=user_id,
                            title=arguments.get("title"),
                            description=arguments.get("description")
                        )
                        result = await update_task_tool(request_obj)
                        # Return cleaner output
                        if result.get("success"):
                            task = result.get("task", {})
                            return {"result": f"✅ Task updated: {task.get('title', 'Untitled Task')}"}
                        else:
                            return {"result": f"❌ Failed to update task: {result.get('detail', 'Unknown error')}"}
                    else:
                        return {"result": "❌ Task not found"}
            else:
                return {"result": "❌ Missing user_id or task_id"}
            
        elif tool_name == "toggle_task_completion":
            # For toggle_task_completion, we need to find the actual task ID first
            user_id = arguments.get("user_id")
            task_id = arguments.get("task_id")
            completed = arguments.get("completed", True)

            # If we have a task_id, we need to find its position
            if task_id and user_id:
                # Get all tasks for the user to find the position of the specified task
                with next(get_session()) as session:
                    statement = select(Task).where(Task.user_id == user_id)
                    all_tasks = session.exec(statement).all()

                    task_position = None
                    for idx, task in enumerate(all_tasks, 1):
                        if task.id == task_id:
                            task_position = idx
                            break

                    if task_position:
                        request_obj = CompleteTaskRequest(
                            task_position=task_position,
                            user_id=user_id,
                            completed=completed
                        )
                        result = await complete_task_tool(request_obj)
                        # Return cleaner output
                        if result.get("success"):
                            task = result.get("task", {})
                            status = "completed" if completed else "marked as incomplete"
                            return {"result": f"✅ Task {status}: {task.get('title', 'Untitled Task')}"}
                        else:
                            return {"result": f"❌ Failed to update task: {result.get('detail', 'Unknown error')}"}
                    else:
                        return {"result": "❌ Task not found"}
            else:
                return {"result": "❌ Missing user_id or task_id"}
            
        elif tool_name == "delete_task":
            # For delete_task, we need to find the actual task ID first
            user_id = arguments.get("user_id")
            task_id = arguments.get("task_id")

            # If we have a task_id, we need to find its position
            if task_id and user_id:
                # Get all tasks for the user to find the position of the specified task
                with next(get_session()) as session:
                    statement = select(Task).where(Task.user_id == user_id)
                    all_tasks = session.exec(statement).all()

                    task_position = None
                    for idx, task in enumerate(all_tasks, 1):
                        if task.id == task_id:
                            task_position = idx
                            break

                    if task_position:
                        request_obj = DeleteTaskRequest(
                            task_position=task_position,
                            user_id=user_id
                        )
                        result = await delete_task_tool(request_obj)
                        # Return cleaner output
                        if result.get("success"):
                            return {"result": f"✅ Task deleted successfully!"}
                        else:
                            return {"result": f"❌ Failed to delete task: {result.get('detail', 'Unknown error')}"}
                    else:
                        return {"result": "❌ Task not found"}
            else:
                return {"result": "❌ Missing user_id or task_id"}
            
        else:
            return {"error": f"Unknown tool: {tool_name}", "success": False}
            
    except Exception as e:
        print(f"ERROR executing tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"result": f"❌ Error executing tool: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)