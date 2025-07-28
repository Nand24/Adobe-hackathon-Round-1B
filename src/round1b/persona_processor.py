"""
Persona Processor for understanding user personas and job requirements
"""

import re
from typing import Dict, List, Set
from shared.text_processor import TextProcessor


class PersonaProcessor:
    """Processes and understands user personas and job requirements"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        
        # Domain keywords for different roles
        self.role_domains = {
            "researcher": {"research", "study", "analysis", "methodology", "findings", "literature", "academic", "paper", "journal"},
            "student": {"learn", "study", "exam", "concept", "understand", "knowledge", "education", "course", "textbook"},
            "analyst": {"analyze", "data", "trend", "report", "financial", "business", "metric", "performance", "investment"},
            "journalist": {"news", "article", "report", "story", "interview", "source", "media", "press", "journalism"},
            "entrepreneur": {"business", "startup", "market", "opportunity", "strategy", "growth", "innovation", "venture"},
            "developer": {"code", "software", "programming", "development", "technical", "system", "application", "framework"},
            "manager": {"team", "project", "management", "leadership", "strategy", "planning", "execution", "operations"},
            "travel planner": {"travel", "trip", "destination", "itinerary", "activities", "attractions", "hotels", "restaurants", "transport", "booking", "vacation", "tourism", "sightseeing", "accommodation", "flight", "guide", "explore", "visit", "experience"},
            "tourist": {"travel", "vacation", "sightseeing", "attractions", "culture", "local", "experience", "explore", "visit", "leisure", "holiday"},
            "traveler": {"journey", "destination", "adventure", "culture", "local", "experience", "explore", "discover", "immerse"}
        }
        
        # Action words for different job types
        self.job_actions = {
            "review": {"review", "analyze", "examine", "evaluate", "assess", "critique"},
            "summarize": {"summarize", "overview", "abstract", "synopsis", "brief", "condensed"},
            "compare": {"compare", "contrast", "difference", "similarity", "versus", "benchmark"},
            "identify": {"identify", "find", "locate", "discover", "detect", "recognize"},
            "prepare": {"prepare", "create", "develop", "build", "design", "construct"},
            "learn": {"learn", "understand", "study", "master", "comprehend", "grasp"},
            "plan": {"plan", "organize", "schedule", "arrange", "coordinate", "itinerary", "trip", "travel", "book", "reserve"}
        }
    
    def process_persona(self, persona: str, job_to_be_done: str) -> Dict:
        """Process persona and job description to extract key information"""
        persona_profile = {
            "raw_persona": persona,
            "raw_job": job_to_be_done,
            "role": self._extract_role(persona),
            "domain": self._extract_domain(persona),
            "expertise_level": self._extract_expertise_level(persona),
            "keywords": self._extract_persona_keywords(persona),
            "job_type": self._extract_job_type(job_to_be_done),
            "job_keywords": self._extract_job_keywords(job_to_be_done),
            "action_words": self._extract_action_words(job_to_be_done),
            "success_criteria": self._extract_success_criteria(job_to_be_done)
        }
        
        return persona_profile
    
    def _extract_role(self, persona: str) -> str:
        """Extract the primary role from persona description"""
        if not persona:
            return "general"
        persona_lower = persona.lower()
        
        # Direct role matching
        for role in self.role_domains.keys():
            if role in persona_lower:
                return role
        
        # Pattern matching for roles
        role_patterns = {
            "researcher": r"(phd|research|scientist|academic)",
            "student": r"(student|undergraduate|graduate|learner)",
            "analyst": r"(analyst|investment|financial|business)",
            "journalist": r"(journalist|reporter|writer|media)",
            "entrepreneur": r"(entrepreneur|founder|startup|business owner)",
            "developer": r"(developer|programmer|engineer|coder)",
            "manager": r"(manager|director|executive|lead)",
            "travel planner": r"(travel planner|trip planner|travel agent|travel advisor)",
            "tourist": r"(tourist|vacationer|visitor)",
            "traveler": r"(traveler|traveller|backpacker|explorer)"
        }
        
        for role, pattern in role_patterns.items():
            if re.search(pattern, persona_lower):
                return role
        
        return "general"
    
    def _extract_domain(self, persona: str) -> str:
        """Extract the domain/field from persona description"""
        persona_lower = persona.lower()
        
        # Common domains
        domains = {
            "technology": ["tech", "technology", "software", "computer", "ai", "ml", "data science"],
            "biology": ["biology", "bio", "life science", "medical", "health"],
            "chemistry": ["chemistry", "chemical", "organic", "inorganic"],
            "finance": ["finance", "financial", "investment", "banking", "economics"],
            "business": ["business", "management", "marketing", "sales"],
            "education": ["education", "teaching", "academic", "school"],
            "engineering": ["engineering", "mechanical", "electrical", "civil"],
            "law": ["law", "legal", "attorney", "lawyer"],
            "travel": ["travel", "tourism", "hospitality", "destination", "vacation", "trip", "journey"]
        }
        
        for domain, keywords in domains.items():
            if any(keyword in persona_lower for keyword in keywords):
                return domain
        
        return "general"
    
    def _extract_expertise_level(self, persona: str) -> str:
        """Extract expertise level from persona description"""
        persona_lower = persona.lower()
        
        if any(term in persona_lower for term in ["phd", "doctor", "professor", "senior", "expert", "lead"]):
            return "expert"
        elif any(term in persona_lower for term in ["master", "graduate", "experienced", "analyst"]):
            return "intermediate"
        elif any(term in persona_lower for term in ["student", "undergraduate", "beginner", "junior"]):
            return "beginner"
        else:
            return "intermediate"
    
    def _extract_persona_keywords(self, persona: str) -> List[str]:
        """Extract relevant keywords from persona description"""
        keywords = set()
        
        # Extract using NLP
        if self.text_processor.nlp:
            nlp_keywords = self.text_processor.extract_keywords(persona, top_n=15)
            keywords.update(nlp_keywords)
        
        # Add domain-specific keywords based on detected role
        role = self._extract_role(persona)
        if role in self.role_domains:
            keywords.update(self.role_domains[role])
        
        # Extract entities
        entities = self.text_processor.extract_entities(persona)
        for entity_type, entity_list in entities.items():
            if entity_type in ["ORG", "PERSON", "GPE"]:  # Organizations, persons, places
                keywords.update([ent.lower() for ent in entity_list])
        
        return list(keywords)
    
    def _extract_job_type(self, job_to_be_done: str) -> str:
        """Extract the type of job from job description"""
        job_lower = job_to_be_done.lower()
        
        for job_type, action_words in self.job_actions.items():
            if any(action in job_lower for action in action_words):
                return job_type
        
        return "analyze"  # Default
    
    def _extract_job_keywords(self, job_to_be_done: str) -> List[str]:
        """Extract relevant keywords from job description"""
        keywords = set()
        
        # Extract using NLP
        if self.text_processor.nlp:
            nlp_keywords = self.text_processor.extract_keywords(job_to_be_done, top_n=20)
            keywords.update(nlp_keywords)
        
        # Extract quoted terms (often important concepts)
        quoted_terms = re.findall(r'"([^"]*)"', job_to_be_done)
        keywords.update([term.lower() for term in quoted_terms])
        
        # Extract capitalized terms (often important concepts)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+\b', job_to_be_done)
        keywords.update([term.lower() for term in capitalized_terms])
        
        return list(keywords)
    
    def _extract_action_words(self, job_to_be_done: str) -> List[str]:
        """Extract action words from job description"""
        return self.text_processor.extract_action_words(job_to_be_done)
    
    def _extract_success_criteria(self, job_to_be_done: str) -> List[str]:
        """Extract success criteria from job description"""
        criteria = []
        
        # Look for result-oriented phrases
        result_patterns = [
            r"focus(?:ing)? on ([^.]+)",
            r"identify ([^.]+)",
            r"analyze ([^.]+)",
            r"summarize ([^.]+)",
            r"review ([^.]+)",
            r"prepare ([^.]+)"
        ]
        
        for pattern in result_patterns:
            matches = re.findall(pattern, job_to_be_done, re.IGNORECASE)
            criteria.extend(matches)
        
        # Clean and filter criteria
        cleaned_criteria = []
        for criterion in criteria:
            criterion = criterion.strip()
            if len(criterion) > 5 and len(criterion) < 100:
                cleaned_criteria.append(criterion)
        
        return cleaned_criteria[:5]  # Top 5 criteria
