from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from typing import Optional
import asyncio

from app.config import get_settings

settings = get_settings()


def get_document_intelligence_client() -> Optional[DocumentIntelligenceClient]:
    """Get Azure Document Intelligence client if configured."""
    if not settings.azure_doc_intel_endpoint or not settings.azure_doc_intel_key:
        return None

    return DocumentIntelligenceClient(
        endpoint=settings.azure_doc_intel_endpoint,
        credential=AzureKeyCredential(settings.azure_doc_intel_key)
    )


async def parse_resume(file_bytes: bytes) -> str:
    """
    Parse a resume PDF using Azure Document Intelligence.

    Args:
        file_bytes: Raw PDF file content

    Returns:
        Extracted text content from the resume
    """
    client = get_document_intelligence_client()

    if client is None:
        # Fallback: return placeholder for development without Azure
        return "[Resume parsing unavailable - Azure Document Intelligence not configured]"

    # Run in executor since the SDK is synchronous
    loop = asyncio.get_event_loop()

    def _analyze():
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            body=file_bytes,
            content_type="application/pdf"
        )
        result = poller.result()
        return result.content

    text = await loop.run_in_executor(None, _analyze)
    return text


async def extract_resume_info(resume_text: str) -> dict:
    """
    Extract structured information from resume text using LLM.

    This extracts:
    - Experience level estimate
    - Technical skills mentioned
    - Areas of expertise
    - Potential weak areas (gaps in common skills)

    Args:
        resume_text: Raw text extracted from resume

    Returns:
        Dictionary with structured resume information
    """
    # This will be enhanced with LLM analysis
    # For now, return a basic structure
    return {
        "raw_text": resume_text,
        "experience_level": "unknown",  # junior, mid, senior, staff
        "skills_mentioned": [],
        "areas_of_expertise": [],
        "potential_gaps": []
    }
