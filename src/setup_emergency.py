from src.rag import initialize_memory

if __name__ == "__main__":
    print("🚧 STARTING DATABASE SETUP...")
    print("This will wipe existing data and re-import text files.")
    
    # This is the ONLY place reset=True should ever be used
    initialize_memory(reset=True)
    
    print("🏁 SETUP COMPLETE. You can now run 'streamlit run main.py'")