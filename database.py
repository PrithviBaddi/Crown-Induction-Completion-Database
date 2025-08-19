import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def get_connection():
    """Create and return a database connection"""
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        return connection
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None

def get_all_stakeholders() -> List[Dict[str, Any]]:
    """Fetch all stakeholders from the database"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # First, let's check if the stakeholders table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'stakeholders'
        """)
        
        if not cursor.fetchone():
            print("Stakeholders table not found. Available tables:")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            for table in tables:
                print(f"  - {table['table_name']}")
            return []
        
        # If table exists, fetch all stakeholders
        cursor.execute("SELECT * FROM stakeholders ORDER BY id")
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        stakeholders = [dict(row) for row in results]
        
        cursor.close()
        connection.close()
        return stakeholders
        
    except Exception as e:
        print(f"Error fetching stakeholders: {e}")
        if connection:
            connection.close()
        return []

def get_all_tables() -> List[str]:
    """Get list of all tables in the database"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        if connection:
            connection.close()
        return []

def get_table_data(table_name: str) -> List[Dict[str, Any]]:
    """Fetch all data from a specific table"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Validate table name to prevent SQL injection
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        """, (table_name,))
        
        if not cursor.fetchone():
            print(f"Table '{table_name}' not found")
            return []
        
        # Fetch data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = [dict(row) for row in results]
        
        cursor.close()
        connection.close()
        return data
        
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        if connection:
            connection.close()
        return []

def test_connection():
    """Test the database connection"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print(f"Connection successful! Current time: {result[0]}")
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        if connection:
            connection.close()
        return False

# Test connection when module is imported
if __name__ == "__main__":
    test_connection()