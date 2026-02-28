import weaviate
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate.embedded import EmbeddedOptions

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

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

    def create_documents(self, data):
        return []

    def embed_data(self, data):
        documents = self.create_documents(data)
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=self.storage_context,
            show_progress=True
        )

        print(f"Successfully persisted {len(documents)} documents to ./chroma_db")