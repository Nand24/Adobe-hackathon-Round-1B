"""
Round 1B: Document Analyzer for Persona-Driven Intelligence
Analyzes document collections based on user persona and job requirements
"""

import json
import time
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from shared.pdf_utils import extract_document_content, TextBlock
from shared.text_processor import TextProcessor
from shared.config import Config
from .persona_processor import PersonaProcessor
from .relevance_ranker import RelevanceRanker
from .section_extractor import SectionExtractor


class DocumentAnalyzer:
    """Main class for persona-driven document analysis"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.persona_processor = PersonaProcessor()
        self.relevance_ranker = RelevanceRanker()
        self.section_extractor = SectionExtractor()
    
    def analyze_documents(self, pdf_files: List[Path], persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Analyze document collection based on persona and job requirements"""
        try:
            start_time = time.time()
            
            # Process persona and job requirements
            persona_profile = self.persona_processor.process_persona(persona, job_to_be_done)
            
            # Extract sections from all documents
            all_sections = []
            for pdf_file in pdf_files:
                sections = self.section_extractor.extract_sections(str(pdf_file))
                all_sections.extend(sections)
            
            # Rank sections based on relevance
            ranked_sections = self.relevance_ranker.rank_sections(
                sections=all_sections,
                persona_profile=persona_profile
            )
            
            # Extract and analyze sub-sections
            subsection_analysis = self._analyze_subsections(ranked_sections, persona_profile)
            
            # Build final output
            result = {
                "metadata": {
                    "persona": persona,
                    "job_to_be_done": job_to_be_done,
                    "documents_processed": [str(f.name) for f in pdf_files],
                    "processing_timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": round(time.time() - start_time, 2)
                },
                "extracted_sections": self._format_extracted_sections(ranked_sections),
                "subsection_analysis": subsection_analysis
            }
            
            return result
            
        except Exception as e:
            print(f"Error in document analysis: {str(e)}")
            return {
                "metadata": {"error": str(e)},
                "extracted_sections": [],
                "subsection_analysis": []
            }
    
    def _analyze_subsections(self, ranked_sections: List[Dict], persona_profile: Dict) -> List[Dict]:
        """Analyze and refine sub-sections"""
        subsection_analysis = []
        
        for section in ranked_sections[:10]:  # Analyze top 10 sections
            # Extract sub-sections from the main section
            subsections = self.section_extractor.extract_subsections(
                section["content"], 
                section["document"], 
                section["page"]
            )
            
            for subsection in subsections:
                # Refine text for sub-section
                refined_text = self._refine_subsection_text(
                    subsection["content"], 
                    persona_profile
                )
                
                if refined_text:  # Only include if refinement produced content
                    subsection_analysis.append({
                        "document": subsection["document"],
                        "page_number": subsection["page"],
                        "refined_text": refined_text
                    })
        
        return subsection_analysis[:20]  # Limit to top 20 sub-sections
    
    def _refine_subsection_text(self, content: str, persona_profile: Dict) -> str:
        """Refine sub-section text based on persona requirements"""
        if not content:
            return ""
        
        # Extract key sentences based on persona relevance
        sentences = content.split('. ')
        
        relevant_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum sentence length
                # Score sentence relevance
                relevance_score = self._score_sentence_relevance(sentence, persona_profile)
                if relevance_score > 0.3:  # Threshold for inclusion
                    relevant_sentences.append(sentence)
        
        # Join top sentences
        if relevant_sentences:
            refined = '. '.join(relevant_sentences[:3])  # Top 3 sentences
            if not refined.endswith('.'):
                refined += '.'
            return refined
        
        return ""
    
    def _score_sentence_relevance(self, sentence: str, persona_profile: Dict) -> float:
        """Score sentence relevance to persona profile"""
        score = 0.0
        
        # Keyword matching
        persona_keywords = persona_profile.get("keywords", [])
        job_keywords = persona_profile.get("job_keywords", [])
        
        sentence_lower = sentence.lower()
        
        # Check for persona keywords
        for keyword in persona_keywords:
            if keyword.lower() in sentence_lower:
                score += 0.2
        
        # Check for job-related keywords
        for keyword in job_keywords:
            if keyword.lower() in sentence_lower:
                score += 0.3
        
        # Length bonus (longer sentences often contain more information)
        if len(sentence) > 50:
            score += 0.1
        
        # Question or conclusion indicators
        if any(indicator in sentence_lower for indicator in ['therefore', 'conclusion', 'result', 'finding']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _format_extracted_sections(self, ranked_sections: List[Dict]) -> List[Dict]:
        """Format sections for final output"""
        formatted_sections = []
        
        for i, section in enumerate(ranked_sections[:15]):  # Top 15 sections
            formatted_section = {
                "document": section["document"],
                "page_number": section["page"],
                "section_title": section["title"],
                "importance_rank": i + 1
            }
            formatted_sections.append(formatted_section)
        
        return formatted_sections
