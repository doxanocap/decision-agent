"""
Decision Engine - Simplified RAG for MVP.
Only dense retrieval, no sparse vectors or reranking.
"""

from typing import List, Dict, Any
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from FlagEmbedding import BGEM3FlagModel

from server.core.config import config


class DecisionEngine:
    def __init__(self):
        print("Initializing DecisionEngine...")
        self.qdrant = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        
        print(f"Loading Embedding Model: {config.EMBEDDING_MODEL}")
        self.embedding_model = BGEM3FlagModel(config.EMBEDDING_MODEL, use_fp16=True)

        self._ensure_collection()
        print("DecisionEngine Initialized.")

    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        if not self.qdrant.collection_exists(config.QDRANT_COLLECTION):
            print(f"Creating collection {config.QDRANT_COLLECTION}...")
            self.qdrant.create_collection(
                collection_name=config.QDRANT_COLLECTION,
                vectors_config={
                    "dense": models.VectorParams(
                        size=1024,
                        distance=models.Distance.COSINE
                    )
                }
            )

    def _generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def index_decision(self, decision_id: str, context: str, arguments: List[Dict[str, str]]):
        """Index a decision and its arguments into Qdrant with content hashing."""
        # For simplicity, we index the whole context + arguments as one point
        # In a more advanced RAG, we might index each argument separately
        canonical_text = f"Context: {context}\n" + "\n".join([f"- {a['text']}" for a in arguments])
        content_hash = self._generate_hash(canonical_text)
        
        # Check if already indexed
        scroll_result, _ = self.qdrant.scroll(
            collection_name=config.QDRANT_COLLECTION,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="content_hash",
                        match=models.MatchValue(value=content_hash)
                    )
                ]
            ),
            limit=1
        )
        
        if scroll_result:
            return  # Duplicate

        # Encode (dense only)
        output = self.embedding_model.encode([canonical_text], return_dense=True)
        query_dense = output['dense_vecs'][0]

        # Upsert
        self.qdrant.upsert(
            collection_name=config.QDRANT_COLLECTION,
            points=[
                models.PointStruct(
                    id=decision_id,
                    vector={"dense": query_dense.tolist()},
                    payload={
                        "decision_id": decision_id,
                        "canonical_text": canonical_text,
                        "content_hash": content_hash
                    }
                )
            ]
        )

    def simple_retrieval(self, query: str, top_k: int = 3) -> List[str]:
        """
        Simple RAG: dense retrieval only, no reranking.
        
        Args:
            query: search query
            top_k: number of results
            
        Returns:
            List of similar argument texts
        """
        # Encode query (dense only)
        output = self.embedding_model.encode(
            [query], 
            return_dense=True, 
            return_sparse=False,
            return_colbert_vecs=False
        )
        query_dense = output['dense_vecs'][0]
        
        # Search in Qdrant
        response = self.qdrant.query_points(
            collection_name=config.QDRANT_COLLECTION,
            query=query_dense.tolist(),
            using="dense",
            limit=top_k,
            with_payload=True,
        )
        
        # Extract texts
        results = []
        for point in response.points:
            canonical_text = point.payload.get("canonical_text", "")
            if canonical_text:
                results.append(canonical_text)
        
        return results


    def delete_decision_vectors(self, decision_id: str):
        """Delete vectors associated with a decision ID."""
        try:
            self.qdrant.delete(
                collection_name=config.QDRANT_COLLECTION,
                points_selector=models.PointIdsList(
                    points=[decision_id]
                )
            )
            print(f"Deleted vectors for decision {decision_id}")
        except Exception as e:
            print(f"Error deleting vectors for {decision_id}: {e}")

# Singleton
engine = DecisionEngine()
