#!/usr/bin/env python3
"""
Generate Embeddings Script

This script scans all guide files in the guides directory, generates embeddings
using Google Vertex AI, and uploads them to Firestore for semantic search.

This script is designed to be run as part of the content pipeline workflow.

Usage:
    python scripts/generate_embeddings.py
    
Environment Variables:
    GCP_PROJECT_ID: Google Cloud Project ID (default: from application default)
"""

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import frontmatter
except ImportError:
    print("❌ Missing dependency: python-frontmatter")
    print("   Install with: pip install python-frontmatter")
    sys.exit(1)

try:
    from google.cloud import firestore
    from vertexai.language_models import TextEmbeddingModel
    import vertexai
except ImportError:
    print("❌ Missing dependencies: google-cloud-firestore, google-cloud-aiplatform")
    print("   Install with: pip install google-cloud-firestore google-cloud-aiplatform")
    sys.exit(1)

# --- CONFIGURATION ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = "us-central1"
FIRESTORE_COLLECTION = "implementation-guides"
GUIDES_ROOT_DIR = Path("guides")
MODEL_NAME = "text-embedding-004"
MAX_WORKERS = 10
BATCH_SIZE = 5  # Process embeddings in batches to avoid rate limits

# --- INITIALIZE CLIENTS ---
print(f"🔧 Initializing Google Cloud clients...")
print(f"   Project ID: {PROJECT_ID}")
print(f"   Location: {LOCATION}")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Firestore
db = firestore.Client(project=PROJECT_ID)

# Initialize embedding model
model = TextEmbeddingModel.from_pretrained(MODEL_NAME)


def extract_text_for_embedding(content: str, max_chars: int = 10000) -> str:
    """
    Extract and prepare text for embedding generation.
    Truncate if necessary to stay within model limits.
    """
    # Remove excessive whitespace
    text = " ".join(content.split())
    
    # Truncate if too long
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    
    return text


def process_guide_file(file_path: Path) -> dict:
    """
    Reads a guide, generates its embedding, and returns the document data.
    Returns None if processing fails.
    """
    try:
        rel_path = file_path.relative_to(GUIDES_ROOT_DIR.parent)
        print(f"📄 Processing: {rel_path}")
        
        # Load frontmatter and content
        post = frontmatter.load(file_path)
        content = post.content
        metadata = post.metadata
        
        # Generate a unique, stable ID from the file path
        doc_id = str(file_path.relative_to(GUIDES_ROOT_DIR)).replace("/", "_").replace(".md", "")
        
        # Prepare text for embedding
        embedding_text = extract_text_for_embedding(content)
        
        # Generate embedding
        embeddings = model.get_embeddings([embedding_text])
        vector = embeddings[0].values
        
        # Prepare data for Firestore
        doc_data = {
            "title": metadata.get("title", file_path.parent.name),
            "division": metadata.get("division", "uncategorized"),
            "maturity": metadata.get("maturity", "unknown"),
            "source_url": metadata.get("source_url", ""),  # Empty for local guides
            "file_path": str(file_path.relative_to(GUIDES_ROOT_DIR)),
            "content": content,
            "embedding": vector,
            "content_length": len(content),
            "is_local": not bool(metadata.get("source_url")),  # Flag for local-only guides
        }
        
        return {"id": doc_id, "data": doc_data, "path": rel_path}
        
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")
        return None


def upsert_to_firestore(results: list) -> tuple:
    """
    Upsert processed guide documents to Firestore.
    Returns (success_count, failure_count).
    """
    success_count = 0
    failure_count = 0
    
    for result in results:
        if result is None:
            failure_count += 1
            continue
            
        try:
            doc_id = result["id"]
            doc_data = result["data"]
            
            # Upsert to Firestore
            db.collection(FIRESTORE_COLLECTION).document(doc_id).set(doc_data)
            print(f"   ✅ Upserted: {doc_id}")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to upsert {result['path']}: {e}")
            failure_count += 1
    
    return success_count, failure_count


def main():
    """Finds all guides and processes them in parallel."""
    print("=" * 70)
    print("🚀 Starting Embedding Generation Process")
    print("=" * 70)
    
    # Find all guide files
    guide_files = list(GUIDES_ROOT_DIR.glob("**/index.md"))
    
    if not guide_files:
        print("⚠️  No guide files found to process.")
        return
    
    print(f"\n📊 Found {len(guide_files)} guides to process")
    print(f"🔧 Using model: {MODEL_NAME}")
    print(f"🔧 Max workers: {MAX_WORKERS}")
    print("=" * 70 + "\n")
    
    # Process files in parallel
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_guide_file, f): f for f in guide_files}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    print("\n" + "=" * 70)
    print("💾 Uploading to Firestore...")
    print("=" * 70 + "\n")
    
    # Upsert to Firestore
    success_count, failure_count = upsert_to_firestore(results)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ Embedding Generation Complete!")
    print("=" * 70)
    print(f"   Total guides found:    {len(guide_files)}")
    print(f"   Successfully indexed:  {success_count}")
    print(f"   Failed:                {failure_count}")
    print("=" * 70)
    
    if failure_count > 0:
        print("\n⚠️  Some files failed to process. Check logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
