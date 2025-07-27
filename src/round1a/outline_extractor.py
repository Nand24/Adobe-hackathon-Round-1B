"""
Round 1A: Document Outline Extractor
Extracts structured outlines (Title, H1, H2, H3) from PDF documents
"""

import json
import statistics
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re

from shared.pdf_utils import extract_document_content, TextBlock
from shared.text_processor import TextProcessor
from shared.config import Config


class OutlineExtractor:
    """Main class for extracting document outlines"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def extract_outline(self, file_path: str) -> Dict:
        """Extract structured outline from PDF or text file"""
        try:
            # Extract document content
            doc_content = extract_document_content(file_path)
            
            if not doc_content['text_blocks']:
                return {"title": "", "outline": []}
            
            # Use the headings detected by our text processor
            headings = doc_content['headings']
            
            # Extract title (first heading or first line)
            title = self._extract_title_from_headings(headings, doc_content['text_blocks'])
            
            # Build outline structure
            outline = self._build_outline_structure(headings)
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            print(f"Error extracting outline from {file_path}: {e}")
            return {"title": "", "outline": []}
    
    def _extract_title_from_headings(self, headings: List[Dict], text_blocks: List[TextBlock]) -> str:
        """Extract document title from headings or first text block"""
        if headings:
            # Find the highest level heading (lowest level number)
            title_heading = min(headings, key=lambda h: h['level'])
            return title_heading['text']
        elif text_blocks:
            # Fallback to first non-empty text block
            for block in text_blocks:
                if block.text.strip():
                    return block.text.strip()
        return ""
    
    def _build_outline_structure(self, headings: List[Dict]) -> List[Dict]:
        """Build outline structure in Adobe's exact format: {"level": "H1", "text": "...", "page": 1}"""
        if not headings:
            return []
        
        # Sort headings by page number and position
        sorted_headings = sorted(headings, key=lambda h: (h['page_num'], h['bbox'][1]))
        
        outline = []
        
        for heading in sorted_headings:
            level = heading['level']
            
            # Convert level to Adobe's string format (H1, H2, H3)
            level_mapping = {1: "H1", 2: "H2", 3: "H3"}
            level_str = level_mapping.get(level, f"H{min(level, 3)}")  # Cap at H3 per Adobe spec
            
            # Adobe's exact required format
            outline_item = {
                "level": level_str,
                "text": heading['text'], 
                "page": heading['page_num']
            }
            outline.append(outline_item)
        
        return outline
