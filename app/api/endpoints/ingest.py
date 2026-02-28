from fastapi import APIRouter
import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()
router = APIRouter()

@router.post("/")
def create_vector_db():
    """
    Endpoint for creating the Vector DB and ingesting data.
    """
    return {"message": "Vector DB ingestion initiated."}

def get_db_connection():
    try:
        print(os.getenv("DB_HOST"))
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@router.post("/check-connection")
def check_connection():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"status": "success", "message": "Connected to PostgreSQL!"}
    raise HTTPException(status_code=500, detail="Database connection failed")

def get_candidate_profiles():
    

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM candidate_profiles")
        return cursor.fetchall()

    return []    

if __name__ == "__main__":
    check_connection()
