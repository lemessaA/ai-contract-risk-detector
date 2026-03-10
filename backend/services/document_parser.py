"""
Document Parser Service - Agent 1
Extracts plain text from contract documents (PDF, DOCX, TXT)
"""
import os
import json
from typing import Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

class DocumentParserAgent:
    """Agent responsible for parsing contract documents and extracting text"""
    
    def __init__(self):
        """Initialize the document parser agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
        self.system_prompt = """
You are an AI document processing specialist. Your task is to extract and clean text from legal documents.

Instructions:
1. Extract all text content from the provided document
2. Clean up formatting issues (extra spaces, broken lines, etc.)
3. Preserve the logical structure and paragraph breaks
4. Remove any headers, footers, or page numbers that are not part of the actual content
5. Ensure the text is readable and well-formatted

Return the cleaned text in a structured JSON format:
{
    "success": true/false,
    "text": "extracted and cleaned text",
    "word_count": number_of_words,
    "page_count": number_of_pages,
    "file_type": "pdf/docx/txt",
    "error": "error_message_if_any"
}
"""
    
    async def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse document and extract text
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing parsed text and metadata
        """
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            
            # Extract text based on file type
            if file_extension == ".pdf":
                raw_text = self._extract_from_pdf(file_path)
                page_count = self._get_pdf_page_count(file_path)
            elif file_extension == ".docx":
                raw_text = self._extract_from_docx(file_path)
                page_count = None  # DOCX doesn't have clear page boundaries
            elif file_extension == ".txt":
                raw_text = self._extract_from_txt(file_path)
                page_count = None
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_extension}",
                    "text": "",
                    "word_count": 0,
                    "page_count": 0,
                    "file_type": file_extension
                }
            
            # Use LLM to clean and structure the text
            cleaned_result = await self._clean_text_with_llm(raw_text, file_extension)
            
            # Add page count if available
            if page_count:
                cleaned_result["page_count"] = page_count
            
            return cleaned_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "word_count": 0,
                "page_count": 0,
                "file_type": Path(file_path).suffix.lower()
            }
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _get_pdf_page_count(self, file_path: Path) -> int:
        """Get page count from PDF file"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    async def _clean_text_with_llm(self, raw_text: str, file_type: str) -> Dict[str, Any]:
        """
        Use LLM to clean and structure the extracted text
        
        Args:
            raw_text: Raw text extracted from document
            file_type: Type of file processed
            
        Returns:
            Dictionary with cleaned text and metadata
        """
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Please clean and structure the following text from a {file_type} file:\n\n{raw_text}")
            ]
            
            response = await self.llm.ainvoke(messages)
            result_text = response.content
            
            # Try to parse as JSON, fallback to text response
            try:
                result = json.loads(result_text)
                # Ensure required fields are present
                if "success" not in result:
                    result["success"] = True
                if "file_type" not in result:
                    result["file_type"] = file_type
                if "word_count" not in result:
                    result["word_count"] = len(result_text.split())
                return result
            except json.JSONDecodeError:
                # Fallback: create structured response manually
                return {
                    "success": True,
                    "text": result_text,
                    "word_count": len(result_text.split()),
                    "page_count": 0,
                    "file_type": file_type,
                    "error": None
                }
                
        except Exception as e:
            # Fallback to basic text processing
            return {
                "success": True,
                "text": raw_text.strip(),
                "word_count": len(raw_text.split()),
                "page_count": 0,
                "file_type": file_type,
                "error": f"LLM cleaning failed: {str(e)}"
            }
