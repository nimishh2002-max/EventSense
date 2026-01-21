import os
import hashlib
import chromadb
from typing import List, Dict, Optional, Any

# LangChain Imports
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURATION (ABSOLUTE PATHS) ---
# This ensures the DB is always created in your project root, not in a temp folder
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_FILE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db_storage")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "knowledge_base")
EMBEDDING_MODEL = "mxbai-embed-large:latest"

def get_embedding_function():
    return OllamaEmbeddings(model=EMBEDDING_MODEL)

def generate_doc_id(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()

def get_chroma_client():
    """
    Creates a Persistent Client. Data is saved to 'chroma_db_storage' folder.
    """
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
        print(f"📁 Creating Database Storage at: {DB_PATH}")
    return chromadb.PersistentClient(path=DB_PATH)

def get_vectorstore():
    """
    Returns the LangChain wrapper.
    Checks if DB is empty; if so, populates it automatically.
    """
    client = get_chroma_client()
    collection_name = "campus_event_memory"
    
    # Check if data exists
    try:
        count = client.get_collection(collection_name).count()
    except Exception:
        count = 0
        
    db = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=get_embedding_function(),
    )
    
    # SELF-HEALING: If DB is empty, load data immediately
    if count == 0:
        print("⚠️ Database is empty. Auto-loading initial data...")
        _ingest_files(db)
        
    return db

def _ingest_files(db_instance):
    """
    Internal function to read .txt files and save them.
    """
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"⚠️ Created data folder: {DATA_PATH}. Put your .txt files here!")
        return

    documents = []
    print(f"📂 Scanning {DATA_PATH}...")
    
    for filename in os.listdir(DATA_PATH):
        if not filename.endswith(".txt"): continue
        
        file_path = os.path.join(DATA_PATH, filename)
        category = "memory" if any(k in filename.lower() for k in ["incident", "log", "memory"]) else "rule"
        
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            raw_docs = loader.load()
            for doc in raw_docs:
                doc.metadata["category"] = category
                doc.metadata["source_file"] = filename
                documents.extend(raw_docs)
            print(f"   -> Found {filename}")
        except Exception as e:
            print(f"   ❌ Error {filename}: {e}")

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        ids = [generate_doc_id(chunk.page_content) for chunk in chunks]
        
        print(f"💉 Injecting {len(chunks)} chunks into Persistent DB...")
        db_instance.add_documents(documents=chunks, ids=ids)
        print("✅ Data persisted.")
    else:
        print("⚠️ No documents found to ingest.")

def query_knowledge_base(query: str, filters: Optional[Dict[str, Any]] = None, k: int = 4) -> List[Dict]:
    """
    Retrieves info from the persistent DB.
    """
    db = get_vectorstore() # This triggers the auto-load check
    results = db.similarity_search(query, k=k, filter=filters)
    
    return [{"content": doc.page_content, "source": doc.metadata.get("source_file", "unknown")} for doc in results]

def add_memory_log(event_name: str, outcome: str, description: str, lesson_learned: str) -> bool:
    """
    Writes a new memory to the persistent database.
    """
    print(f"\n--- 💾 SAVING TO DISK: {event_name} ---")
    
    content = f"""
    EVENT ID: {event_name.upper()}
    Type: User Feedback
    Outcome: {outcome}
    Description: {description}
    Lesson Learned: {lesson_learned}
    """
    
    new_doc = Document(
        page_content=content,
        metadata={
            "category": "memory",
            "source_file": "user_feedback_log.txt",
            "timestamp": "new"
        }
    )
    
    try:
        db = get_vectorstore()
        doc_id = generate_doc_id(content)
        db.add_documents(documents=[new_doc], ids=[doc_id])
        
        # Verify immediately
        check = db.similarity_search(description, k=1)
        if check:
            print("✅ SUCCESS: Memory verified on hard drive.")
            return True
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

# --- AUTO-SETUP BLOCK ---
# This allows you to run `python src/rag.py` to force-check the DB
if __name__ == "__main__":
    print("🔧 RUNNING DIRECT DB CHECK...")
    db = get_vectorstore()
    print("✅ DB Check Complete. You can run 'streamlit run main.py' now.")