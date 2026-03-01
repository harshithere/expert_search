from fastapi import APIRouter
import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from app.services.embedding import embedCandidateData

load_dotenv()
router = APIRouter()
embed_candidate_data = embedCandidateData()

@router.post("/")
def create_vector_db():
    """
    Endpoint for creating the Vector DB and ingesting data.
    """
    return {"message": "Vector DB ingestion initiated."}

def get_db_connection():
    try:
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

@router.post("/ingest")
def ingest_data():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cursor:
            #cursor.execute("SELECT first_name, last_name, gender, headline, years_of_experience FROM candidates LIMIT 10")

            cursor.execute("SELECT DISTINCT id FROM candidates LIMIT 10")

            data = cursor.fetchall()
            print(data)
            embed_candidate_data.embed_data(data, cursor)
            return {"status": "success", "message": "Data ingested successfully!"}
    raise HTTPException(status_code=500, detail="Database connection failed")

if __name__ == "__main__":
    ingest_data()
