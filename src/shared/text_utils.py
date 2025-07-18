"""
Fallback text processing when PyMuPDF is not available
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TextBlock:
    """Represents a text block with formatting information"""
    text: str
    page_num: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font_size: float
    font_name: str
    font_flags: int
    line_height: float


def extract_text_from_file(file_path: str) -> List[TextBlock]:
    """
    Extract text from a simple text file as fallback
    """
    text_blocks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into lines and create text blocks
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                # Simulate text block with default values
                text_block = TextBlock(
                    text=line.strip(),
                    page_num=1,  # All content on page 1 for text files
                    bbox=(0, i * 20, 100, (i + 1) * 20),  # Simulate line positions
                    font_size=12.0,  # Default font size
                    font_name="Arial",
                    font_flags=0,
                    line_height=14.0
                )
                text_blocks.append(text_block)
        
        print(f"Extracted {len(text_blocks)} text blocks from {file_path}")
        return text_blocks
        
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}")
        return []


def detect_headings_from_text(text_blocks: List[TextBlock]) -> List[Dict]:
    """
    Detect headings from text blocks using simple heuristics
    """
    headings = []
    
    for block in text_blocks:
        text = block.text.strip()
        
        # Skip very short or very long lines
        if len(text) < 3 or len(text) > 200:
            continue
        
        # Check if it looks like a heading
        is_heading = False
        level = 3  # Default level
        
        # Pattern 1: Numbered sections (1., 1.1, 1.1.1, etc.)
        if re.match(r'^\d+(\.\d+)*\.?\s+\w+', text):
            is_heading = True
            # Count dots to determine level
            dots = text.count('.')
            level = min(dots + 1, 4)  # Max level 4
        
        # Pattern 2: Short lines that look like titles
        elif len(text) < 80 and not text.endswith('.') and not text.endswith(','):
            # Check if it's likely a heading (title case, short, no punctuation)
            words = text.split()
            if len(words) <= 8:  # Short phrases
                is_heading = True
                level = 2  # Assume level 2 for title-like text
        
        # Pattern 3: All caps words (likely headers)
        elif text.isupper() and len(text.split()) <= 6:
            is_heading = True
            level = 1  # Top level for all caps
        
        if is_heading:
            heading = {
                'text': text,
                'level': level,
                'page_num': block.page_num,
                'bbox': block.bbox,
                'font_size': block.font_size,
                'confidence': 0.7  # Lower confidence for text-based detection
            }
            headings.append(heading)
    
    return headings


def get_text_statistics(text_blocks: List[TextBlock]) -> Dict:
    """
    Get basic statistics about the text
    """
    if not text_blocks:
        return {
            'total_blocks': 0,
            'avg_font_size': 12.0,
            'font_sizes': [12.0]
        }
    
    font_sizes = [block.font_size for block in text_blocks]
    
    return {
        'total_blocks': len(text_blocks),
        'avg_font_size': sum(font_sizes) / len(font_sizes),
        'font_sizes': font_sizes
    }


def extract_document_structure(file_path: str) -> Dict:
    """
    Extract document structure from a text file
    """
    print(f"Processing text file: {file_path}")
    
    # Extract text blocks
    text_blocks = extract_text_from_file(file_path)
    
    if not text_blocks:
        return {
            'text_blocks': [],
            'headings': [],
            'statistics': get_text_statistics([])
        }
    
    # Detect headings
    headings = detect_headings_from_text(text_blocks)
    
    # Get statistics
    statistics = get_text_statistics(text_blocks)
    
    return {
        'text_blocks': text_blocks,
        'headings': headings,
        'statistics': statistics
    }
