# API Contract: Todo Application

## Base Rules
- All endpoints require authentication via JWT token in Authorization header
- All requests and responses use JSON format
- All datetime fields use ISO 8601 format
- Error responses follow the format: `{"error": "error_message"}`

## Endpoints

### Authentication
- `POST /api/auth/login` - User login, returns JWT token
- `POST /api/auth/signup` - User registration, returns JWT token
- `POST /api/auth/logout` - User logout

### Task Management

#### `GET /api/users/{user_id}/tasks`
- **Description**: Retrieve all tasks for a specific user
- **Auth Required**: Yes
- **Path Parameters**:
  - `user_id`: ID of the user whose tasks to retrieve
- **Query Parameters**: None
- **Request Body**: None
- **Success Response**:
  - Code: 200
  - Content: `{"tasks": [{"id": "string", "user_id": "string", "title": "string", "description": "string", "completed": "boolean", "created_at": "datetime", "updated_at": "datetime"}]}`
- **Error Responses**:
  - 401: Unauthorized
  - 404: User not found

#### `POST /api/users/{user_id}/tasks`
- **Description**: Create a new task for a specific user
- **Auth Required**: Yes
- **Path Parameters**:
  - `user_id`: ID of the user creating the task
- **Request Body**:
  - `{"title": "string", "description": "string"}`
- **Success Response**:
  - Code: 201
  - Content: `{"id": "string", "user_id": "string", "title": "string", "description": "string", "completed": "boolean", "created_at": "datetime", "updated_at": "datetime"}`
- **Error Responses**:
  - 400: Invalid request body
  - 401: Unauthorized
  - 404: User not found

#### `GET /api/users/{user_id}/tasks/{task_id}`
- **Description**: Retrieve a specific task for a user
- **Auth Required**: Yes
- **Path Parameters**:
  - `user_id`: ID of the user
  - `task_id`: ID of the task to retrieve
- **Request Body**: None
- **Success Response**:
  - Code: 200
  - Content: `{"id": "string", "user_id": "string", "title": "string", "description": "string", "completed": "boolean", "created_at": "datetime", "updated_at": "datetime"}`
- **Error Responses**:
  - 401: Unauthorized
  - 404: Task not found or user not found

#### `PUT /api/users/{user_id}/tasks/{task_id}`
- **Description**: Update a specific task for a user
- **Auth Required**: Yes
- **Path Parameters**:
  - `user_id`: ID of the user
  - `task_id`: ID of the task to update
- **Request Body**:
  - `{"title": "string", "description": "string", "completed": "boolean"}`
- **Success Response**:
  - Code: 200
  - Content: `{"id": "string", "user_id": "string", "title": "string", "description": "string", "completed": "boolean", "created_at": "datetime", "updated_at": "datetime"}`
- **Error Responses**:
  - 400: Invalid request body
  - 401: Unauthorized
  - 404: Task not found or user not found

#### `DELETE /api/users/{user_id}/tasks/{task_id}`
- **Description**: Delete a specific task for a user
- **Auth Required**: Yes
- **Path Parameters**:
  - `user_id`: ID of the user
  - `task_id`: ID of the task to delete
- **Request Body**: None
- **Success Response**:
  - Code: 204
  - Content: Empty
- **Error Responses**:
  - 401: Unauthorized
  - 404: Task not found or user not found

#### `PATCH /api/users/{user_id}/tasks/{task_id}/complete`
- **Description**: Toggle the completion status of a specific task
- **Auth Required**: Yes
- **Path Parameters**:
  - `user_id`: ID of the user
  - `task_id`: ID of the task to update
- **Request Body**:
  - `{"completed": "boolean"}`
- **Success Response**:
  - Code: 200
  - Content: `{"id": "string", "user_id": "string", "title": "string", "description": "string", "completed": "boolean", "created_at": "datetime", "updated_at": "datetime"}`
- **Error Responses**:
  - 400: Invalid request body
  - 401: Unauthorized
  - 404: Task not found or user not found