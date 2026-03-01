# Expert_search
A service that allows users to search for subject-matter experts through API endpoints

## Setup
- Create virtual environment: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Run the application: `uvicorn main:app --reload`

## API Endpoints

### Ingest
- POST /api/ingest

### Search
- POST /api/search

### Design Decisions
- Dividing ingest and search into seperate API routers for clarity
- Vector DB decision:
-- Chroma selected because it is a lightweight that can be run locally from a single file. It still supports hybrid search which is necessary for this application. Pgvector could be a better DB for the storage but not used from sheer time POV
-- Weavite also has a great hybrid search but I was facing some problem with the local deployment due to the python version used for the application
- Embedding decisions
-- All candidate work information (headline, past experiences) etc is embedded together to get better context on cross experiences. 
- UV would be a better package manager but sometimes takes longer to setup system with that so was avoided. Docker was not used because my 8GB RAM system gets overloaded given the other applications running