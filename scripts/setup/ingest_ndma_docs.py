#!/usr/bin/env python3
"""
SAHAYAK-AI NDMA Document Ingestion Pipeline

Loads NDMA/SDMA PDF documents, extracts text, chunks it,
embeds using FastEmbed, and stores in ChromaDB for RAG retrieval.
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Any

import structlog

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from config import settings

logger = structlog.get_logger(__name__)

# Chunking configuration
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text from PDF using PyMuPDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of page dicts with text and metadata
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("pymupdf_not_installed", hint="pip install PyMuPDF")
        return []
    
    pages = []
    
    try:
        doc = fitz.open(str(pdf_path))
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                pages.append({
                    "text": text.strip(),
                    "page_num": page_num + 1,
                    "source_pdf": pdf_path.name,
                })
        
        doc.close()
        logger.info(
            "pdf_extracted",
            pdf=pdf_path.name,
            pages=len(pages),
        )
        
    except Exception as e:
        logger.error("pdf_extraction_failed", pdf=pdf_path.name, error=str(e))
    
    return pages


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end
            for sep in ['. ', '.\n', '! ', '? ', '\n\n']:
                last_sep = text.rfind(sep, start + chunk_size // 2, end)
                if last_sep > start:
                    end = last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def extract_metadata(page_text: str, pdf_name: str, page_num: int) -> Dict[str, Any]:
    """
    Extract metadata from text content for filtering.
    
    Args:
        page_text: Text from PDF page
        pdf_name: PDF filename
        page_num: Page number
        
    Returns:
        Metadata dict
    """
    text_lower = page_text.lower()
    
    # Detect hazard type
    hazard_type = "UNKNOWN"
    hazard_keywords = {
        "FIRE": ["fire", "firefighting", "flame", "burn", "extinguish"],
        "FLOOD": ["flood", "floodwater", "inundation", "deluge", "overflow"],
        "EARTHQUAKE": ["earthquake", "seismic", "tremor", "quake", " Richter"],
        "MEDICAL": ["medical", "health", "hospital", "patient", "injury"],
        "CHEMICAL": ["chemical", "toxic", "hazardous", "spill", "contamination"],
        "CYCLONE": ["cyclone", "hurricane", "typhoon", "storm", "wind"],
    }
    
    for h_type, keywords in hazard_keywords.items():
        if any(kw in text_lower for kw in keywords):
            hazard_type = h_type
            break
    
    # Detect state
    states = [
        "Uttarakhand", "Kerala", "Odisha", "Maharashtra", "Gujarat",
        "Tamil Nadu", "Andhra Pradesh", "Karnataka", "Rajasthan", "Bihar",
        "West Bengal", "Assam", "Uttar Pradesh", "Madhya Pradesh", "Chhattisgarh",
        "Jharkhand", "Himachal Pradesh", "Punjab", "Haryana", "Delhi",
    ]
    
    detected_state = "National"
    for state in states:
        if state.lower() in text_lower:
            detected_state = state
            break
    
    return {
        "source": f"{pdf_name}, p.{page_num}",
        "source_pdf": pdf_name,
        "page_num": page_num,
        "hazard_type": hazard_type,
        "state": detected_state,
    }


def ingest_documents(docs_dir: str = None) -> Dict[str, Any]:
    """
    Main ingestion pipeline.
    
    Args:
        docs_dir: Directory containing NDMA PDF documents
        
    Returns:
        Ingestion summary
    """
    if docs_dir is None:
        docs_dir = str(Path(__file__).parent.parent.parent / "data" / "ndma_docs")
    
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        logger.warning("docs_directory_not_found", path=str(docs_path))
        return {"error": f"Directory not found: {docs_path}"}
    
    pdf_files = list(docs_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("no_pdf_files_found", path=str(docs_path))
        return {"error": "No PDF files found in directory"}
    
    logger.info(
        "ingestion_started",
        docs_dir=str(docs_path),
        pdf_count=len(pdf_files),
    )
    
    # Initialize ChromaDB
    from rag.vector_store import get_chroma_client, get_or_create_collection, add_documents
    
    client = get_chroma_client()
    collection = get_or_create_collection(client)
    
    # Process each PDF
    total_chunks = 0
    states_covered = set()
    hazard_types_indexed = set()
    
    for pdf_file in pdf_files:
        logger.info("processing_pdf", pdf=pdf_file.name)
        
        # Extract text
        pages = extract_text_from_pdf(pdf_file)
        
        if not pages:
            logger.warning("no_text_extracted", pdf=pdf_file.name)
            continue
        
        # Chunk and embed
        documents = []
        metadatas = []
        ids = []
        
        for page in pages:
            chunks = chunk_text(page["text"])
            
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(
                    f"{pdf_file.name}_{page['page_num']}_{i}".encode()
                ).hexdigest()
                
                metadata = extract_metadata(
                    chunk,
                    pdf_file.name,
                    page["page_num"],
                )
                
                documents.append(chunk)
                metadatas.append(metadata)
                ids.append(chunk_id)
                
                states_covered.add(metadata["state"])
                hazard_types_indexed.add(metadata["hazard_type"])
        
        # Add to ChromaDB
        if documents:
            try:
                add_documents(
                    collection=collection,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )
                total_chunks += len(documents)
                logger.info(
                    "pdf_ingested",
                    pdf=pdf_file.name,
                    chunks=len(documents),
                )
            except Exception as e:
                logger.error(
                    "pdf_ingestion_failed",
                    pdf=pdf_file.name,
                    error=str(e),
                )
    
    summary = {
        "total_pdfs": len(pdf_files),
        "total_chunks": total_chunks,
        "states_covered": list(states_covered),
        "hazard_types_indexed": list(hazard_types_indexed),
        "collection_count": collection.count(),
    }
    
    logger.info("ingestion_completed", **summary)
    
    print("\n" + "=" * 50)
    print("NDMA Document Ingestion Summary")
    print("=" * 50)
    print(f"PDFs processed: {summary['total_pdfs']}")
    print(f"Chunks created: {summary['total_chunks']}")
    print(f"States covered: {', '.join(summary['states_covered'])}")
    print(f"Hazard types: {', '.join(summary['hazard_types_indexed'])}")
    print(f"Collection size: {summary['collection_count']} documents")
    print("=" * 50)
    
    return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest NDMA/SDMA documents into ChromaDB"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=None,
        help="Directory containing NDMA PDF documents",
    )
    
    args = parser.parse_args()
    
    result = ingest_documents(args.docs_dir)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print("\nIngestion completed successfully!")


if __name__ == "__main__":
    main()
