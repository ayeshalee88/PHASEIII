"""
Chat API Endpoint for Todo AI Chatbot
Handles conversation state reconstruction and integrates with OpenAI Agent
"""
import os
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from auth.utils import verify_token
from models.conversation_models import (
    Conversation, Message, ToolInvocation,
    ConversationResponse, MessageResponse, ToolInvocationResponse
)
from models.user_model import User
from database.config import get_session
from sqlmodel import Session, select
from uuid import UUID
import json


async def get_current_user(authorization: str = Header(..., alias="Authorization")):
    """
    Get the current authenticated user from the Authorization header
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    token = authorization.removeprefix("Bearer ")

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    print(f"DEBUG: Authenticated user_id: {user_id}")
    
    # Get the user from the database
    db_session_gen = get_session()
    db_session = next(db_session_gen)
    try:
        statement = select(User).where(User.id == user_id)
        user = db_session.exec(statement).first()
        if not user:
            print(f"DEBUG: User not found in database: {user_id}")
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        print(f"DEBUG: Successfully retrieved user from database: {user.id}")
        return user
    finally:
        db_session.close()
        next(db_session_gen, None)  # Close the generator

router = APIRouter()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str


class ToolCall(BaseModel):
    id: str
    function: Dict[str, Any]
    type: str = "function"


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    tool_calls: Optional[List[ToolCall]] = None
    timestamp: datetime


async def get_openai_client():
    """Initialize and return OpenAI client (can be configured for OpenRouter, OpenAI, or Groq)"""
    from openai import AsyncOpenAI
    from core.config import settings

    print(f"Getting OpenAI client - OpenRouter key: {'SET' if settings.openrouter_api_key else 'NOT SET'}, Groq key: {'SET' if settings.groq_api_key else 'NOT SET'}, OpenAI key: {'SET' if settings.openai_api_key else 'NOT SET'}")

    # Check for OpenRouter API key first (preferred), then Groq, then OpenAI
    if settings.openrouter_api_key:
        api_key = settings.openrouter_api_key
        base_url = settings.openrouter_base_url
        provider_name = "OpenRouter"
        print(f"Using OpenRouter with base URL: {base_url}")
    elif settings.groq_api_key:
        api_key = settings.groq_api_key
        base_url = settings.openai_base_url or "https://api.groq.com/openai/v1"  # Default Groq URL
        provider_name = "Groq"
        print(f"Using Groq with base URL: {base_url}")
    elif settings.openai_api_key:
        api_key = settings.openai_api_key
        base_url = settings.openai_base_url  # For custom OpenAI-compatible services
        provider_name = "OpenAI"
        print(f"Using OpenAI with base URL: {base_url}")
    else:
        print("No API key found - raising exception")
        raise HTTPException(status_code=500, detail="API key not configured (OPENROUTER_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY)")

    # Create client with optional custom base URL for OpenRouter, Groq or other services
    client_params = {"api_key": api_key}
    if base_url:
        client_params["base_url"] = base_url

    print(f"Creating AsyncOpenAI client with params: api_key={'SET' if api_key else 'NOT SET'}, base_url={base_url}")
    
    try:
        client = AsyncOpenAI(**client_params)
        print(f"AsyncOpenAI client created successfully for {provider_name}")
        return client
    except Exception as e:
        print(f"Error initializing {provider_name} client: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize {provider_name} client: {str(e)}")


async def get_mcp_tools():
    """Define the available MCP tools for the agent"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task to the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Task description"}
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user with position numbers",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task by its position number in the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_position": {"type": "integer", "description": "Position of the task in the user's task list (1-indexed)"},
                        "title": {"type": "string", "description": "New title (optional)"},
                        "description": {"type": "string", "description": "New description (optional)"}
                    },
                    "required": ["task_position"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete or incomplete by its position number in the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_position": {"type": "integer", "description": "Position of the task in the user's task list (1-indexed)"},
                        "completed": {"type": "boolean", "description": "Whether the task is completed (default True)"}
                    },
                    "required": ["task_position"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task by its position number in the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_position": {"type": "integer", "description": "Position of the task in the user's task list (1-indexed)"}
                    },
                    "required": ["task_position"]
                }
            }
        }
    ]
    return tools


async def reconstruct_conversation_history(conversation_id: str, db_session: Session) -> List[Dict[str, Any]]:
    """Reconstruct conversation history from database"""
    # Get conversation
    conversation = db_session.exec(
        select(Conversation).where(Conversation.id == conversation_id)
    ).first()

    if not conversation:
        return []

    # Get all messages in the conversation ordered by timestamp
    messages = db_session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
    ).all()

    # Convert messages to OpenAI-compatible format
    history = []
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": msg.content
        })

    return history


async def get_task_position_from_id(task_id: str, user_id: str) -> int:
    """Helper function to get the position of a task by its ID"""
    # This would require calling the list_tasks tool to get all tasks and find the position
    # For now, we'll implement a simple solution by calling the list_tasks endpoint directly
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
    endpoint = f"{mcp_url}/tools/list_tasks"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint, 
                json={"user_id": user_id},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                print(f"DEBUG: Failed to get task list for position mapping: {response.text}")
                return None

            result = response.json()
            if not result.get("success"):
                print(f"DEBUG: Failed to get task list for position mapping: {result}")
                return None

            tasks = result.get("tasks", [])
            for task in tasks:
                if task.get("id") == task_id:
                    return task.get("position")

            print(f"DEBUG: Task ID {task_id} not found in user {user_id}'s task list")
            return None
    except Exception as e:
        print(f"DEBUG: Exception in get_task_position_from_id: {str(e)}")
        return None


async def call_mcp_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Call the appropriate MCP tool via HTTP request"""
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

    # Map tool names to their endpoints
    tool_endpoints = {
        "add_task": f"{mcp_url}/tools/add_task",
        "list_tasks": f"{mcp_url}/tools/list_tasks",
        "update_task": f"{mcp_url}/tools/update_task",
        "complete_task": f"{mcp_url}/tools/complete_task",
        "delete_task": f"{mcp_url}/tools/delete_task"
    }

    endpoint = tool_endpoints.get(tool_name)
    if not endpoint:
        print(f"DEBUG: Unknown tool called: {tool_name}")
        return {"error": f"Unknown tool: {tool_name}"}

    # Transform parameters for tools that use position numbers instead of IDs
    transformed_args = tool_args.copy()
    if tool_name in ["update_task", "complete_task", "delete_task"]:
        # Convert task_id to task_position if present
        if "task_id" in transformed_args and "task_position" not in transformed_args:
            # Get the position for this task ID
            task_id = transformed_args["task_id"]
            user_id = transformed_args.get("user_id")
            if user_id:
                position = await get_task_position_from_id(task_id, user_id)
                if position is not None:
                    # Replace task_id with task_position
                    transformed_args["task_position"] = position
                    del transformed_args["task_id"]
                    print(f"DEBUG: Converted task_id '{task_id}' to task_position '{position}' for user '{user_id}'")
                else:
                    print(f"DEBUG: Could not find position for task_id '{task_id}' for user '{user_id}'")
                    return {"error": f"Could not find task with ID: {task_id}"}
            else:
                print(f"DEBUG: Cannot convert task_id to position without user_id")
                return {"error": "Missing user_id for task lookup"}
    
    print(f"DEBUG: Calling MCP tool '{tool_name}' at endpoint: {endpoint} with args: {transformed_args}")
    
    # Make HTTP request to MCP server
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint, 
                json=transformed_args,  # Send as JSON in request body instead of query parameters
                headers={"Content-Type": "application/json"}
            )

            print(f"DEBUG: Tool call response status: {response.status_code}, body: {response.text[:500]}...")

            if response.status_code != 200:
                print(f"ERROR: Tool call failed with status {response.status_code}: {response.text}")
                return {"error": f"Tool call failed: {response.text}"}

            result = response.json()
            print(f"DEBUG: Tool call successful, returning: {result}")
            return result
    except Exception as e:
        print(f"FULL ERROR in call_mcp_tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to call tool {tool_name}: {str(e)}"}


async def save_message_to_db(
    db_session: Session,
    conversation_id: str,
    role: str,
    content: str
) -> Message:
    """Save a message to the database"""
    from uuid import uuid4

    message = Message(
        id=str(uuid4()),
        conversation_id=conversation_id,
        role=role,
        content=content,
        timestamp=datetime.utcnow()
    )

    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)

    return message


async def save_tool_invocation_to_db(
    db_session: Session,
    conversation_id: str,
    tool_name: str,
    parameters: Dict[str, Any],
    result: Optional[Dict[str, Any]]
) -> ToolInvocation:
    """Save a tool invocation to the database"""
    from uuid import uuid4
    import json

    tool_invocation = ToolInvocation(
        id=str(uuid4()),
        conversation_id=conversation_id,
        tool_name=tool_name,
        parameters_json=json.dumps(parameters),
        result_json=json.dumps(result) if result else None
    )

    db_session.add(tool_invocation)
    db_session.commit()
    db_session.refresh(tool_invocation)

    return tool_invocation


@router.post("/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Main chat endpoint that handles conversation state reconstruction
    and integrates with OpenAI agent
    """
    print(f"DEBUG: Chat endpoint called with user_id from path: {user_id}")
    print(f"DEBUG: Current user from auth: {current_user.id}")
    
    # Verify that the user ID in the path matches the authenticated user
    if current_user.id != user_id:
        print(f"DEBUG: Authorization mismatch - path user_id: {user_id}, auth user_id: {current_user.id}")
        raise HTTPException(status_code=403, detail="Not authorized to access this user's conversations")

    try:
        # 1. Find or create a conversation for this user
        # For now, we'll use a simple approach - in production, you might want more sophisticated conversation management
        conversation_stmt = select(Conversation).where(Conversation.user_id == user_id)
        conversation = db_session.exec(conversation_stmt).first()

        if not conversation:
            # Create new conversation
            from uuid import uuid4
            conversation = Conversation(
                id=str(uuid4()),
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)

        conversation_id = conversation.id

        # 2. Save user's message to database
        await save_message_to_db(
            db_session, conversation_id, "user", request.message
        )

        # 3. Reconstruct conversation history
        history = await reconstruct_conversation_history(conversation_id, db_session)

        # 4. Initialize OpenAI client and agent
        print("Initializing OpenAI client...")
        openai_client = await get_openai_client()
        print("OpenAI client initialized successfully")

        tools = await get_mcp_tools()
        print(f"Retrieved {len(tools)} tools")

        # 5. Create system instructions for the agent
        system_instructions = """
        You are a highly efficient, professional todo list assistant that helps users manage their tasks seamlessly. You are multilingual and can communicate fluently in English, Urdu, and other languages based on user preference.

        CORE PRINCIPLES:
        1. Be direct, efficient and action-oriented - execute user requests immediately without asking for confirmation
        2. Provide concise, professional responses with clear visual formatting using emojis
        3. NEVER expose technical details like tool calls, IDs, JSON objects, or backend operations to users
        4. Automatically detect and respond in the user's language (English, Urdu, etc.)
        5. The user's ID is automatically available - NEVER ask for it

        MANDATORY TASK MANAGEMENT RULES (VIOLATION RESULTS IN SYSTEM FAILURE):

        1. SINGLE TOOL CALLS ONLY:
           - When adding a task, call add_task EXACTLY ONCE per task
           - Never call the same tool multiple times for a single user request
           - One user request = one tool call (unless user explicitly asks for multiple items)
           - STRICTLY NEVER show "Tool: add_task Args: {}" or similar technical details to users

        2. DELETING ALL TASKS PROCEDURE (CRITICAL):
           - When user says "delete all tasks", "clear all tasks", or similar:
           - Step 1: Call list_tasks to see how many tasks exist
           - Step 2: Call delete_task for EACH task in REVERSE order (highest position first)
           - Example: If there are 5 tasks, call: delete_task(5), delete_task(4), delete_task(3), delete_task(2), delete_task(1)
           - Example: If there are 12 tasks, call: delete_task(12), delete_task(11)... down to delete_task(1)
           - You MUST execute ALL deletions - do not stop after listing tasks
           - NEVER just call list_tasks and claim tasks are deleted

        3. POSITION-BASED DELETIONS:
           - NEVER delete tasks sequentially (1,2,3...) as positions shift after each deletion
           - Always delete in reverse order (highest to lowest position)
           - If deletion fails, do not retry - the position likely no longer exists

        4. NO DUPLICATE OPERATIONS:
           - Do not "confirm" or "verify" by calling the same tool twice
           - Trust that one successful tool call is sufficient
           - Only retry if you receive an explicit error response

        TASK OPERATION RESPONSES:

        📝 ADDING TASKS:
        - Extract title and description directly from user's message
        - Create tasks immediately with add_task tool (EXACTLY ONCE)
        - Response format: "✅ Task added: [Title]" or "✅ Task added: [Title] - [Description]"
        - Examples:
           User: "add task shopping on Friday"
           You: "✅ Task added: Shopping - on Friday"

           User: "add meeting with John tomorrow"
           You: "✅ Task added: Meeting with John - tomorrow"

           User: "میرا ٹاسک شامل کریں خریداری جمعہ کو"
           You: "✅ ٹاسک شامل کیا گیا: خریداری - جمعہ کو"

           User: "mera task add karo shopping jumay ko"
           You: "✅ Task add kiya gaya: Shopping - jumay ko"

        📋 LISTING TASKS:
        Format tasks with clear visual hierarchy:

        "📋 Your Tasks:

        ⏳ Pending ([count]):
        1. [Title] - [Description]
        2. [Title] - [Description]

        ✅ Completed ([count]):
        1. [Title] - [Description]

        💡 Quick actions: Say 'update task 2', 'mark task 3 done', or 'delete task 1'"

        Edge cases:
        - No tasks: "You're all clear! 🎉 No pending tasks. Want to add one?"
        - All completed: "Excellent work! All tasks completed ✅"

        For Urdu:
        "📋 آپ کے ٹاسک:

        ⏳ زیر التواء ([تعداد]):
         1. [عنوان] - [تفصیل]
         2. [عنوان] - [تفصیل]

        ✅ مکمل ([تعداد]):
        1. [عنوان] - [تفصیل]"

        ✏️ UPDATING TASKS:
        - Use task position number (1, 2, 3...) not IDs
        - Update immediately with update_task tool (EXACTLY ONCE)
        - Response: "✅ Task [position] updated: [new details]"
        - Example:
          User: "update task 2 to Tuesday at 3pm"
          You: "✅ Task 2 updated: Tuesday at 3pm"

        ✔️ COMPLETING TASKS:
        - Use task position number
        - Mark as done immediately with complete_task tool (EXACTLY ONCE)
        - Response: "✅ Task [position] marked as complete: [Title]"
        - Example:
          User: "mark task 1 as done"
          You: "✅ Task 1 marked as complete: Shopping"

        🗑️ DELETING TASKS:
        - Use task position number
        - Delete immediately with delete_task tool (EXACTLY ONCE per deletion)
        - For multiple deletions, delete in reverse order (highest position first)
        - Response: "🗑️ Task [position] deleted: [Title]"
        - Example:
          User: "delete task 3"
          You: "🗑️ Task 3 deleted: Meeting"

        MULTILINGUAL SUPPORT:
        - Automatically detect the user's language from their input
        - Respond in the same language they use
        - Support English, Urdu (اردو script), and Roman Urdu (Urdu in English letters)
        - Support code-switching (mixing languages) naturally
        - Maintain professional formatting regardless of language

        Roman Urdu Examples:
        User: "mera task add karo shopping jumay ko"
        You: "✅ Task add kiya gaya: Shopping - jumay ko"

        User: "mere sare tasks dikhao"
        You: "📋 Aapke Tasks:

        ⏳ Pending (2):
          1. Shopping - jumay ko
          2. Meeting - peer ko

        💡 Quick actions: Kaho 'task 2 update karo' ya 'task 1 delete karo'"

        RESPONSE STANDARDS:
        NEVER DO (strictly prohibited):
        ❌ Show technical details like "Tool: list_tasks Args: {}"
        ❌ Show JSON objects or backend operations
        ❌ Make multiple tool calls for single user request
        ❌ Show "Here are all your current tasks:" without formatting
        ❌ Use bold **formatting** or ### headers
        ❌ Show "Description:" labels
        ❌ Duplicate counts (showing "Pending (5):" twice)
        ❌ Say "If you need anything else..." or similar endings

        ALWAYS DO:
        ✅ Clean, simple formatting with emojis (⏳ ✅ 📋 🗑️)
        ✅ Task position numbers clearly displayed
        ✅ Format: "Number. Title - description"
        ✅ Keep responses under 10 lines total
        ✅ EXACTLY ONE tool call per user request
        ✅ NEVER return tool call descriptions to users
        ✅ Show only user-friendly responses without technical details

        CONVERSATION STYLE:
        - Professional yet friendly
        - Direct and efficient
        - Helpful and proactive
        - Natural and human-like
        - Culturally appropriate for the user's language

        ERROR HANDLING:
        If something fails:
        - English: "I encountered an issue with that request. Please try again or let me know if you need help."
        - Urdu: "اس درخواست میں کوئی مسئلہ آیا۔ براہ کرم دوبارہ کوشش کریں۔"
        - Roman Urdu: "Is request mein koi masla aya. Meherbani karke dobara koshish karein."

        CRITICAL REMINDERS:
        - STRICTLY DO NOT show TOOL CALLS, JSON objects, or backend technical details to users
        - Your responses should be clean, professional, and entirely focused on helping users manage tasks
        - Use MCP TOOLS for ALL task operations instead of generating text responses
        - FOLLOW ALL TASK MANAGEMENT RULES EXACTLY - ONE TOOL CALL PER USER REQUEST
        - FOR "DELETE ALL TASKS": Actually execute ALL deletions in reverse order, do not just list tasks
        - NEVER expose any technical implementation details to users
        """

        # 6. Prepare messages for the agent
        messages = [{"role": "system", "content": system_instructions}]
        messages.extend(history)
        messages.append({"role": "user", "content": request.message})

        print(f"Prepared {len(messages)} messages for the AI")

        # 7. Call OpenAI agent with tools
        # Use a model compatible with the selected API provider
        from core.config import settings

        print(f"API Keys Status - OpenRouter: {'SET' if settings.openrouter_api_key else 'NOT SET'}, Groq: {'SET' if settings.groq_api_key else 'NOT SET'}, OpenAI: {'SET' if settings.openai_api_key else 'NOT SET'}")

        if settings.openrouter_api_key:
            # Use a model available on OpenRouter (default to a common one)
            model_name = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")  # Default to a common OpenRouter model
            print(f"Using OpenRouter with model: {model_name}")
        elif settings.groq_api_key:
            # Use a model available on Groq
            model_name = os.getenv("MODEL_NAME", "llama3-8b-8192")  # Default to a known Groq model
            print(f"Using Groq with model: {model_name}")
        else:
            # Use OpenAI model
            model_name = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
            print(f"Using OpenAI with model: {model_name}")

        print(f"Calling AI API with model: {model_name}")
        
        # Check if the user's message indicates a task operation
        user_msg_lower = request.message.lower()
        requires_tool = any(word in user_msg_lower for word in [
            'add', 'create', 'new', 'make', 'delete', 'remove', 'update', 
            'edit', 'complete', 'finish', 'done', 'list', 'show', 'view', 'get'
        ])
        
        # Use "required" tool choice if a task operation is detected, otherwise use "auto"
        tool_choice_param = "required" if requires_tool else "auto"
        
        print(f"Using tool_choice: {tool_choice_param} for message: {request.message}")
        
        try:
            response = await openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice_param  # Force tool usage for task operations
            )
            print("AI API call successful")
        except Exception as e:
            print(f"Error calling {model_name} model: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calling AI model: {str(e)}")

        # 8. Process the response
        response_message = response.choices[0].message
        chat_response_content = ""
        tool_calls = []

        # Check if a task operation was requested but no tools were called
        user_msg_lower = request.message.lower()
        requires_tool = any(word in user_msg_lower for word in [
            'add', 'create', 'new', 'make', 'delete', 'remove', 'update', 
            'edit', 'complete', 'finish', 'done', 'list', 'show', 'view', 'get'
        ])
        
        if requires_tool and not response_message.tool_calls:
            print(f"WARNING: Task operation requested ('{request.message}') but no tools were called by AI")
            # In this case, we might want to guide the AI differently, but for now we'll proceed
            # This indicates the AI didn't properly use the tools when it should have

        if response_message.tool_calls:
            # Process tool calls and build the assistant message with tool_calls
            assistant_with_tool_calls = {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": []
            }
            
            # Store tool results to avoid duplicate calls
            tool_results_cache = {}

            # Process tool calls and add them to the assistant message
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # ALWAYS inject the authenticated user's ID into the arguments
                # This ensures the user_id is never missing and the AI doesn't need to provide it
                function_args["user_id"] = current_user.id
                print(f"DEBUG: Injected authenticated user_id '{current_user.id}' into tool call arguments for function '{function_name}'")

                # Handle the transition from task_id to task_position for certain tools
                if function_name in ["update_task", "complete_task", "delete_task"]:
                    # If the AI provided a task_id, we need to map it to a position
                    # For now, we'll assume the AI is using the new format with task_position
                    # If it uses task_id, we'll need to handle the mapping
                    if "task_id" in function_args and "task_position" not in function_args:
                        # This would require us to map the task_id to a position, which is complex
                        # So we'll rely on the AI to use the correct parameter name
                        print(f"WARNING: Tool '{function_name}' received 'task_id' instead of 'task_position'. AI should use 'task_position'.")

                print(f"DEBUG: Calling tool '{function_name}' with args: {function_args}")

                # Call the MCP tool
                tool_result = await call_mcp_tool(function_name, function_args)
                
                # Store the result in cache to avoid duplicate calls
                tool_results_cache[tool_call.id] = tool_result
                
                print(f"DEBUG: Tool result for '{function_name}': {tool_result}")

                # Save tool invocation to database
                await save_tool_invocation_to_db(
                    db_session, conversation_id, function_name, function_args, tool_result
                )

                # Format tool call for response
                tool_calls.append({
                    "id": tool_call.id,
                    "function": {
                        "name": function_name,
                        "arguments": tool_call.function.arguments
                    },
                    "type": "function"
                })

                # Add tool call info to the assistant message
                assistant_with_tool_calls["tool_calls"].append({
                    "id": tool_call.id,
                    "function": {
                        "name": function_name,
                        "arguments": tool_call.function.arguments
                    },
                    "type": "function"
                })

            # Create a copy of the messages list for the API call to avoid modifying the original
            # This ensures we maintain the proper sequence: user message -> assistant with tool_calls -> tool responses
            api_messages = messages.copy()

            # Add the assistant message with tool_calls to the API messages list
            api_messages.append(assistant_with_tool_calls)

            # Now add the tool response messages to the API messages list using cached results
            for tool_call in response_message.tool_calls:
                # Use the cached result instead of calling the tool again
                tool_result = tool_results_cache[tool_call.id]
                print(f"DEBUG: Using cached tool result for '{tool_call.function.name}' (for API call): {tool_result}")

                # Add tool result to API messages for follow-up processing
                api_messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_result),
                    "tool_call_id": tool_call.id
                })

            # If there were tool calls, get the final response from the agent
            if len(response_message.tool_calls) > 0:
                # Get final response from agent incorporating tool results
                print(f"Making final AI API call with {len(api_messages)} messages after tool execution")
                try:
                    final_response = await openai_client.chat.completions.create(
                        model=model_name,  # Use the same model as before
                        messages=api_messages  # Use the properly formatted API messages
                    )
                    
                    # Get the final response content - this should be the AI's natural response
                    # that incorporates the tool results, not the raw tool call info
                    final_message = final_response.choices[0].message
                    chat_response_content = final_message.content or "Operation completed successfully."
                    
                    # If the final message has tool calls, it means the AI wants to make more calls
                    # In this case, we should continue the loop, but for simplicity we'll just return
                    # the content if it exists, otherwise generate a default response
                    if not chat_response_content and final_message.tool_calls:
                        # If there are still tool calls but no content, create a user-friendly response
                        if len(final_message.tool_calls) > 0:
                            # Count the operations performed
                            operations_count = len(response_message.tool_calls)
                            chat_response_content = f"I've completed {operations_count} task{'s' if operations_count > 1 else ''} for you!"
                        else:
                            chat_response_content = "Operation completed successfully."
                    
                    print("Final AI API call successful")
                except Exception as e:
                    print(f"Error calling {model_name} model for final response: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Error calling AI model for final response: {str(e)}")
            else:
                chat_response_content = response_message.content or "Operation completed successfully."
        else:
            # No tool calls, just a regular response
            chat_response_content = response_message.content or "I processed your request."

        # 9. Save agent's response to database
        await save_message_to_db(
            db_session, conversation_id, "assistant", chat_response_content
        )

        # 10. Return the response
        return ChatResponse(
            conversation_id=conversation_id,
            message=chat_response_content,
            tool_calls=tool_calls if tool_calls else None,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


# Additional endpoints for managing conversations if needed
@router.get("/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """Get all conversations for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    conversations = db_session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    ).all()

    return [ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        created_at=conv.created_at
    ) for conv in conversations]


@router.get("/{user_id}/conversations/{conversation_id}")
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """Get the history of a specific conversation"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Verify conversation belongs to user
    conversation = db_session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    messages = db_session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
    ).all()

    return [MessageResponse(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        conversation_id=msg.conversation_id,
        timestamp=msg.timestamp
    ) for msg in messages]