#!/usr/bin/env python3
"""
In-Memory Todo Application

A command-line Todo application that stores tasks in memory with the following functionality:
- Add tasks with title and description
- List all tasks with unique ID and completion status
- Update task title and description by ID
- Delete tasks by ID
- Toggle task completion state by ID
"""

import json
import shlex
import sys
from datetime import datetime
from typing import Dict, List, Optional


class Task:
    """Represents a single todo task"""

    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False):
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create Task instance from dictionary"""
        task = cls(data['id'], data['title'], data['description'], data['completed'])
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.updated_at = datetime.fromisoformat(data['updated_at'])
        return task


class TodoApp:
    """Main Todo Application class with in-memory storage"""

    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task to the todo list"""
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(self.next_id, title.strip(), description.strip())
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def list_tasks(self) -> List[Task]:
        """Return all tasks in the todo list"""
        return list(self.tasks.values())

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        return self.tasks.get(task_id)

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Task]:
        """Update an existing task"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]

        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip()

        task.updated_at = datetime.now()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

    def toggle_task_completion(self, task_id: int) -> Optional[Task]:
        """Toggle the completion status of a task"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        task.completed = not task.completed
        task.updated_at = datetime.now()
        return task

    def mark_task_completed(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        task.completed = True
        task.updated_at = datetime.now()
        return task

    def mark_task_incomplete(self, task_id: int) -> Optional[Task]:
        """Mark a task as incomplete"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        task.completed = False
        task.updated_at = datetime.now()
        return task


class TodoCLI:
    """Command-Line Interface for the Todo Application"""

    def __init__(self):
        self.app = TodoApp()

    def print_task(self, task: Task):
        """Print a single task with formatting"""
        status = "X" if task.completed else "O"
        print(f"[{status}] ID: {task.id} | Title: {task.title}")
        if task.description:
            print(f"      Description: {task.description}")
        print(f"      Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if task.updated_at != task.created_at:
            print(f"      Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def print_tasks(self, tasks: List[Task]):
        """Print a list of tasks"""
        if not tasks:
            print("No tasks found.\n")
            return

        for task in tasks:
            self.print_task(task)

    def add_task(self, args: List[str]):
        """Add a new task"""
        if len(args) < 1:
            print("Usage: add <title> [description]")
            return

        title = args[0]
        description = " ".join(args[1:]) if len(args) > 1 else ""

        try:
            task = self.app.add_task(title, description)
            print(f"Task added successfully!")
            self.print_task(task)
        except ValueError as e:
            print(f"Error: {e}\n")

    def list_tasks(self, args: List[str]):
        """List all tasks"""
        tasks = self.app.list_tasks()
        print(f"Total tasks: {len(tasks)}\n")
        self.print_tasks(tasks)

    def view_task(self, args: List[str]):
        """View a specific task"""
        if len(args) != 1:
            print("Usage: view <id>")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            print("Error: ID must be a number\n")
            return

        task = self.app.get_task(task_id)
        if task:
            print("Task details:\n")
            self.print_task(task)
        else:
            print(f"Task with ID {task_id} not found.\n")

    def update_task(self, args: List[str]):
        """Update a task"""
        if len(args) < 2:
            print("Usage: update <id> <title> [description]")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            print("Error: ID must be a number\n")
            return

        title = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else ""

        try:
            task = self.app.update_task(task_id, title, description)
            if task:
                print(f"Task updated successfully!")
                self.print_task(task)
            else:
                print(f"Task with ID {task_id} not found.\n")
        except ValueError as e:
            print(f"Error: {e}\n")

    def delete_task(self, args: List[str]):
        """Delete a task"""
        if len(args) != 1:
            print("Usage: delete <id>")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            print("Error: ID must be a number\n")
            return

        if self.app.delete_task(task_id):
            print(f"Task with ID {task_id} deleted successfully.\n")
        else:
            print(f"Task with ID {task_id} not found.\n")

    def complete_task(self, args: List[str]):
        """Mark a task as completed"""
        if len(args) != 1:
            print("Usage: complete <id>")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            print("Error: ID must be a number\n")
            return

        task = self.app.mark_task_completed(task_id)
        if task:
            print(f"Task marked as completed!")
            self.print_task(task)
        else:
            print(f"Task with ID {task_id} not found.\n")

    def incomplete_task(self, args: List[str]):
        """Mark a task as incomplete"""
        if len(args) != 1:
            print("Usage: incomplete <id>")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            print("Error: ID must be a number\n")
            return

        task = self.app.mark_task_incomplete(task_id)
        if task:
            print(f"Task marked as incomplete!")
            self.print_task(task)
        else:
            print(f"Task with ID {task_id} not found.\n")

    def toggle_task(self, args: List[str]):
        """Toggle task completion status"""
        if len(args) != 1:
            print("Usage: toggle <id>")
            return

        try:
            task_id = int(args[0])
        except ValueError:
            print("Error: ID must be a number\n")
            return

        task = self.app.toggle_task_completion(task_id)
        if task:
            status = "completed" if task.completed else "incomplete"
            print(f"Task marked as {status}!")
            self.print_task(task)
        else:
            print(f"Task with ID {task_id} not found.\n")

    def help(self, args: List[str]):
        """Show help information"""
        print("Todo Application - Available Commands:\n")
        print("  add <title> [description]     - Add a new task")
        print("  list                          - List all tasks")
        print("  view <id>                     - View a specific task")
        print("  update <id> <title> [desc]    - Update a task")
        print("  delete <id>                   - Delete a task")
        print("  complete <id>                 - Mark task as completed")
        print("  incomplete <id>               - Mark task as incomplete")
        print("  toggle <id>                   - Toggle task completion status")
        print("  quit/exit                     - Exit the application")
        print("  help                          - Show this help message\n")

    def run(self):
        """Run the command-line interface"""
        print("Welcome to the Todo Application!")
        print("Type 'help' for available commands or 'quit' to exit.\n")

        while True:
            try:
                user_input = input("todo> ").strip()

                if not user_input:
                    continue

                try:
                    parts = shlex.split(user_input)
                    command = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []
                except ValueError:
                    print("Error: Unmatched quotes in command. Use spaces without quotes or properly quote strings.\n")
                    continue

                if command in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                elif command == 'help':
                    self.help(args)
                elif command == 'add':
                    self.add_task(args)
                elif command == 'list':
                    self.list_tasks(args)
                elif command == 'view':
                    self.view_task(args)
                elif command == 'update':
                    self.update_task(args)
                elif command == 'delete':
                    self.delete_task(args)
                elif command == 'complete':
                    self.complete_task(args)
                elif command == 'incomplete':
                    self.incomplete_task(args)
                elif command == 'toggle':
                    self.toggle_task(args)
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands.\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    """Main function to run the application"""
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()