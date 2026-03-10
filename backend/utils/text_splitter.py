"""
Text Splitter Utility
Helper functions for splitting contract text into manageable chunks
"""
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class ContractTextSplitter:
    """Utility class for splitting contract text into clauses and sections"""
    
    def __init__(self, max_chunk_size: int = 3000, overlap: int = 100):
        """
        Initialize the text splitter
        
        Args:
            max_chunk_size: Maximum size of each text chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def split_by_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text by numbered sections and subsections
        
        Args:
            text: The contract text to split
            
        Returns:
            List of tuples (section_id, section_text)
        """
        sections = []
        
        # Pattern to match numbered sections (1., 2., etc.) and subsections (1.1, 1.a, etc.)
        section_pattern = r'(?=\n\s*(\d+(?:\.\d+|\.[a-zA-Z]?)\.?\s+.*?(?=\n\s*\d+|\n\s*[A-Z]\.|\n\s*\([a-zA-Z]\)|\Z)))'
        
        try:
            # Find all section matches
            matches = re.finditer(section_pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                section_start = match.start()
                section_text = match.group(1).strip()
                
                # Extract section number/title
                section_id_match = re.match(r'(\d+(?:\.\d+|\.[a-zA-Z]?)\.?)', section_text)
                section_id = section_id_match.group(1) if section_id_match else f"section_{len(sections) + 1}"
                
                # Get the full section content
                # Look ahead to find where this section ends
                remaining_text = text[section_start:]
                next_section_match = re.search(r'\n\s*(\d+(?:\.\d+|\.[a-zA-Z]?)\.?\s+)', remaining_text[1:])
                
                if next_section_match:
                    section_content = remaining_text[:next_section_match.start() + 1].strip()
                else:
                    section_content = remaining_text.strip()
                
                sections.append((section_id, section_content))
            
            # If no sections found, try alternative patterns
            if not sections:
                sections = self._split_by_alternative_patterns(text)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error splitting by sections: {str(e)}")
            return self._fallback_split(text)
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text by paragraphs
        
        Args:
            text: The contract text to split
            
        Returns:
            List of paragraph strings
        """
        try:
            # Split by double newlines (paragraph breaks)
            paragraphs = re.split(r'\n\s*\n', text)
            
            # Filter out empty paragraphs and very short ones
            filtered_paragraphs = []
            for para in paragraphs:
                cleaned_para = para.strip()
                if len(cleaned_para) > 20:  # Only keep substantial paragraphs
                    filtered_paragraphs.append(cleaned_para)
            
            return filtered_paragraphs
            
        except Exception as e:
            logger.error(f"Error splitting by paragraphs: {str(e)}")
            return [text]
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text by sentences
        
        Args:
            text: The contract text to split
            
        Returns:
            List of sentence strings
        """
        try:
            # Simple sentence splitting pattern
            sentence_pattern = r'(?<=[.!?])\s+'
            sentences = re.split(sentence_pattern, text)
            
            # Filter and clean sentences
            filtered_sentences = []
            for sentence in sentences:
                cleaned_sentence = sentence.strip()
                if len(cleaned_sentence) > 10:  # Only keep substantial sentences
                    filtered_sentences.append(cleaned_sentence)
            
            return filtered_sentences
            
        except Exception as e:
            logger.error(f"Error splitting by sentences: {str(e)}")
            return [text]
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into chunks of specified size with overlap
        
        Args:
            text: The contract text to split
            
        Returns:
            List of text chunks
        """
        try:
            if len(text) <= self.max_chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text):
                # Calculate end position
                end = start + self.max_chunk_size
                
                # If this isn't the last chunk, try to break at a sentence boundary
                if end < len(text):
                    # Look for sentence boundary near the end
                    sentence_boundary = text.rfind('.', start, end)
                    if sentence_boundary > start + self.max_chunk_size // 2:
                        end = sentence_boundary + 1
                    else:
                        # Try other punctuation
                        for punct in ['!', '?', '\n']:
                            boundary = text.rfind(punct, start, end)
                            if boundary > start + self.max_chunk_size // 2:
                                end = boundary + 1
                                break
                
                # Extract chunk
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                # Move start position with overlap
                start = max(start + 1, end - self.overlap)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting into chunks: {str(e)}")
            return [text]
    
    def _split_by_alternative_patterns(self, text: str) -> List[Tuple[str, str]]:
        """Try alternative patterns for section splitting"""
        sections = []
        
        # Try splitting by common clause headers
        clause_headers = [
            r'\n\s*(WHEREAS|NOW\s+THEREFORE|ARTICLE\s+\d+|SECTION\s+\d+)\s*[:\.]?\s*',
            r'\n\s*(Payment|Termination|Liability|Confidentiality|Indemnification|Warranty|Governing\s+Law|Dispute\s+Resolution|Force\s+Majeure)\s*[:\.]?\s*',
            r'\n\s*([A-Z][A-Z\s]+)\s*[:\.]?\s*'
        ]
        
        for pattern in clause_headers:
            try:
                matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
                if len(matches) > 1:  # Found multiple matches
                    for i, match in enumerate(matches):
                        header = match.group(1).strip()
                        section_id = f"clause_{i+1}_{header.lower().replace(' ', '_')}"
                        
                        # Get content until next header or end
                        start = match.start()
                        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                        content = text[start:end].strip()
                        
                        sections.append((section_id, content))
                    
                    if sections:
                        break
                        
            except Exception as e:
                logger.debug(f"Pattern {pattern} failed: {str(e)}")
                continue
        
        return sections or self._fallback_split(text)
    
    def _fallback_split(self, text: str) -> List[Tuple[str, str]]:
        """Fallback splitting method"""
        try:
            # Split by paragraphs as fallback
            paragraphs = self.split_by_paragraphs(text)
            return [(f"paragraph_{i+1}", para) for i, para in enumerate(paragraphs)]
        except Exception:
            return [("full_text", text)]
    
    def extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms and definitions from the text
        
        Args:
            text: The contract text to analyze
            
        Returns:
            List of key terms found
        """
        key_terms = []
        
        # Common patterns for definitions
        definition_patterns = [
            r'"([^"]+)"\s+means?',
            r'([A-Z][A-Z\s]+)\s+shall mean',
            r'([A-Z][A-Z\s]+)\s+refers to',
            r'defined as\s+"([^"]+)"',
            r'term\s+"([^"]+)"'
        ]
        
        for pattern in definition_patterns:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    term = match.group(1).strip()
                    if len(term) > 2 and term not in key_terms:
                        key_terms.append(term)
            except Exception as e:
                logger.debug(f"Definition pattern {pattern} failed: {str(e)}")
        
        return key_terms
    
    def identify_clause_types(self, section_text: str) -> List[str]:
        """
        Identify the type(s) of a clause based on its content
        
        Args:
            section_text: The text of the clause/section
            
        Returns:
            List of identified clause types
        """
        clause_types = []
        text_lower = section_text.lower()
        
        # Clause type keywords
        type_keywords = {
            "Payment": ["payment", "fee", "cost", "invoice", "billing", "compensation"],
            "Termination": ["terminate", "termination", "end", "cancel", "expiration"],
            "Liability": ["liability", "limit", "damage", "responsibility", "liable"],
            "Confidentiality": ["confidential", "proprietary", "trade secret", "non-disclosure"],
            "Intellectual Property": ["intellectual property", "copyright", "trademark", "patent"],
            "Indemnification": ["indemnify", "indemnification", "hold harmless"],
            "Governing Law": ["governing law", "jurisdiction", "applicable law"],
            "Dispute Resolution": ["dispute", "arbitration", "mediation", "litigation"],
            "Force Majeure": ["force majeure", "act of god", "unforeseeable"],
            "Warranty": ["warranty", "guarantee", "represent", "warrant"],
            "Non-Compete": ["non-compete", "competition", "compete"],
            "Assignment": ["assignment", "assign", "transfer"],
            "Amendment": ["amendment", "amend", "modify", "modification"]
        }
        
        for clause_type, keywords in type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                clause_types.append(clause_type)
        
        return clause_types or ["General"]
