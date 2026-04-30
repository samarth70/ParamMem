import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CrossSampleMemory:
    """
    Cross-Sample Memory Retrieval Pipeline for ParamAgent-plus.
    Uses ChromaDB to retrieve relevant reasoning patterns from past experiences.
    """
    def __init__(self, db_path: str = "./data/chroma_db", collection_name: str = "trajectory_bank"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Initialized CrossSampleMemory at {db_path} with collection '{collection_name}'")

    def add_trajectory(self, trajectory_id: str, problem_description: str, final_reflection: str, metadata: Dict[str, Any] = None):
        """
        Stores a successful reasoning trajectory and reflection into the bank.
        """
        if metadata is None:
            metadata = {}
            
        # We index based on the problem description to find similar problems later
        self.collection.add(
            documents=[problem_description],
            metadatas=[{"reflection": final_reflection, **metadata}],
            ids=[trajectory_id]
        )
        logger.debug(f"Added trajectory {trajectory_id} to memory bank.")

    def retrieve_similar_patterns(self, current_problem: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves relevant cross-sample reasoning patterns based on the current problem context.
        """
        if self.collection.count() == 0:
            return []

        # Query the DB for similar problem descriptions
        results = self.collection.query(
            query_texts=[current_problem],
            n_results=min(n_results, self.collection.count())
        )
        
        retrieved_patterns = []
        if results['metadatas'] and len(results['metadatas'][0]) > 0:
            for metadata in results['metadatas'][0]:
                retrieved_patterns.append(metadata)
                
        return retrieved_patterns
