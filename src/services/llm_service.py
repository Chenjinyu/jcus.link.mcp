# src/services/llm_service.py
"""
LLM Service for resume generation and text processing
"""

import asyncio
import logging
from typing import AsyncIterator, List, Optional, AsyncGenerator
from abc import ABC, abstractmethod

from ..config import settings
from ..core.exceptions import LLMServiceException
from ..schemas import ResumeMatch

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    async def generate_resume(
        self,
        job_description: str,
        matched_resumes: List[ResumeMatch],
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate resume based on job description and matches"""
        pass
    
    @abstractmethod
    async def analyze_text(self, text: str) -> dict:
        """Analyze text and extract structured information"""
        pass


class AnthropicLLMService(BaseLLMService):
    """Anthropic Claude LLM service implementation"""
    
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        
        if not self.api_key:
            logger.warning("Anthropic API key not set, using simulated responses")
        
        # In production, initialize the client:
        # from anthropic import Anthropic
        # self.client = Anthropic(api_key=self.api_key)
    
    async def generate_resume(
        self,
        job_description: str,
        matched_resumes: List[ResumeMatch],
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate optimized resume using Claude"""
        
        try:
            prompt = self._build_resume_prompt(job_description, matched_resumes)
            
            if stream:
                async for chunk in self._stream_generate(prompt):
                    yield chunk
            else:
                result = await self._generate(prompt)
                yield result
        
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise LLMServiceException("resume generation", str(e))
    
    async def analyze_text(self, text: str) -> dict:
        """Analyze job description using Claude"""
        
        try:
            prompt = self._build_analysis_prompt(text)
            response = await self._generate(prompt)
            
            # Parse response into structured format
            # In production, use structured outputs or JSON mode
            return {
                "required_skills": ["Python", "FastAPI", "React", "AWS"],
                "experience_level": "Senior",
                "key_responsibilities": [
                    "Design and implement scalable systems",
                    "Lead technical projects",
                    "Mentor junior developers"
                ],
                "estimated_match_threshold": 0.7
            }
        
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            raise LLMServiceException("text analysis", str(e))
    
    def _build_resume_prompt(
        self,
        job_description: str,
        matched_resumes: List[ResumeMatch]
    ) -> str:
        """Build prompt for resume generation"""
        
        context = "Matched candidate profiles:\n\n"
        for i, resume in enumerate(matched_resumes, 1):
            context += f"{i}. Skills: {', '.join(resume.skills)}\n"
            context += f"   Experience: {resume.experience_years} years\n"
            context += f"   Match Score: {resume.similarity_score:.2f}\n\n"
        
        return f"""Based on this job description and matched candidate profiles, generate an optimized resume.

Job Description:
{job_description}

{context}

Generate a professional resume that highlights relevant skills and experience for this role.
Include:
- Professional Summary
- Key Skills
- Work Experience (tailored to job requirements)
- Education
- Notable Achievements

Format in clean, professional markdown.
"""
    
    def _build_analysis_prompt(self, text: str) -> str:
        """Build prompt for job description analysis"""
        
        return f"""Analyze this job description and extract key information:

{text}

Provide:
1. Required skills (list)
2. Experience level (Entry/Mid/Senior/Lead)
3. Key responsibilities (list)
4. Estimated match threshold (0.0-1.0)

Format as JSON.
"""
    
    async def _stream_generate(self, prompt: str) -> AsyncIterator[str]:
        """Stream LLM response (simulated for now)"""
        
        if self.api_key:
            # In production:
            # stream = await self.client.messages.create(
            #     model=self.model,
            #     max_tokens=self.max_tokens,
            #     messages=[{"role": "user", "content": prompt}],
            #     stream=True
            # )
            # async for chunk in stream:
            #     if chunk.type == "content_block_delta":
            #         yield chunk.delta.text
            pass
        
        # Simulated streaming response
        resume_parts = [
            "# Professional Resume\n\n",
            "## Professional Summary\n",
            "Experienced software engineer with strong background in Python, TypeScript, and cloud technologies. ",
            "Proven track record of building scalable applications and leading development teams.\n\n",
            "## Key Skills\n",
            "- **Programming Languages:** Python, TypeScript, JavaScript\n",
            "- **Frameworks:** FastAPI, React, Node.js\n",
            "- **Cloud Platforms:** AWS, GCP\n",
            "- **Tools:** Docker, Kubernetes, Git\n\n",
            "## Work Experience\n\n",
            "### Senior Software Engineer | Tech Company\n",
            "*2020 - Present*\n\n",
            "- Developed microservices architecture serving 1M+ users\n",
            "- Led team of 5 engineers in implementing CI/CD pipeline\n",
            "- Reduced deployment time by 60% through automation\n\n",
            "## Education\n",
            "**Bachelor of Science in Computer Science**\n",
            "University Name, 2018\n\n",
            "## Achievements\n",
            "- Architected system handling 10K requests/second\n",
            "- Published 3 technical articles on Medium\n",
            "- Contributed to 5+ open source projects\n"
        ]
        
        for part in resume_parts:
            await asyncio.sleep(0.1)  # Simulate generation delay
            yield part
    
    async def _generate(self, prompt: str) -> str:
        """Generate complete response"""
        
        result = []
        async for chunk in self._stream_generate(prompt):
            result.append(chunk)
        return "".join(result)


class OpenAILLMService(BaseLLMService):
    """OpenAI GPT service implementation"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        
        # In production:
        # from openai import AsyncOpenAI
        # self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate_resume(
        self,
        job_description: str,
        matched_resumes: List[ResumeMatch],
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate resume using OpenAI"""
        # Implementation similar to Anthropic
        yield "OpenAI implementation"
    
    async def analyze_text(self, text: str) -> dict:
        """Analyze text using OpenAI"""
        # Implementation similar to Anthropic
        return {}


class LLMServiceFactory:
    """Factory for creating LLM service instances"""
    
    @staticmethod
    def create() -> BaseLLMService:
        """Create LLM service based on configuration"""
        
        provider = settings.llm_provider.lower()
        
        if provider == "anthropic":
            logger.info("Using Anthropic LLM service")
            return AnthropicLLMService()
        elif provider == "openai":
            logger.info("Using OpenAI LLM service")
            return OpenAILLMService()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


# Singleton instance
_llm_service: Optional[BaseLLMService] = None


def get_llm_service() -> BaseLLMService:
    """Get LLM service instance (singleton)"""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMServiceFactory.create()
    
    return _llm_service