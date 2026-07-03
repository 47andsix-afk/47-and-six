import os
from chromadb import PersistentClient
from chef_knowledge.loader import iter_school_files, extract_text

try:
    from google.genai import Client as GeminiClient  # type: ignore[import-not-found, import-untyped]
except ImportError:
    GeminiClient = None

DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = "chef_training"

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client_genai = GeminiClient(api_key=API_KEY) if GeminiClient and API_KEY else None


def build_index():
    client = PersistentClient(path=DB_PATH)
    try:
        coll = client.get_or_create_collection(COLLECTION_NAME)
    except Exception:
        coll = client.get_collection(name=COLLECTION_NAME)

    print("Building Chef Knowledge Index...")

    for i, path in enumerate(iter_school_files()):
        text = extract_text(path)

        if not text or not text.strip():
            print(f"Skipping empty file: {path}")
            continue

        try:
            if client_genai is None:
                print("Gemini embedding client not configured; skipping index build.")
                break

            embedding_resp = client_genai.models.embed_content(
                model="text-embedding-004",
                contents=text,
            )
            embeddings = getattr(embedding_resp, "embeddings", None)
            embedding = None
            if embeddings:
                first_embedding = embeddings[0]
                embedding = getattr(first_embedding, "values", None)

            if not embedding:
                print(f"No embedding returned for {path}")
                continue

            coll.add(
                documents=[text],
                embeddings=[embedding],
                ids=[f"chef-doc-{i}"],
                metadatas=[{"filename": path.name, "path": str(path), "source": "AESOCA Training"}],
            )

            print(f"Indexed: {path.name}")

        except Exception as e:
            print(f"Error indexing {path}: {e}")

    print("Chef Knowledge Index Complete.")


def query_chef_knowledge(prompt: str, n_results: int = 5):
    client = PersistentClient(path=DB_PATH)
    try:
        coll = client.get_or_create_collection(COLLECTION_NAME)
    except Exception:
        coll = client.get_collection(name=COLLECTION_NAME)

    try:
        results = coll.query(query_texts=[prompt], n_results=n_results)
    except Exception:
        return {"documents": [], "metadatas": []}

    return results
