"""LLM service for resume generation and job description analysis."""

import asyncio
import logging
from typing import List, Dict, Any, AsyncIterator

from anthropic import AsyncAnthropic

from src.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service for resume generation and analysis."""

    def __init__(self) -> None:
        """Initialize LLM client."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set, using mock responses")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_resume(
        self,
        job_description: str,
        matched_resumes: List[Dict[str, Any]],
        stream: bool = True,
    ) -> AsyncIterator[str]:
        """
        Generate updated resume based on job description and matches.

        Args:
            job_description: The job description text
            matched_resumes: List of matched resume profiles with similarity scores
            stream: Whether to stream the response

        Yields:
            Chunks of the generated resume text
        """
        # Build context from matched resumes
        context = "Matched candidate profiles:\n\n"
        for i, resume in enumerate(matched_resumes, 1):
            skills = resume.get("skills", [])
            experience = resume.get("experience_years", 0)
            score = resume.get("similarity_score", 0.0)

            context += f"{i}. Skills: {', '.join(skills) if isinstance(skills, list) else 'N/A'}\n"
            context += f"   Experience: {experience} years\n"
            context += f"   Match Score: {score:.2f}\n\n"

        prompt = f"""Based on this job description and matched candidate profiles, generate an optimized resume.

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

        if stream:
            async for chunk in self._stream_generate(prompt):
                yield chunk
        else:
            response = await self._generate(prompt)
            yield response

    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key requirements.

        Args:
            job_description: The job description text

        Returns:
            Dictionary with extracted information
        """
        if not self.client:
            # Fallback analysis
            return {
                "required_skills": [],
                "experience_level": "Unknown",
                "key_responsibilities": [],
                "estimated_match_threshold": 0.5,
            }

        prompt = f"""Analyze this job description and extract key information:

{job_description}

Extract and return a JSON object with:
- required_skills: List of required technical skills
- experience_level: Senior/Mid/Junior
- key_responsibilities: List of main responsibilities
- estimated_match_threshold: Float between 0 and 1 indicating match difficulty

Return only valid JSON, no markdown formatting."""

        try:
            message = await self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            response_text = message.content[0].text if message.content else "{}"

            # Parse JSON response
            import json

            try:
                analysis = json.loads(response_text)
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON, using fallback")
                return {
                    "required_skills": [],
                    "experience_level": "Unknown",
                    "key_responsibilities": [],
                    "estimated_match_threshold": 0.5,
                }

        except Exception as e:
            logger.error(f"Error analyzing job description: {e}")
            raise
    
    async def _stream_generate(self, prompt: str) -> AsyncIterator[str]:
        """Stream LLM response."""
        if not self.client:
            # Fallback: simulated streaming response
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
                "- Contributed to 5+ open source projects\n",
            ]

            for part in resume_parts:
                await asyncio.sleep(0.1)  # Simulate generation delay
                yield part
            return

        # Use actual LLM streaming
        try:
            async with self.client.messages.stream(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Error streaming LLM response: {e}")
            raise

    async def _generate(self, prompt: str) -> str:
        """Generate complete response (non-streaming)."""
        if not self.client:
            # Fallback: return simulated response
            result = []
            async for chunk in self._stream_generate(prompt):
                result.append(chunk)
            return "".join(result)

        try:
            message = await self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text if message.content else ""

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise