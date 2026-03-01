import weaviate
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate.embedded import EmbeddedOptions

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document

class embedCandidateData():
    def __init__(self, persist_directory: str = "./vector_db"):
        """Initializes the local vector database client."""
        self.client = chromadb.PersistentClient(path="data/chroma")
        
        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Set this as the global embedding model for LlamaIndex
        Settings.embed_model = embed_model

        # 3. Create or Get a collection
        chroma_collection = self.client.get_or_create_collection("job_search_index")
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        """self.vector_store = WeaviateVectorStore(
            weaviate_client=self.client, 
            index_name="JobDescriptions"
        )"""

    def create_documents(self, data, cursor):
        documents = []
        for row in data:
            cursor.execute("""SELECT c.first_name, c.last_name, c.gender, c.headline, c.years_of_experience, cities.name as city, countries.name as country 
                FROM candidates as c 
                JOIN cities ON cities.id = c.city_id 
                join countries on cities.country_id = countries.id 
                WHERE c.id = %s""", (row[0],))
            first_name, last_name, gender, headline, YOE, city, country = cursor.fetchone()
            candidate_text = "Headline: " + headline
            candidate_name = first_name + " " + last_name

            cursor.execute("SELECT job_title, start_date, is_current, description FROM work_experience WHERE candidate_id = %s", (row[0],))
            work_experiences = cursor.fetchall()
            for work_experience in work_experiences:
                candidate_text += "\n" + "Work Experience: " +  work_experience[0] + " " + work_experience[3]

            print("Creating VB embedding for " + candidate_name + "with info -->" + candidate_text)

            # Create a Document
            doc = Document(
                text=candidate_text,
                metadata={
                    "candidate_name": candidate_name,
                    "experience": YOE,
                    "city": city,
                    "country": country
                },
                # Optional: control how metadata appears in the text for the LLM
                excluded_llm_metadata_keys=["email"], 
                excluded_embed_metadata_keys=["experience"]
            )
            documents.append(doc)
        return documents

    def embed_data(self, data, cursor):
        documents = self.create_documents(data, cursor)
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=self.storage_context,
            show_progress=True
        )

        print(f"Successfully persisted {len(documents)} documents to ./chroma_db")