# Data Model: Phase II – Full-Stack Todo Web Application

## Task Entity

### Fields
- `id` (UUID/string) - Unique identifier for each task
- `user_id` (UUID/string) - Foreign key linking to the user who owns the task
- `title` (string) - Required title of the task
- `description` (string, optional) - Optional detailed description of the task
- `completed` (boolean) - Flag indicating whether the task is completed
- `created_at` (timestamp) - Timestamp when the task was created
- `updated_at` (timestamp) - Timestamp when the task was last updated

### Relationships
- Each task belongs to exactly one user (user_id foreign key)
- Each user can own multiple tasks

### Validation Rules
- `title` is required and must not be empty
- `user_id` must reference an existing user
- `completed` defaults to `false`
- `created_at` is set automatically on creation
- `updated_at` is updated automatically on any change

### State Transitions
- Task can transition from `completed: false` to `completed: true`
- Task can transition from `completed: true` to `completed: false`
- Task deletion is permanent

## User Entity (for reference)

### Fields
- `id` (UUID/string) - Unique identifier for each user
- `email` (string) - User's email address
- `password_hash` (string) - Hashed password for authentication
- `created_at` (timestamp) - Timestamp when the user was created
- `updated_at` (timestamp) - Timestamp when the user was last updated