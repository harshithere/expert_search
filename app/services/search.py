import os
import chromadb
from typing import Optional
import weaviate
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from dotenv import load_dotenv


from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

load_dotenv()

class SearchVectorDb:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initializes the local vector database client.
        self.client = weaviate.connect_to_local()
        self.vector_store = WeaviateVectorStore(
            weaviate_client=self.client, 
            index_name="JobDescriptions"
        )

        # 3. Load the index from the vector store directly
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)"""

        db_client = chromadb.PersistentClient(path="data/chroma")
        chroma_collection = db_client.get_collection("job_search_index")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Set this as the global embedding model for LlamaIndex
        Settings.embed_model = embed_model

        llm = OpenRouter(
            api_key=os.getenv("OPENROUTER_KEY"),
            model="openai/gpt-4o", 
            context_window=128000, # Match the model's capacity
        )

        # 2. Set it globally so your index uses it automatically
        Settings.llm = llm

        # Load the index from the vector store
        self.index = VectorStoreIndex.from_vector_store(
            vector_store, 
            embed_model=embed_model
        )

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
    
    def search_RRF(self, query: str, conversation_id: Optional[str] = ""):
        vector_retriever = self.index.as_retriever(similarity_top_k=5)

        # BM25 requires the underlying nodes to calculate corpus statistics
        bm25_retriever = BM25Retriever.from_defaults(
            docstore=self.index.docstore, 
            similarity_top_k=5
        )

        retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=5,
            num_queries=1,  # Set to 1 to use only the original query (avoids extra LLM calls)
            mode="reciprocal_rerank", # This enables RRF
            use_async=True,
        )

        # 3. Create the Query Engine
        query_engine = RetrieverQueryEngine.from_args(retriever)
        response = query_engine.query(query)
        return response
