"""Vector database for storing and searching resume embeddings."""

import asyncio
import logging
from typing import List, Dict, Any

import numpy as np

from src.config import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    Vector database for storing and searching resume embeddings.

    Currently uses in-memory storage. In production, replace with:
    - ChromaDB
    - Pinecone
    - Weaviate
    - Supabase with pgvector
    """

    def __init__(self) -> None:
        """Initialize vector database."""
        # In production, initialize actual vector DB
        # Example with ChromaDB:
        # import chromadb
        # self.client = chromadb.Client()
        # self.collection = self.client.get_or_create_collection("resumes")

        # Simulated resume database
        self.resumes: List[Dict[str, Any]] = [
            {
                "id": "resume_1",
                "content": "Senior Software Engineer with 5 years experience in Python, FastAPI, React, and AWS. Built scalable microservices...",
                "skills": ["Python", "FastAPI", "React", "AWS", "Docker", "Kubernetes"],
                "experience_years": 5,
                "embedding": np.random.rand(settings.EMBEDDING_DIMENSION),
            },
            {
                "id": "resume_2",
                "content": "Full Stack Developer specializing in TypeScript, Node.js, and cloud infrastructure. Led team of 3 developers...",
                "skills": ["TypeScript", "Node.js", "React", "GCP", "MongoDB"],
                "experience_years": 3,
                "embedding": np.random.rand(settings.EMBEDDING_DIMENSION),
            },
            {
                "id": "resume_3",
                "content": "Machine Learning Engineer with expertise in PyTorch, TensorFlow, and MLOps. Deployed models at scale...",
                "skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "Kubernetes"],
                "experience_years": 4,
                "embedding": np.random.rand(settings.EMBEDDING_DIMENSION),
            },
        ]
    
    async def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        # In production, use actual embedding model:
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer(settings.EMBEDDING_MODEL)
        # embedding = await asyncio.to_thread(model.encode, text)
        # return np.array(embedding)

        # Simulated embedding (for development)
        await asyncio.sleep(0.1)  # Simulate API call
        return np.random.rand(settings.EMBEDDING_DIMENSION)

    async def similarity_search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar resumes using cosine similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return

        Returns:
            List of matched resumes with similarity scores
        """
        results: List[Dict[str, Any]] = []

        for resume in self.resumes:
            # Calculate cosine similarity
            embedding = resume["embedding"]
            dot_product = np.dot(query_embedding, embedding)
            norm_product = np.linalg.norm(query_embedding) * np.linalg.norm(embedding)

            if norm_product == 0:
                similarity = 0.0
            else:
                similarity = dot_product / norm_product

            results.append(
                {
                    "resume_id": resume["id"],
                    "content": resume["content"],
                    "skills": resume["skills"],
                    "experience_years": resume["experience_years"],
                    "similarity_score": float(similarity),
                }
            )

        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    async def add_resume(
        self, resume_id: str, content: str, skills: List[str], experience_years: int
    ) -> None:
        """
        Add a new resume to the database.

        Args:
            resume_id: Unique identifier for the resume
            content: Resume content text
            skills: List of skills
            experience_years: Years of experience
        """
        embedding = await self.embed_text(content)

        self.resumes.append(
            {
                "id": resume_id,
                "content": content,
                "skills": skills,
                "experience_years": experience_years,
                "embedding": embedding,
            }
        )

        logger.info(f"Added resume {resume_id} to database")