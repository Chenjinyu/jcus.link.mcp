# src/models/__init__.py
"""Data models module"""

from .domain_models import (
    ResumeMatch,
    JobAnalysis,
    SearchMatchesRequest,
    SearchMatchesResponse,
    AnalyzeJobRequest,
    GenerateResumeRequest,
    UploadJobResponse,
    ResumeData,
)

__all__ = [
    "ResumeMatch",
    "JobAnalysis",
    "SearchMatchesRequest",
    "SearchMatchesResponse",
    "AnalyzeJobRequest",
    "GenerateResumeRequest",
    "UploadJobResponse",
    "ResumeData",
]