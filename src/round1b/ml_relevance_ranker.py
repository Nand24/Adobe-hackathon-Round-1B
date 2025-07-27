"""
ML-Enhanced Relevance Ranker for Round 1B
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter

from shared.text_processor import TextProcessor


class MLRelevanceRanker:
    """ML-enhanced relevance ranker with semantic similarity"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def rank_sections(self, sections: List[Dict], persona_profile: Dict) -> List[Dict]:
        """Rank sections using ML-enhanced relevance scoring"""
        if not sections:
            return []
        
        # Calculate relevance scores using ML
        scored_sections = []
        for section in sections:
            score = self._calculate_ml_relevance_score(section, persona_profile)
            section_copy = section.copy()
            section_copy['relevance_score'] = score
            scored_sections.append(section_copy)
        
        # Sort by relevance score (descending)
        scored_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Assign importance ranks
        for i, section in enumerate(scored_sections):
            section['importance_rank'] = i + 1
        
        return scored_sections
    
    def _calculate_ml_relevance_score(self, section: Dict, persona_profile: Dict) -> float:
        """Calculate relevance score using ML semantic similarity"""
        content = section.get('content', '')
        title = section.get('title', '')
        
        if not content and not title:
            return 0.0
        
        # Combine title and content for analysis
        full_text = f"{title} {content}".strip()
        
        # Create persona context
        persona_context = self._create_persona_context(persona_profile)
        
        # Use ML-enhanced similarity calculation
        semantic_score = self._calculate_semantic_similarity(full_text, persona_context)
        
        # Combine with rule-based scoring
        rule_score = self._calculate_rule_based_score(section, persona_profile)
        
        # Weighted combination: 70% ML, 30% rules
        final_score = 0.7 * semantic_score + 0.3 * rule_score
        
        return min(final_score, 1.0)
    
    def _create_persona_context(self, persona_profile: Dict) -> str:
        """Create context string from persona profile"""
        context_parts = []
        
        # Add persona description
        if persona_profile.get('raw_persona'):
            context_parts.append(persona_profile['raw_persona'])
        
        # Add job description
        if persona_profile.get('raw_job'):
            context_parts.append(persona_profile['raw_job'])
        
        # Add keywords
        if persona_profile.get('keywords'):
            context_parts.extend(persona_profile['keywords'])
        
        # Add job keywords
        if persona_profile.get('job_keywords'):
            context_parts.extend(persona_profile['job_keywords'])
        
        return ' '.join(context_parts)
    
    def _calculate_semantic_similarity(self, text: str, context: str) -> float:
        """Calculate semantic similarity using ML models"""
        if not text or not context:
            return 0.0
        
        # Use ML-enhanced similarity calculation
        try:
            similarity = self.text_processor.calculate_text_similarity(text, context)
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            print(f"Warning: ML similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_rule_based_score(self, section: Dict, persona_profile: Dict) -> float:
        """Calculate relevance score using rule-based approach"""
        content = section.get('content', '').lower()
        title = section.get('title', '').lower()
        full_text = f"{title} {content}"
        
        score = 0.0
        
        # Keyword matching
        keywords = persona_profile.get('keywords', [])
        job_keywords = persona_profile.get('job_keywords', [])
        all_keywords = keywords + job_keywords
        
        if all_keywords:
            matched_keywords = sum(1 for keyword in all_keywords if keyword.lower() in full_text)
            keyword_score = matched_keywords / len(all_keywords)
            score += keyword_score * 0.4
        
        # Role-specific scoring
        role = persona_profile.get('role', '').lower()
        domain = persona_profile.get('domain', '').lower()
        
        # Role-based relevance
        role_keywords = self._get_role_keywords(role)
        if role_keywords:
            role_matches = sum(1 for keyword in role_keywords if keyword in full_text)
            role_score = role_matches / len(role_keywords)
            score += role_score * 0.3
        
        # Domain-based relevance
        domain_keywords = self._get_domain_keywords(domain)
        if domain_keywords:
            domain_matches = sum(1 for keyword in domain_keywords if keyword in full_text)
            domain_score = domain_matches / len(domain_keywords)
            score += domain_score * 0.3
        
        return min(score, 1.0)
    
    def _get_role_keywords(self, role: str) -> List[str]:
        """Get keywords associated with specific roles"""
        role_keywords = {
            'researcher': ['research', 'study', 'analysis', 'methodology', 'experiment', 'findings', 'results'],
            'student': ['learning', 'education', 'course', 'assignment', 'exam', 'study', 'tutorial'],
            'analyst': ['analysis', 'data', 'metrics', 'insights', 'trends', 'evaluation', 'assessment'],
            'engineer': ['technical', 'implementation', 'system', 'design', 'architecture', 'development'],
            'manager': ['strategy', 'planning', 'management', 'objectives', 'goals', 'performance'],
            'developer': ['code', 'programming', 'software', 'application', 'development', 'implementation']
        }
        
        return role_keywords.get(role, [])
    
    def _get_domain_keywords(self, domain: str) -> List[str]:
        """Get keywords associated with specific domains"""
        domain_keywords = {
            'biology': ['biological', 'organism', 'cell', 'genetic', 'protein', 'species', 'evolution'],
            'chemistry': ['chemical', 'molecule', 'reaction', 'compound', 'element', 'bond', 'synthesis'],
            'physics': ['physical', 'energy', 'force', 'particle', 'wave', 'quantum', 'mechanics'],
            'computer science': ['algorithm', 'data structure', 'programming', 'software', 'hardware', 'computing'],
            'mathematics': ['mathematical', 'equation', 'theorem', 'proof', 'function', 'variable', 'formula'],
            'medicine': ['medical', 'patient', 'treatment', 'diagnosis', 'therapy', 'clinical', 'health'],
            'finance': ['financial', 'investment', 'market', 'revenue', 'profit', 'risk', 'portfolio'],
            'business': ['business', 'strategy', 'market', 'customer', 'revenue', 'competition', 'growth'],
            'technology': ['technology', 'innovation', 'digital', 'ai', 'machine learning', 'automation']
        }
        
        # Try exact match first
        if domain in domain_keywords:
            return domain_keywords[domain]
        
        # Try partial matches
        for key, keywords in domain_keywords.items():
            if key in domain or domain in key:
                return keywords
        
        return []
    
    def find_related_sections(self, target_section: Dict, all_sections: List[Dict], 
                            max_related: int = 3) -> List[str]:
        """Find sections related to the target section using ML similarity"""
        if not target_section or not all_sections:
            return []
        
        target_content = f"{target_section.get('title', '')} {target_section.get('content', '')}"
        
        # Calculate similarities
        similarities = []
        for section in all_sections:
            if section == target_section:
                continue
            
            section_content = f"{section.get('title', '')} {section.get('content', '')}"
            similarity = self.text_processor.calculate_text_similarity(target_content, section_content)
            
            if similarity > 0.3:  # Threshold for related content
                similarities.append((section.get('title', ''), similarity))
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [title for title, _ in similarities[:max_related]]
