# src/services/vector_service.py
"""
Vector Database Service for resume similarity search
"""

import asyncio
import logging
import numpy as np
from typing import List, Optional
from abc import ABC, abstractmethod

from src.config import settings
from src.core.exceptions import VectorDatabaseException
from src.models import ResumeMatch, ResumeData

logger = logging.getLogger(__name__)


class BaseVectorService(ABC):
    """Abstract base class for vector database services"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        pass
    
    @abstractmethod
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[ResumeMatch]:
        """Find most similar resumes"""
        pass
    
    @abstractmethod
    async def add_resume(self, resume: ResumeData) -> bool:
        """Add resume to vector database"""
        pass
    
    @abstractmethod
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete resume from vector database"""
        pass


class ChromaDBVectorService(BaseVectorService):
    """ChromaDB vector database implementation"""
    
    def __init__(self):
        self.collection_name = settings.vector_db_collection
        self.embedding_model_name = settings.embedding_model
        
        # In production, initialize ChromaDB:
        # import chromadb
        # self.client = chromadb.Client()
        # self.collection = self.client.get_or_create_collection(self.collection_name)
        
        # Initialize embedding model
        # from sentence_transformers import SentenceTransformer
        # self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Simulated resume database for now
        self._init_sample_data()
        
        logger.info(f"Initialized ChromaDB service with collection: {self.collection_name}")
    
    def _init_sample_data(self):
        """Initialize sample resume data"""
        self.resumes = [
            ResumeData(
                id="resume_1",
                content="Senior Software Engineer with 5 years experience in Python, FastAPI, React, and AWS. Built scalable microservices...",
                skills=["Python", "FastAPI", "React", "AWS", "Docker", "Kubernetes"],
                experience_years=5,
                embedding=np.random.rand(settings.embedding_dimension).tolist()
            ),
            ResumeData(
                id="resume_2",
                content="Full Stack Developer specializing in TypeScript, Node.js, and cloud infrastructure. Led team of 3 developers...",
                skills=["TypeScript", "Node.js", "React", "GCP", "MongoDB"],
                experience_years=3,
                embedding=np.random.rand(settings.embedding_dimension).tolist()
            ),
            ResumeData(
                id="resume_3",
                content="Machine Learning Engineer with expertise in PyTorch, TensorFlow, and MLOps. Deployed models at scale...",
                skills=["Python", "PyTorch", "TensorFlow", "MLOps", "Kubernetes"],
                experience_years=4,
                embedding=np.random.rand(settings.embedding_dimension).tolist()
            ),
            ResumeData(
                id="resume_4",
                content="DevOps Engineer with 6 years experience in AWS, Azure, CI/CD pipelines, and infrastructure automation...",
                skills=["AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Jenkins"],
                experience_years=6,
                embedding=np.random.rand(settings.embedding_dimension).tolist()
            ),
            ResumeData(
                id="resume_5",
                content="Frontend Developer specializing in React, Vue.js, and modern web technologies. Built responsive UIs...",
                skills=["React", "Vue.js", "TypeScript", "CSS", "Webpack"],
                experience_years=4,
                embedding=np.random.rand(settings.embedding_dimension).tolist()
            ),
        ]
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        
        try:
            # In production:
            # embedding = self.embedding_model.encode(text)
            # return np.array(embedding)
            
            # Simulated embedding
            await asyncio.sleep(0.1)  # Simulate API call
            return np.random.rand(settings.embedding_dimension)
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise VectorDatabaseException("embedding", str(e))
    
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[ResumeMatch]:
        """Find most similar resumes using cosine similarity"""
        
        try:
            results = []
            
            for resume in self.resumes:
                resume_embedding = np.array(resume.embedding)
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, resume_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(resume_embedding)
                )
                
                # Filter by threshold
                if similarity >= settings.min_similarity_threshold:
                    results.append(
                        ResumeMatch(
                            resume_id=resume.id,
                            content=resume.content,
                            skills=resume.skills,
                            experience_years=resume.experience_years,
                            similarity_score=float(similarity)
                        )
                    )
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.info(f"Found {len(results)} matches, returning top {top_k}")
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise VectorDatabaseException("similarity search", str(e))
    
    async def add_resume(self, resume: ResumeData) -> bool:
        """Add resume to vector database"""
        
        try:
            # Generate embedding if not provided
            if not resume.embedding:
                embedding = await self.embed_text(resume.content)
                resume.embedding = embedding.tolist()
            
            # In production:
            # self.collection.add(
            #     ids=[resume.id],
            #     embeddings=[resume.embedding],
            #     documents=[resume.content],
            #     metadatas=[{
            #         "skills": resume.skills,
            #         "experience_years": resume.experience_years
            #     }]
            # )
            
            # Simulated add
            self.resumes.append(resume)
            logger.info(f"Added resume: {resume.id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add resume: {e}")
            raise VectorDatabaseException("add resume", str(e))
    
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete resume from vector database"""
        
        try:
            # In production:
            # self.collection.delete(ids=[resume_id])
            
            # Simulated delete
            self.resumes = [r for r in self.resumes if r.id != resume_id]
            logger.info(f"Deleted resume: {resume_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete resume: {e}")
            raise VectorDatabaseException("delete resume", str(e))


class PineconeVectorService(BaseVectorService):
    """Pinecone vector database implementation"""
    
    def __init__(self):
        # In production:
        # import pinecone
        # pinecone.init(api_key=settings.pinecone_api_key)
        # self.index = pinecone.Index(settings.pinecone_index)
        pass
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        # Implementation similar to ChromaDB
        return np.random.rand(settings.embedding_dimension)
    
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[ResumeMatch]:
        """Find most similar resumes"""
        # Implementation using Pinecone
        return []
    
    async def add_resume(self, resume: ResumeData) -> bool:
        """Add resume to Pinecone"""
        return True
    
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete resume from Pinecone"""
        return True


class VectorServiceFactory:
    """Factory for creating vector service instances"""
    
    @staticmethod
    def create() -> BaseVectorService:
        """Create vector service based on configuration"""
        
        db_type = settings.vector_db_type.lower()
        
        if db_type == "chromadb":
            logger.info("Using ChromaDB vector service")
            return ChromaDBVectorService()
        elif db_type == "pinecone":
            logger.info("Using Pinecone vector service")
            return PineconeVectorService()
        else:
            raise ValueError(f"Unsupported vector database type: {db_type}")


# Singleton instance
_vector_service: Optional[BaseVectorService] = None


def get_vector_service() -> BaseVectorService:
    """Get vector service instance (singleton)"""
    global _vector_service
    
    if _vector_service is None:
        _vector_service = VectorServiceFactory.create()
    
    return _vector_service