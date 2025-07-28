"""
Common PDF processing utilities
"""

# Try to import PyMuPDF, fallback to text processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    print("Warning: PyMuPDF not available. Using text file fallback.")
    PYMUPDF_AVAILABLE = False

import re
import statistics
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Import our text fallback
from shared.text_utils import extract_document_structure as extract_text_structure, TextBlock


def extract_document_content(file_path: str) -> Dict:
    """
    Extract content from PDF or text file
    """
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith('.txt'):
        # Handle text files
        return extract_text_structure(file_path)
    elif file_path_lower.endswith('.pdf') and PYMUPDF_AVAILABLE:
        # Handle PDF files with PyMuPDF
        return extract_pdf_content(file_path)
    elif file_path_lower.endswith('.pdf') and not PYMUPDF_AVAILABLE:
        # PDF requested but PyMuPDF not available
        print(f"Warning: PyMuPDF not available for PDF {file_path}. Please install PyMuPDF or provide a text file.")
        return {'text_blocks': [], 'headings': [], 'statistics': {'total_blocks': 0, 'avg_font_size': 12.0, 'font_sizes': [12.0]}}
    else:
        print(f"Unsupported file type: {file_path}")
        return {'text_blocks': [], 'headings': [], 'statistics': {'total_blocks': 0, 'avg_font_size': 12.0, 'font_sizes': [12.0]}}


def extract_pdf_content(file_path: str) -> Dict:
    """
    Extract content from PDF file using PyMuPDF
    """
    ## added pdf extraction logic
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF not available")
    
    import fitz  # PyMuPDF
    doc = fitz.open(file_path)
    text_blocks = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b[:7]
            cleaned_text = clean_text(text)  # <--- Clean the text here
            if cleaned_text:
                text_block = TextBlock(
                    text=cleaned_text,
                    page_num=page_num + 1,
                    bbox=(x0, y0, x1, y1),
                    font_size=12.0,
                    font_name="Unknown",
                    font_flags=0,
                    line_height=14.0
                )
                text_blocks.append(text_block)
    from shared.text_utils import detect_headings_from_text, get_text_statistics
    headings = detect_headings_from_text(text_blocks)
    statistics = get_text_statistics(text_blocks)
    return {
        'text_blocks': text_blocks,
        'headings': headings,
        'statistics': statistics
    }


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def is_likely_heading(text: str) -> bool:
    """Check if text looks like a heading"""
    if not text or len(text.strip()) < 3:
        return False
    
    text = text.strip()
    
    # Check for common heading patterns
    heading_patterns = [
        r'^\d+\.',  # Numbered sections
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title case
        r'^[A-Z\s]+$',  # All caps
        r'^\w+:',  # Colon-terminated
    ]
    
    for pattern in heading_patterns:
        if re.match(pattern, text):
            return True
    
    # Check length (headings are usually shorter)
    if len(text) < 80 and not text.endswith('.'):
        return True
    
    return False


def get_text_statistics(text_blocks: List[TextBlock]) -> Dict:
    """Get statistics about text blocks"""
    if not text_blocks:
        return {
            'total_blocks': 0,
            'avg_font_size': 12.0,
            'font_sizes': [12.0],
            'page_count': 0
        }
    
    font_sizes = [block.font_size for block in text_blocks]
    pages = set(block.page_num for block in text_blocks)
    
    return {
        'total_blocks': len(text_blocks),
        'avg_font_size': sum(font_sizes) / len(font_sizes),
        'font_sizes': font_sizes,
        'page_count': len(pages)
    }


class PDFUtils:
    """Utility functions for PDF processing"""
    
    @staticmethod
    def extract_text_blocks(pdf_path: str) -> List[TextBlock]:
        """Extract text blocks with formatting information from PDF"""
        # Use our fallback system
        doc_content = extract_document_content(pdf_path)
        return doc_content.get('text_blocks', [])
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        return clean_text(text)
    
    @staticmethod
    def is_likely_heading(text: str) -> bool:
        """Check if text looks like a heading"""
        return is_likely_heading(text)
    
    @staticmethod
    def get_document_stats(text_blocks: List[TextBlock]) -> Dict:
        """Get document statistics"""
        return get_text_statistics(text_blocks)