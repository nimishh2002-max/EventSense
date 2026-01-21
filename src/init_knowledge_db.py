import sqlite3
import os

# Configuration
DB_NAME = "knowledge_base.db"

# These are the exact files you uploaded. 
# We are creating "index cards" for them in the database.
documents_to_index = [
    {
        "filename": "incident_memory_log.txt",
        "file_path": "./data/knowledge_base/incident_memory_log.txt",
        "category": "Historical Risks",
        "description": "Logs of past failures: Spring Fling overcrowding, Hackathon WiFi crash, and generator fume issues.",
        "status": "ready"
    },
    {
        "filename": "university_sops_policy.txt",
        "file_path": "./data/knowledge_base/university_sops_policy.txt",
        "category": "Compliance Rules",
        "description": "Rules for Fire Safety (aisle width), Alcohol service, and Outdoor noise ordinances.",
        "status": "ready"
    }
]

def create_database():
    print(f"⚙️  Creating database '{DB_NAME}'...")
    
    # Connect to the database (this creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the table (the columns in our catalog)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_path TEXT,
            category TEXT,
            description TEXT,
            status TEXT
        )
    ''')

    # Clear old entries so we don't have duplicates
    cursor.execute('DELETE FROM documents')

    # Add our files to the database
    print("📝 Writing file details to the catalog...")
    for doc in documents_to_index:
        cursor.execute('''
            INSERT INTO documents (filename, file_path, category, description, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc['filename'], doc['file_path'], doc['category'], doc['description'], doc['status']))
        
        print(f"   > Indexed: {doc['filename']}")

    # Save changes and close
    conn.commit()
    conn.close()
    print(f"✅ Success! Database '{DB_NAME}' is ready.")

if __name__ == "__main__":
    create_database()