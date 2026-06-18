import os
import chromadb
from sentence_transformers import SentenceTransformer

KB_FOLDER = "knowledge_base"
DB_FOLDER = "vector_db"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=DB_FOLDER)

collection = client.get_or_create_collection(
    name="business_statistics_kb"
)

def read_markdown_files(folder_path):
    documents = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            documents.append({
                "id": filename.replace(".md", ""),
                "text": content,
                "source": filename
            })

    return documents

def ingest_documents():
    documents = read_markdown_files(KB_FOLDER)

    for doc in documents:
        embedding = embedding_model.encode(doc["text"]).tolist()

        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[embedding],
            metadatas=[{"source": doc["source"]}]
        )

    print(f"Ingested {len(documents)} documents into ChromaDB.")

if __name__ == "__main__":
    ingest_documents()