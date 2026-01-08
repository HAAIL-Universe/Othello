import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def migrate():
    if not DATABASE_URL:
        print("DATABASE_URL not set. Skipping migration.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Checking 'sessions' table columns...")
        
        # Add duet_narrator_text
        cur.execute("""
            ALTER TABLE sessions 
            ADD COLUMN IF NOT EXISTS duet_narrator_text TEXT NULL;
        """)
        
        # Add duet_narrator_updated_at
        cur.execute("""
            ALTER TABLE sessions 
            ADD COLUMN IF NOT EXISTS duet_narrator_updated_at TIMESTAMPTZ NULL;
        """)
        
        # Add duet_narrator_msg_count
        cur.execute("""
            ALTER TABLE sessions 
            ADD COLUMN IF NOT EXISTS duet_narrator_msg_count INT NULL DEFAULT 0;
        """)
        
        conn.commit()
        print("Migration successful: Added narrator columns to sessions table.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")
        exit(1)

if __name__ == "__main__":
    migrate()
