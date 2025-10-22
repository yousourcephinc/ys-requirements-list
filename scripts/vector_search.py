#!/usr/bin/env python3
"""
Vector search implementation using Vertex AI embeddings and Firestore.
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import numpy as np

from google.cloud import firestore
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

logger = logging.getLogger(__name__)

# Initialize Vertex AI
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "requirements-mcp-server")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

try:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logger.warning(f"Could not initialize Vertex AI: {e}")

# Firestore collection name
GUIDES_COLLECTION = "guides_embeddings"


def get_embedding(text: str) -> List[float]:
    """
    Generate embeddings using Vertex AI text-embedding-004 model.
    
    Args:
        text: The text to generate embeddings for
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        embeddings = model.get_embeddings([text])
        return embeddings[0].values
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def index_guide(guide_id: str, title: str, division: str, content: str, 
                file_path: str, maturity: str = "Unknown") -> None:
    """
    Index a guide in Firestore with its embedding.
    
    Args:
        guide_id: Unique identifier for the guide
        title: Guide title
        division: Division/category
        content: Full text content
        file_path: Path to the guide file
        maturity: Maturity level
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        
        # Generate embedding for the content
        # We'll embed title + content for better search
        text_to_embed = f"{title}\n\n{content}"
        embedding = get_embedding(text_to_embed)
        
        # Store in Firestore
        doc_ref = db.collection(GUIDES_COLLECTION).document(guide_id)
        doc_ref.set({
            "title": title,
            "division": division,
            "content": content[:1000],  # Store preview
            "file_path": file_path,
            "maturity": maturity,
            "embedding": embedding,
            "indexed_at": firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Indexed guide: {title}")
    except Exception as e:
        logger.error(f"Error indexing guide {guide_id}: {e}")
        raise


def search_guides(query: str, top_k: int = 5, division_filter: str = None) -> List[Dict[str, Any]]:
    """
    Search guides using semantic similarity.
    
    Args:
        query: Search query
        top_k: Number of results to return
        division_filter: Optional division to filter by
        
    Returns:
        List of matching guides with scores
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        
        # Fetch all documents (or filtered by division)
        collection_ref = db.collection(GUIDES_COLLECTION)
        if division_filter:
            docs = collection_ref.where("division", "==", division_filter).stream()
        else:
            docs = collection_ref.stream()
        
        # Calculate similarity scores
        results = []
        for doc in docs:
            data = doc.to_dict()
            doc_embedding = data.get("embedding", [])
            
            if doc_embedding:
                similarity = cosine_similarity(query_embedding, doc_embedding)
                results.append({
                    "title": data.get("title"),
                    "division": data.get("division"),
                    "file_path": data.get("file_path"),
                    "maturity": data.get("maturity"),
                    "score": similarity,
                    "content_preview": data.get("content", "")[:200] + "..."
                })
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
        
    except Exception as e:
        logger.error(f"Error searching guides: {e}")
        raise


def build_index_from_guides(guides_dir: Path) -> Dict[str, Any]:
    """
    Build the vector index from all guides in the directory.
    
    Args:
        guides_dir: Path to the guides directory
        
    Returns:
        Dictionary with indexing statistics
    """
    indexed_count = 0
    error_count = 0
    
    try:
        for division_dir in guides_dir.iterdir():
            if not division_dir.is_dir() or division_dir.name in ("semantic_index", "README.md"):
                continue
                
            division = division_dir.name
            
            for guide_dir in division_dir.iterdir():
                if not guide_dir.is_dir():
                    continue
                    
                index_file = guide_dir / "index.md"
                if not index_file.exists():
                    continue
                
                try:
                    # Read the guide content
                    with open(index_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse frontmatter
                    title = "Unknown"
                    maturity = "Unknown"
                    
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            frontmatter = parts[1]
                            markdown_content = parts[2]
                            
                            for line in frontmatter.strip().split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    key = key.strip()
                                    value = value.strip().strip('"')
                                    if key == 'title':
                                        title = value
                                    elif key == 'maturity':
                                        maturity = value
                        else:
                            markdown_content = content
                    else:
                        markdown_content = content
                    
                    # Create unique guide ID
                    guide_id = f"{division}_{guide_dir.name}"
                    file_path = str(index_file.relative_to(guides_dir))
                    
                    # Index the guide
                    index_guide(
                        guide_id=guide_id,
                        title=title,
                        division=division,
                        content=markdown_content,
                        file_path=file_path,
                        maturity=maturity
                    )
                    
                    indexed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {index_file}: {e}")
                    error_count += 1
        
        return {
            "success": True,
            "indexed_count": indexed_count,
            "error_count": error_count,
            "message": f"Successfully indexed {indexed_count} guides"
        }
        
    except Exception as e:
        logger.error(f"Error building index: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def clear_index() -> None:
    """Clear all documents from the Firestore index."""
    try:
        db = firestore.Client(project=PROJECT_ID)
        docs = db.collection(GUIDES_COLLECTION).stream()
        
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        
        logger.info(f"Cleared {deleted_count} documents from index")
    except Exception as e:
        logger.error(f"Error clearing index: {e}")
        raise
