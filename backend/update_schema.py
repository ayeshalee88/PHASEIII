#!/usr/bin/env python3
"""
Script to update the database schema to match the model
"""

import sqlite3

# Connect to the database
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()

# Check if 'name' column exists
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]
print(f"Existing columns: {columns}")

# Add 'name' column if it doesn't exist
if 'name' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR")
    print("Added 'name' column to users table")

# Commit changes and close connection
conn.commit()
conn.close()
print("Database schema updated successfully!")