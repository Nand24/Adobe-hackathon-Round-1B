"""
Relevance Ranker for scoring and ranking content sections based on persona and job requirements
"""

import math
from typing import List, Dict, Tuple
from collections import Counter

from shared.text_processor import TextProcessor
from shared.config import Config


class RelevanceRanker:
    """Ranks document sections based on relevance to persona and job requirements"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def rank_sections(self, sections: List[Dict], persona_profile: Dict) -> List[Dict]:
        """Rank sections based on relevance to persona profile"""
        if not sections:
            return []
        
        # Score each section
        scored_sections = []
        for section in sections:
            score = self._calculate_relevance_score(section, persona_profile)
            section_with_score = section.copy()
            section_with_score["relevance_score"] = score
            scored_sections.append(section_with_score)
        
        # Sort by relevance score (descending)
        scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_sections
    
    def _calculate_relevance_score(self, section: Dict, persona_profile: Dict) -> float:
        """Calculate overall relevance score for a section"""
        content = section.get("content", "")
        title = section.get("title", "")
        
        if not content:
            return 0.0
        
        # Component scores
        semantic_score = self._calculate_semantic_score(content, title, persona_profile)
        keyword_score = self._calculate_keyword_score(content, title, persona_profile)
        structural_score = self._calculate_structural_score(section)
        quality_score = self._calculate_quality_score(content)
        
        # Weighted combination
        total_score = (
            semantic_score * Config.SEMANTIC_WEIGHT +
            keyword_score * Config.KEYWORD_WEIGHT +
            structural_score * Config.STRUCTURAL_WEIGHT +
            quality_score * Config.QUALITY_WEIGHT
        )
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_semantic_score(self, content: str, title: str, persona_profile: Dict) -> float:
        """Calculate semantic similarity score"""
        score = 0.0
        
        # Combine content and title
        full_text = f"{title} {content}"
        
        # Simple semantic scoring based on domain and role matching
        role = persona_profile.get("role", "")
        domain = persona_profile.get("domain", "")
        job_type = persona_profile.get("job_type", "")
        
        # Role-based scoring
        role_keywords = self._get_role_keywords(role)
        role_matches = sum(1 for keyword in role_keywords if keyword.lower() in full_text.lower())
        score += min(role_matches / max(len(role_keywords), 1) * 0.4, 0.4)
        
        # Domain-based scoring
        domain_keywords = self._get_domain_keywords(domain)
        domain_matches = sum(1 for keyword in domain_keywords if keyword.lower() in full_text.lower())
        score += min(domain_matches / max(len(domain_keywords), 1) * 0.3, 0.3)
        
        # Job type scoring
        job_keywords = self._get_job_type_keywords(job_type)
        job_matches = sum(1 for keyword in job_keywords if keyword.lower() in full_text.lower())
        score += min(job_matches / max(len(job_keywords), 1) * 0.3, 0.3)
        
        return score
    
    def _calculate_keyword_score(self, content: str, title: str, persona_profile: Dict) -> float:
        """Calculate keyword matching score"""
        score = 0.0
        
        full_text = f"{title} {content}".lower()
        
        # Persona keywords
        persona_keywords = persona_profile.get("keywords", [])
        persona_matches = sum(1 for keyword in persona_keywords if keyword.lower() in full_text)
        if persona_keywords:
            score += min(persona_matches / len(persona_keywords) * 0.5, 0.5)
        
        # Job keywords
        job_keywords = persona_profile.get("job_keywords", [])
        job_matches = sum(1 for keyword in job_keywords if keyword.lower() in full_text)
        if job_keywords:
            score += min(job_matches / len(job_keywords) * 0.5, 0.5)
        
        # Success criteria keywords
        success_criteria = persona_profile.get("success_criteria", [])
        criteria_matches = sum(1 for criterion in success_criteria 
                             if any(word.lower() in full_text for word in criterion.split()))
        if success_criteria:
            score += min(criteria_matches / len(success_criteria) * 0.3, 0.3)
        
        return score
    
    def _calculate_structural_score(self, section: Dict) -> float:
        """Calculate structural importance score"""
        score = 0.0
        
        # Heading level importance (H1 > H2 > H3)
        level = section.get("level", 3)
        if level == 1:
            score += 0.4
        elif level == 2:
            score += 0.3
        elif level == 3:
            score += 0.2
        
        # Page position (earlier pages often more important)
        page = section.get("page", 1)
        page_score = max(0, 1 - (page - 1) / 10)  # Decay over 10 pages
        score += page_score * 0.3
        
        # Content length (moderate length preferred)
        word_count = section.get("word_count", 0)
        if 50 <= word_count <= 500:
            score += 0.3
        elif 500 < word_count <= 1000:
            score += 0.2
        elif word_count > 1000:
            score += 0.1
        
        return score
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate content quality score"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Information density
        word_count = len(content.split())
        unique_words = len(set(content.lower().split()))
        if word_count > 0:
            diversity_ratio = unique_words / word_count
            score += min(diversity_ratio * 2, 0.3)  # Higher diversity = better quality
        
        # Presence of quantitative data
        numbers = len([word for word in content.split() if any(char.isdigit() for char in word)])
        if numbers > 0:
            score += min(numbers / word_count * 10, 0.2)
        
        # Complexity score
        complexity = self.text_processor.get_text_complexity_score(content)
        
        # Adjust based on expertise level
        # For experts, higher complexity is better; for beginners, moderate complexity is preferred
        score += complexity * 0.2
        
        # Readability indicators
        if any(indicator in content.lower() for indicator in 
               ['figure', 'table', 'example', 'case study', 'result', 'finding']):
            score += 0.2
        
        # Question presence (good for learning contexts)
        if self.text_processor.is_question(content):
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_role_keywords(self, role: str) -> List[str]:
        """Get keywords associated with a specific role"""
        role_keywords = {
            "researcher": ["research", "study", "analysis", "methodology", "findings", "literature", "hypothesis", "experiment"],
            "student": ["learn", "understand", "concept", "theory", "practice", "exercise", "example", "explanation"],
            "analyst": ["analyze", "data", "trend", "metric", "performance", "benchmark", "comparison", "insight"],
            "journalist": ["report", "news", "story", "source", "interview", "investigation", "fact", "evidence"],
            "entrepreneur": ["business", "opportunity", "market", "strategy", "growth", "innovation", "venture", "competitive"],
            "developer": ["code", "implementation", "system", "architecture", "framework", "library", "api", "technical"],
            "manager": ["team", "project", "planning", "execution", "strategy", "leadership", "operations", "coordination"]
        }
        
        return role_keywords.get(role, [])
    
    def _get_domain_keywords(self, domain: str) -> List[str]:
        """Get keywords associated with a specific domain"""
        domain_keywords = {
            "technology": ["software", "hardware", "digital", "computer", "internet", "ai", "machine learning", "data"],
            "biology": ["cell", "organism", "gene", "protein", "evolution", "ecosystem", "species", "molecular"],
            "chemistry": ["molecule", "reaction", "compound", "element", "bond", "synthesis", "catalyst", "organic"],
            "finance": ["investment", "revenue", "profit", "market", "financial", "economic", "capital", "asset"],
            "business": ["management", "strategy", "marketing", "sales", "customer", "product", "service", "operation"],
            "education": ["teaching", "learning", "curriculum", "assessment", "pedagogy", "instruction", "academic", "school"],
            "engineering": ["design", "system", "process", "optimization", "manufacturing", "construction", "technical", "specification"],
            "law": ["legal", "regulation", "compliance", "contract", "liability", "court", "statute", "precedent"]
        }
        
        return domain_keywords.get(domain, [])
    
    def _get_job_type_keywords(self, job_type: str) -> List[str]:
        """Get keywords associated with a specific job type"""
        job_keywords = {
            "review": ["review", "evaluate", "assess", "critique", "examination", "analysis", "overview", "summary"],
            "summarize": ["summary", "overview", "brief", "abstract", "condensed", "key points", "main ideas", "synopsis"],
            "compare": ["compare", "contrast", "difference", "similarity", "versus", "benchmark", "relative", "comparison"],
            "identify": ["identify", "find", "locate", "discover", "detect", "recognize", "determine", "specify"],
            "prepare": ["prepare", "create", "develop", "build", "design", "construct", "formulate", "establish"],
            "learn": ["learn", "understand", "study", "master", "comprehend", "grasp", "acquire", "absorb"]
        }
        
        return job_keywords.get(job_type, [])
