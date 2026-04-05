import os
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

def format_handbook_url(file_path):
    """Converts a local git file path into a live GitLab Handbook URL to improve the user experience by providing clickable links."""
    # Convert path separators to forward slashes for consistency (Windows fix)
    file_path = file_path.replace("\\", "/")
    
    # 1. Remove the local folder structure
    if "content/handbook/" in file_path:
        url_path = file_path.split("content/handbook/")[-1]
    else:
        url_path = file_path.split("data/handbook/")[-1]
        
    # 2. Remove the markdown file names to get the clean directory path
    url_path = url_path.replace("_index.md", "")
    url_path = url_path.replace("index.md", "")
    url_path = url_path.replace(".md", "/")
    
    # 3. Build the final URL
    clean_url = f"https://handbook.gitlab.com/handbook/{url_path}"
    
    # Clean up any accidental double slashes (except for the https://)
    clean_url = clean_url.replace("///", "/").replace("//", "/")
    clean_url = clean_url.replace("https:/", "https://")
    
    return clean_url

def load_documents():
    """Load Handbook and Direction pages, and format their sources to live URLs."""
    documents = []
    
    # 1. Load Handbook
    handbook_path = "data/handbook"
    if os.path.exists(handbook_path):
        print("✅ Loading Handbook from local folder...")
        handbook_loader = DirectoryLoader(handbook_path, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
        docs = handbook_loader.load()
        
        # Transform the local file paths into live URLs!
        for doc in docs:
            doc.metadata["source"] = format_handbook_url(doc.metadata.get("source", ""))
            
        documents.extend(docs)
        
    # 2. Load Direction Pages
    direction_path = "data/direction"
    if os.path.exists(direction_path):
        print("✅ Loading Direction Pages from local folder...")
        direction_loader = DirectoryLoader(direction_path, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
        dir_docs = direction_loader.load()
        
        # Transform direction local paths to live URLs
        for doc in dir_docs:
            source_path = doc.metadata.get("source", "")
            # Get just the filename (e.g., 'ai-powered.md' or 'main_direction.md')
            filename = os.path.basename(source_path)
            clean_name = filename.replace(".md", "")
            
            # Map back to the live URL
            if clean_name == "main_direction":
                doc.metadata["source"] = "https://about.gitlab.com/direction/"
            else:
                doc.metadata["source"] = f"https://about.gitlab.com/direction/{clean_name}/"
                
        documents.extend(dir_docs)
    else:
        print("⚠️ Direction folder not found. Did the scraper run?")

    # 3. Split into chunks
    print("✅ Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = text_splitter.split_documents(documents)
    
    print(f"✅ Total chunks created: {len(chunks)}")
    return chunks