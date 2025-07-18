"""
Section Extractor for extracting and processing document sections
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path

from shared.pdf_utils import extract_document_content, TextBlock, PDFUtils
from shared.text_processor import TextProcessor
from round1a.outline_extractor import OutlineExtractor


class SectionExtractor:
    """Extracts sections and sub-sections from PDF documents"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.outline_extractor = OutlineExtractor()
    
    def extract_sections(self, pdf_path: str) -> List[Dict]:
        """Extract main sections from a PDF document"""
        try:
            # First get the document outline
            outline_data = self.outline_extractor.extract_outline(pdf_path)
            
            # Extract text blocks using our fallback system
            text_blocks = PDFUtils.extract_text_blocks(pdf_path)
            
            if not text_blocks:
                return []
            
            # Create sections based on outline
            sections = []
            outline_items = outline_data.get("outline", [])
            
            if outline_items:
                sections = self._create_sections_from_outline(outline_items, text_blocks, pdf_path)
            else:
                # Fallback: create sections based on content analysis
                sections = self._create_sections_from_content(text_blocks, pdf_path)
            
            return sections
            
        except Exception as e:
            print(f"Error extracting sections from {pdf_path}: {str(e)}")
            return []
    
    def _create_sections_from_outline(self, outline_items: List[Dict], text_blocks: List[TextBlock], pdf_path: str) -> List[Dict]:
        """Create sections based on document outline"""
        sections = []
        
        for i, item in enumerate(outline_items):
            # Get section information from outline item
            title = item.get("section_title", "")
            level = item.get("level", 1)
            page_num = item.get("page_number", 1)
            
            if not title:
                continue
            
            # Extract content for this section
            content = self._extract_section_content(
                title, page_num, text_blocks, 
                outline_items[i+1] if i+1 < len(outline_items) else None
            )
            
            if content:
                section = {
                    "title": title,
                    "level": level,
                    "page": page_num,
                    "content": content,
                    "document": Path(pdf_path).name,
                    "word_count": len(content.split())
                }
                sections.append(section)
        
        return sections
    
    def _create_sections_from_content(self, text_blocks: List[TextBlock], pdf_path: str) -> List[Dict]:
        """Create sections based on content analysis when outline is not available"""
        sections = []
        
        # Group text blocks by pages
        pages = {}
        for block in text_blocks:
            if block.page_num not in pages:
                pages[block.page_num] = []
            pages[block.page_num].append(block)
        
        # Create sections per page or logical groupings
        for page_num, blocks in pages.items():
            page_text = " ".join([block.text for block in blocks])
            
            if len(page_text.strip()) > 100:  # Minimum content threshold
                # Try to find a meaningful title from the page
                title = self._extract_page_title(blocks)
                
                section = {
                    "title": title or f"Page {page_num} Content",
                    "level": 1,
                    "page": page_num,
                    "content": PDFUtils.clean_text(page_text),
                    "document": Path(pdf_path).name,
                    "word_count": len(page_text.split())
                }
                sections.append(section)
        
        return sections
    
    def _extract_section_content(self, title: str, start_page: int, text_blocks: List[TextBlock], next_item: Dict = None) -> str:
        """Extract content for a specific section"""
        content_blocks = []
        
        # Determine end page
        end_page = next_item.get("page_number", float('inf')) if next_item else float('inf')
        
        # Collect relevant text blocks
        title_found = False
        for block in text_blocks:
            # Check if we're in the right page range
            if block.page_num < start_page:
                continue
            if block.page_num >= end_page:
                break
            
            # Look for the title to start collecting content
            if not title_found:
                if self._is_title_match(block.text, title):
                    title_found = True
                continue
            
            content_blocks.append(block.text)
        
        # Join and clean content
        content = " ".join(content_blocks)
        return PDFUtils.clean_text(content)
    
    def _is_title_match(self, block_text: str, title: str) -> bool:
        """Check if block text matches the section title"""
        block_clean = PDFUtils.clean_text(block_text).lower()
        title_clean = title.lower()
        
        # Exact match
        if title_clean in block_clean:
            return True
        
        # Fuzzy match for common variations
        title_words = title_clean.split()
        if len(title_words) > 1:
            # Check if most words are present
            matches = sum(1 for word in title_words if word in block_clean)
            return matches >= len(title_words) * 0.7
        
        return False
    
    def _extract_page_title(self, blocks: List[TextBlock]) -> str:
        """Extract a meaningful title from page blocks"""
        if not blocks:
            return ""
        
        # Sort blocks by position (top first)
        sorted_blocks = sorted(blocks, key=lambda x: x.bbox[1])
        
        # Look for title-like text in the first few blocks
        for block in sorted_blocks[:5]:
            text = block.text.strip()
            if (len(text) > 5 and 
                len(text) < 100 and 
                PDFUtils.is_likely_heading(text)):
                return PDFUtils.clean_text(text)
        
        return ""
    
    def extract_subsections(self, content: str, document: str, page: int) -> List[Dict]:
        """Extract sub-sections from section content"""
        if not content:
            return []
        
        subsections = []
        
        # Split content into paragraphs
        paragraphs = self.text_processor.segment_text_by_topics(content, max_segments=5)
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 50:  # Minimum content length
                subsection = {
                    "content": paragraph.strip(),
                    "document": document,
                    "page": page,
                    "subsection_index": i + 1
                }
                subsections.append(subsection)
        
        return subsections
    
    def extract_key_sentences(self, content: str, max_sentences: int = 3) -> List[str]:
        """Extract key sentences from content"""
        if not content:
            return []
        
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Simple scoring based on length and position
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            
            # Position score (earlier sentences often more important)
            score += max(0, 1 - i / len(sentences)) * 0.3
            
            # Length score (moderate length preferred)
            length_score = min(len(sentence) / 100, 1.0)
            score += length_score * 0.4
            
            # Keyword density (would need domain-specific keywords)
            score += 0.3  # Default score
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent[0] for sent in scored_sentences[:max_sentences]]
