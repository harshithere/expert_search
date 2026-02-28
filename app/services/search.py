#import chromadb
from typing import Optional
import weaviate
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore

class SearchVectorDb:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initializes the local vector database client."""
        self.client = weaviate.connect_to_local()
        self.vector_store = WeaviateVectorStore(
            weaviate_client=self.client, 
            index_name="JobDescriptions"
        )

        # 3. Load the index from the vector store directly
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)

    def get_collection(self, name: str):
        """Retrieves or creates a collection by name."""
        return self.client.get_or_create_collection(name=name)

    def search(self, query: str, conversation_id: Optional[str] = ""):
        """Performs a similarity search in the specified collection."""
        query_engine = self.index.as_query_engine(
            vector_store_query_mode="hybrid", 
            alpha=0.5
        )

        response = query_engine.query(query)
        return response        
