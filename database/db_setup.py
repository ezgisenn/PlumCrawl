import sqlite3
import os

DB_PATH = 'plumcrawl.db'
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def initialize_database():
    """Initializes the SQLite database with the defined schema."""
    print("Agent 2: Initializing PlumCrawl database...")
    
    # Connect to SQLite (this creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read and execute the schema.sql file
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_script = f.read()
        
    cursor.executescript(schema_script)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Agent 2: Database initialized successfully at {DB_PATH} with WAL mode enabled for concurrency.")

if __name__ == "__main__":
    initialize_database()