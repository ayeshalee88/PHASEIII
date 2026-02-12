from shared_database import engine
from sqlalchemy import text

print('Engine URL:', engine.url)

with engine.connect() as conn:
    result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table";'))
    tables = [row[0] for row in result]
    print('Tables in database via engine:', tables)
    
    # Try to query the tasks table specifically
    try:
        result = conn.execute(text('SELECT COUNT(*) FROM tasks;'))
        count = result.scalar()
        print(f'Tasks table exists and has {count} rows')
    except Exception as e:
        print(f'Error querying tasks table: {e}')