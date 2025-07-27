"""
ML-Enhanced Outline Extractor for Round 1A
"""

import re
import time
from typing import List, Dict, Any
from pathlib import Path

from shared.pdf_utils import extract_document_content, PDFUtils
from shared.text_processor import TextProcessor
from shared.config import Config


class MLOutlineExtractor:
    """ML-enhanced outline extractor with transformer-based heading detection"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.config = Config()
    
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Extract document outline using ML when available"""
        try:
            # Extract document content
            doc_content = extract_document_content(pdf_path)
            text_blocks = doc_content.get('text_blocks', [])
            
            if not text_blocks:
                return {"title": "", "outline": []}
            
            # Use ML-enhanced heading detection
            outline_items = self._extract_outline_with_ml(text_blocks)
            
            # Extract document title
            title = self._extract_title(text_blocks)
            
            return {
                "title": title,
                "outline": outline_items
            }
            
        except Exception as e:
            print(f"Error extracting outline: {str(e)}")
            return {"title": "", "outline": []}
    
    def _extract_outline_with_ml(self, text_blocks: List) -> List[Dict]:
        """Extract outline using ML-enhanced heading detection"""
        outline_items = []
        
        for block in text_blocks:
            text = block.text.strip()
            
            if not text or len(text) < 3:
                continue
            
            # Use ML-enhanced heading detection
            is_heading, confidence = self.text_processor.is_heading_ml(text)
            
            if is_heading:
                # Determine heading level using ML and rules
                level = self._determine_heading_level_ml(text, confidence, block)
                
                outline_item = {
                    "text": text,  # Adobe format: "text"
                    "level": level,
                    "page_number": getattr(block, 'page_num', 1),
                    "confidence": confidence
                }
                
                outline_items.append(outline_item)
        
        # Post-process: Create hierarchical structure
        return self._create_hierarchical_structure(outline_items)
    
    def _determine_heading_level_ml(self, text: str, confidence: float, block) -> int:
        """Determine heading level using ML features and rules"""
        level = 1
        
        # Font size factor (if available)
        if hasattr(block, 'font_size'):
            font_size = block.font_size
            if font_size > 16:
                level = 1
            elif font_size > 14:
                level = 2
            else:
                level = 3
        
        # Pattern-based level detection
        text_lower = text.lower()
        
        # Level 1 patterns
        if re.match(r'^\d+\.\s*[A-Z]', text):
            level = 1
        elif any(word in text_lower for word in ['chapter', 'part', 'section']):
            level = 1
        
        # Level 2 patterns
        elif re.match(r'^\d+\.\d+\s*[A-Z]', text):
            level = 2
        elif text.isupper() and len(text) < 50:
            level = 2
        
        # Level 3 patterns
        elif re.match(r'^\d+\.\d+\.\d+', text):
            level = 3
        elif confidence < 0.7:
            level = 3
        
        return min(level, 3)  # Cap at level 3
    
    def _create_hierarchical_structure(self, outline_items: List[Dict]) -> List[Dict]:
        """Create hierarchical structure from flat outline items"""
        if not outline_items:
            return []
        
        # Sort by page number and confidence
        outline_items.sort(key=lambda x: (x['page_number'], -x['confidence']))
        
        # Create hierarchy
        result = []
        stack = []
        
        for item in outline_items:
            level = item['level']
            
            # Pop items with higher or equal level
            while stack and stack[-1]['level'] >= level:
                stack.pop()
            
            # Remove confidence from final output and convert to Adobe format
            level_mapping = {1: "H1", 2: "H2", 3: "H3"}
            level_str = level_mapping.get(level, f"H{min(level, 3)}")
            
            final_item = {
                "level": level_str,
                "text": item['text'],
                "page": item['page_number']
            }
            
            result.append(final_item)
        
        return result
    
    def _extract_title(self, text_blocks: List) -> str:
        """Extract document title using ML-enhanced detection"""
        if not text_blocks:
            return ""
        
        # Look for title in first few blocks
        for block in text_blocks[:5]:
            text = block.text.strip()
            
            if not text or len(text) < 5:
                continue
            
            # Use ML heading detection
            is_heading, confidence = self.text_processor.is_heading_ml(text)
            
            if is_heading and confidence > 0.8:
                # Additional checks for title-like text
                if (len(text) > 10 and 
                    len(text) < 100 and 
                    not text.endswith('.') and
                    not re.match(r'^\d+\.', text)):
                    return text
        
        # Fallback: use first heading-like text
        for block in text_blocks[:10]:
            text = block.text.strip()
            if PDFUtils.is_likely_heading(text):
                return text
        
        return ""
