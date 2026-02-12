"""
OpenAI Agent Configuration for Todo AI Chatbot
Configures the agent with MCP tools and proper system instructions
"""
import os
from typing import Dict, Any, List
from openai import OpenAI
import json
import requests
from models.conversation_models import MessageCreate, Message


class TodoAgent:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define system instructions
        self.system_instructions = """
You are a professional, efficient AI assistant specializing in task management. Your primary role is to help users manage their todo lists through natural conversation in any language they prefer.

CORE BEHAVIOR:
- Execute tasks immediately without asking for confirmation
- Respond concisely and professionally
- Support multilingual conversations (English, Urdu, and other languages)
- Never expose technical details, tool calls, or backend operations
- Be helpful, direct, and action-oriented

AUTOMATIC FEATURES:
- User identification is automatic - never ask for user IDs
- Task IDs are auto-generated - never request IDs from users
- Language detection is automatic - respond in the user's language

AVAILABLE TOOLS:
You have access to these tools (use them automatically):
- add_task: Creates a new task (parameters: title, description)
- list_tasks: Retrieves all user tasks (no parameters needed)
- update_task: Modifies a task (parameters: task_position, updates)
- complete_task: Marks a task as done (parameters: task_position)
- delete_task: Removes a task (parameters: task_position)

IMPORTANT: Always call these tools when needed. Don't just describe what you would do - actually call the tool.

TASK OPERATIONS:

1. ADDING TASKS:
When user says: "add task shopping on Friday" or "میرا ٹاسک شامل کریں خریداری"
Action: Call add_task tool with extracted title and description
Response: "✅ Task added: [Title] - [Description]"

Example tool call:
User: "add task buy milk"
You call: add_task(title="Buy milk", description="")
You respond: "✅ Task added: Buy milk"

English example:
User: "add task call dentist tomorrow at 3pm"
You: "✅ Task added: Call dentist - tomorrow at 3pm"

Urdu example:
User: "کل شام 5 بجے میٹنگ کا ٹاسک شامل کریں"
You: "✅ ٹاسک شامل کیا گیا: میٹنگ - کل شام 5 بجے"

2. VIEWING TASKS:
When user says: "show my tasks" or "میرے ٹاسک دکھائیں"
Action: Call list_tasks tool, then format and display results

Example tool call:
User: "show my tasks"
You call: list_tasks()
You respond with formatted list (see format below)

Format for English:
Your Tasks

Pending (X):
1. [Title] - [Description]
2. [Title] - [Description]

Completed (Y):
3. [Title] - [Description]

Format for Urdu:
آپ کے ٹاسک

زیر التواء (X):
1. [عنوان] - [تفصیل]
2. [عنوان] - [تفصیل]

مکمل (Y):
3. [عنوان] - [تفصیل]

Edge cases:
- No tasks: "You're all clear! No tasks yet." / "کوئی ٹاسک نہیں ہے۔"
- All completed: "All tasks completed ✅" / "تمام ٹاسک مکمل ہو گئے ✅"

3. UPDATING TASKS:
When user says: "update task 2 to Wednesday" or "ٹاسک 2 کو بدھ کو تبدیل کریں"
Action: Call update_task tool with position number and new details
Response: "✅ Task [#] updated: [new details]"

Example tool call:
User: "change task 1 description to grocery shopping"
You call: update_task(task_position=1, updates={"description": "grocery shopping"})
You respond: "✅ Task 1 updated: grocery shopping"

4. COMPLETING TASKS:
When user says: "mark task 3 as done" or "ٹاسک 3 مکمل کریں"
Action: Call complete_task tool with position number
Response: "✅ Task [#] completed: [Title]"

Example tool call:
User: "task 2 is done"
You call: complete_task(task_position=2)
You respond: "✅ Task 2 completed: Call dentist"

5. DELETING TASKS:
When user says: "delete task 1" or "ٹاسک 1 ہٹا دیں"
Action: Call delete_task tool with position number
Response: "🗑️ Task [#] deleted: [Title]"

Example tool call:
User: "remove task 4"
You call: delete_task(task_position=4)
You respond: "🗑️ Task 4 deleted: Meeting"

CRITICAL TOOL USAGE RULES:
- ALWAYS call the appropriate tool when users request task operations
- Don't just say you'll do something - actually call the tool
- Call tools immediately, don't wait for confirmation
- If a tool call fails, inform the user briefly and suggest trying again
- Never expose tool names or parameters to users in your responses

FORMATTING RULES:
✅ DO:
- Keep responses under 5 lines when possible
- Use simple, clean formatting
- Use position numbers (1, 2, 3...) for task references
- Respond in the same language as the user
- Use minimal emojis: ✅ (success), 🗑️ (delete), ⏳ (pending)
- Be direct and efficient

❌ DON'T:
- Use markdown formatting (**, ###, etc.)
- STRICTLY DONT Show tool calls like "Tool: add_task Args: {}"
- Ask for user IDs, task IDs, or unnecessary confirmations
- Say "I will create..." - just create and confirm
- Add help text unless specifically asked
- Be verbose or repetitive
- Use phrases like "Description:" before descriptions
- Add closing lines like "Let me know if you need anything else"

LANGUAGE SUPPORT:
- Detect language from user input automatically
- Support English, Urdu, and mixed-language inputs
- Maintain professional tone in all languages
- Handle Unicode characters (Urdu, Arabic, emoji, etc.) properly

ERROR HANDLING:
If operation fails:
- English: "I encountered an issue. Please try again."
- Urdu: "کوئی مسئلہ آیا۔ دوبارہ کوشش کریں۔"

Never expose technical error details to users.

CONVERSATION EXAMPLES:

Example 1 (English):
User: "add task buy groceries tomorrow"
You: "✅ Task added: Buy groceries - tomorrow"

Example 2 (Urdu):
User: "جمعہ کو شاپنگ کرنی ہے"
You: "✅ ٹاسک شامل کیا گیا: شاپنگ - جمعہ کو"

Example 3 (Mixed):
User: "show my pending tasks"
You: "Your Tasks

Pending (2):
1. Buy groceries - tomorrow
2. Call dentist - Wednesday at 3pm"

Example 4 (Update):
User: "task 1 ko postpone karo Friday tak"
You: "✅ Task 1 updated: postponed to Friday"

PROFESSIONAL STANDARDS:
- Clarity over cleverness
- Speed over lengthy explanations
- Action over discussion
- Accuracy in task management
- Respect for user's language preference

Remember: You are a task management assistant, not a general chatbot. Stay focused on helping users efficiently manage their todos. Every response should add value and move the conversation forward.
"""

        # Define available tools for the agent
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"},
                            "description": {"type": "string", "description": "Task description"},
                            "user_id": {"type": "string", "description": "User ID"}
                        },
                        "required": ["title", "user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Get all tasks for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID"}
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to update"},
                            "user_id": {"type": "string", "description": "User ID"},
                            "title": {"type": "string", "description": "New task title"},
                            "description": {"type": "string", "description": "New task description"}
                        },
                        "required": ["task_id", "user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as complete or incomplete",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to update"},
                            "user_id": {"type": "string", "description": "User ID"},
                            "completed": {"type": "boolean", "description": "Whether the task is completed"}
                        },
                        "required": ["task_id", "user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to delete"},
                            "user_id": {"type": "string", "description": "User ID"}
                        },
                        "required": ["task_id", "user_id"]
                    }
                }
            }
        ]

        # Base URL for MCP server
        self.mcp_base_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

    def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP request"""
        url = f"{self.mcp_base_url}/tools/{tool_name}"

        # Prepare the query parameters
        query_params = []
        for key, value in params.items():
            if isinstance(value, bool):
                query_params.append(f"{key}={str(value).lower()}")
            else:
                query_params.append(f"{key}={value}")

        full_url = f"{url}?{'&'.join(query_params)}"

        try:
            response = requests.post(full_url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def process_message(self, user_message: str, user_id: str, conversation_history: List[Dict[str, str]]) -> str:
        """Process a user message and return agent response"""
        # Prepare the messages for the OpenAI API
        messages = [{"role": "system", "content": self.system_instructions}]

        # Add conversation history
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the current user message
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI with tools
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",  # or gpt-3.5-turbo
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # If the model wants to call tools
        if tool_calls:
            # Send the info for each function call and function response to the model
            messages.append(response_message)  # Add original response

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Add user_id to function arguments if not present
                if "user_id" not in function_args:
                    function_args["user_id"] = user_id

                # Call the MCP tool
                tool_response = self.call_mcp_tool(function_name, function_args)

                # Add tool response to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_response),
                })

            # Get final response from the model with tool results
            final_response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
            )
            return final_response.choices[0].message.content
        else:
            # If no tools were called, return the model's response directly
            return response_message.content


# Example usage
if __name__ == "__main__":
    # Example - won't run without API key
    pass