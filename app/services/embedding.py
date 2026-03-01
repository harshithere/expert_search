import weaviate
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate.embedded import EmbeddedOptions

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document
from llama_index.core.schema import IndexNode

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

        self.docstore = SimpleDocumentStore()

    def create_documents_recursive(self, data, cursor):
        documents = []
        for row in data:
            sub_texts, candidate_id = [], row[0]
            cursor.execute("""SELECT c.first_name, c.last_name, c.gender, c.headline, c.years_of_experience, cities.name as city, countries.name as country 
                FROM candidates as c 
                JOIN cities ON cities.id = c.city_id 
                join countries on cities.country_id = countries.id 
                WHERE c.id = %s""", (row[0],))
            first_name, last_name, gender, headline, YOE, city, country = cursor.fetchone()
            candidate_text = "Headline: " + headline
            candidate_name = first_name + " " + last_name

            cursor.execute("SELECT job_title, start_date, is_current, description FROM work_experience WHERE candidate_id = %s", (candidate_id,))
            work_experiences = cursor.fetchall()
            for work_experience in work_experiences:
                candidate_text += "\n" + "Work Experience: " +  work_experience[0] + " " + work_experience[3]
                sub_texts.append(('Work Experience', work_experience[0] + " " + work_experience[3]))

            print("Creating VB embedding for " + candidate_name + "with info -->" + candidate_text)

            # Create a Document
            parent_node = Document(
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

            all_nodes = [parent_node]
            for label, text in sub_texts:
                child_node = IndexNode(
                    text=f"{label}: {text}", 
                    index_id=parent_node.node_id, # Link to parent
                    metadata={"candidate_id": candidate_id, "type": "child"}
                )
                all_nodes.append(child_node)
                self.docstore.add_documents([parent_node])

            documents.append(all_nodes)

        # 3. Save the StorageContext (or use a persistent Vector DB like Pinecone/Chroma)
        storage_context = StorageContext.from_defaults(docstore=self.docstore)
        storage_context.persist(persist_dir="data/doc_storage")
        return documents

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

            print("For candidate " + candidate_name + "vecorr info is -->>" + candidate_text)
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

