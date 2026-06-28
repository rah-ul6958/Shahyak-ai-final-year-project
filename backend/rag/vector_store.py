"""
SAHAYAK-AI Vector Store

ChromaDB-based persistent vector storage for offline RAG.
"""

from typing import Dict, List, Optional, Any

import chromadb
from chromadb import Collection
from chromadb.config import Settings as ChromaSettings

import structlog

from config import settings

logger = structlog.get_logger(__name__)

# Collection name for NDMA protocols
COLLECTION_NAME = "ndma_protocols"


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Get ChromaDB persistent client.

    Returns:
        ChromaDB PersistentClient with offline configuration
    """
    return chromadb.PersistentClient(
        path=str(settings.chroma_path),
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True,
        ),
    )


def get_or_create_collection(
    client: Optional[chromadb.PersistentClient] = None,
    name: str = COLLECTION_NAME,
) -> Collection:
    """
    Get or create a ChromaDB collection.

    Args:
        client: ChromaDB client (creates new if None)
        name: Collection name

    Returns:
        ChromaDB Collection
    """
    if client is None:
        client = get_chroma_client()

    try:
        collection = client.get_collection(name=name)
        logger.info("collection_exists", name=name)
    except Exception:
        collection = client.create_collection(
            name=name,
            metadata={"description": "NDMA/SDMA disaster protocols"},
            get_or_create=True,
        )
        logger.info("collection_created", name=name)

    return collection


def add_documents(
    collection: Collection,
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    ids: Optional[List[str]] = None,
) -> List[str]:
    """
    Add documents to a collection.

    Args:
        collection: ChromaDB collection
        documents: List of document texts
        metadatas: List of metadata dicts
        ids: Optional list of document IDs (generated if None)

    Returns:
        List of document IDs
    """
    if ids is None:
        ids = [f"doc_{i}" for i in range(len(documents))]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    logger.info(
        "documents_added",
        count=len(documents),
        collection=collection.name,
    )

    return ids


def query_collection(
    collection: Collection,
    query_embeddings: List[List[float]],
    n_results: int = 10,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query a ChromaDB collection.

    Args:
        collection: ChromaDB collection
        query_embeddings: Query embedding vectors
        n_results: Number of results to return
        where: Metadata filter
        where_document: Document content filter

    Returns:
        Query results dict
    """
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results,
        where=where,
        where_document=where_document,
        include=["documents", "metadatas", "distances"],
    )

    return results


def delete_collection(name: str = COLLECTION_NAME) -> None:
    """
    Delete a collection.

    Args:
        name: Collection name
    """
    client = get_chroma_client()
    try:
        client.delete_collection(name=name)
        logger.info("collection_deleted", name=name)
    except Exception as e:
        logger.warning("collection_delete_error", error=str(e))


def get_collection_stats(collection: Collection) -> Dict[str, Any]:
    """
    Get collection statistics.

    Args:
        collection: ChromaDB collection

    Returns:
        Dict with collection stats
    """
    return {
        "name": collection.name,
        "count": collection.count(),
        "metadata": collection.metadata,
    }