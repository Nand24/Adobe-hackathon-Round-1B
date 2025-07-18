"""
Text processing utilities for NLP tasks
"""

import re
import string
from typing import List, Dict, Set
from collections import Counter

# Try to import spaCy, but gracefully handle if not available
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Using basic text processing.")


class TextProcessor:
    """Utility class for text processing and NLP tasks"""
    
    def __init__(self):
        """Initialize with spaCy model if available"""
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found. Using basic text processing.")
                self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special formatting characters
        text = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)\[\]\"\'\/]', '', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        if self.nlp:
            # Use spaCy if available
            doc = self.nlp(text)
            
            # Extract meaningful tokens
            keywords = []
            for token in doc:
                # Filter out stop words, punctuation, and short words
                if (not token.is_stop and 
                    not token.is_punct and 
                    len(token.text) > 2 and
                    token.pos_ in ['NOUN', 'ADJ', 'VERB', 'PROPN']):
                    keywords.append(token.lemma_.lower())
            
            # Count frequency and return top keywords
            keyword_counts = Counter(keywords)
            return [word for word, count in keyword_counts.most_common(top_n)]
        else:
            # Basic keyword extraction without spaCy
            # Remove punctuation and convert to lowercase
            text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
            words = text_clean.split()
            
            # Basic stop words list
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            # Filter words
            keywords = [word for word in words if len(word) > 2 and word not in stop_words]
            
            # Count frequency and return top keywords
            keyword_counts = Counter(keywords)
            return [word for word, count in keyword_counts.most_common(top_n)]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        if not text:
            return {}
        
        if self.nlp:
            doc = self.nlp(text)
            
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
            
            return entities
        else:
            # Basic entity extraction without spaCy
            entities = {}
            
            # Extract capitalized words as potential entities
            capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            if capitalized_words:
                entities['PERSON'] = list(set(capitalized_words))
            
            # Extract numbers as potential quantities
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
            if numbers:
                entities['NUMBER'] = list(set(numbers))
            
            return entities
    
    def get_sentence_embeddings(self, sentences: List[str]) -> List:
        """Get sentence embeddings (placeholder for actual implementation)"""
        # This would use sentence-transformers in actual implementation
        # For now, return empty list as placeholder
        return []
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        if self.nlp:
            doc1 = self.nlp(text1)
            doc2 = self.nlp(text2)
            
            return doc1.similarity(doc2)
        else:
            # Basic similarity using word overlap
            words1 = set(re.findall(r'\b\w+\b', text1.lower()))
            words2 = set(re.findall(r'\b\w+\b', text2.lower()))
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
    
    def extract_action_words(self, text: str) -> List[str]:
        """Extract action words (verbs) from text"""
        if not text:
            return []
        
        if self.nlp:
            doc = self.nlp(text)
            
            action_words = []
            for token in doc:
                if token.pos_ == 'VERB' and not token.is_stop:
                    action_words.append(token.lemma_.lower())
            
            return list(set(action_words))  # Remove duplicates
        else:
            # Basic verb extraction using common verb patterns
            text_lower = text.lower()
            
            # Common action words
            action_patterns = [
                r'\b(analyze|analyzing|analyzed)\b',
                r'\b(study|studying|studied)\b',
                r'\b(research|researching|researched)\b',
                r'\b(review|reviewing|reviewed)\b',
                r'\b(examine|examining|examined)\b',
                r'\b(investigate|investigating|investigated)\b',
                r'\b(identify|identifying|identified)\b',
                r'\b(find|finding|found)\b',
                r'\b(discover|discovering|discovered)\b',
                r'\b(determine|determining|determined)\b',
                r'\b(prepare|preparing|prepared)\b',
                r'\b(create|creating|created)\b',
                r'\b(develop|developing|developed)\b',
                r'\b(build|building|built)\b',
                r'\b(design|designing|designed)\b',
                r'\b(learn|learning|learned)\b',
                r'\b(understand|understanding|understood)\b',
                r'\b(compare|comparing|compared)\b',
                r'\b(evaluate|evaluating|evaluated)\b',
                r'\b(assess|assessing|assessed)\b'
            ]
            
            action_words = []
            for pattern in action_patterns:
                matches = re.findall(pattern, text_lower)
                action_words.extend(matches)
            
            return list(set(action_words))  # Remove duplicates
    
    def is_question(self, text: str) -> bool:
        """Check if text is a question"""
        text = text.strip()
        
        # Simple heuristics
        if text.endswith('?'):
            return True
        
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        words = text.lower().split()
        
        return len(words) > 0 and words[0] in question_words
    
    def extract_domain_terms(self, text: str, domain_keywords: Set[str]) -> List[str]:
        """Extract domain-specific terms from text"""
        if not text:
            return []
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        domain_terms = []
        for word in words:
            if word in domain_keywords:
                domain_terms.append(word)
        
        return list(set(domain_terms))
    
    def get_text_complexity_score(self, text: str) -> float:
        """Calculate text complexity score"""
        if not text:
            return 0.0
        
        # Simple readability metrics
        sentences = re.split(r'[.!?]+', text)
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count complex words (>6 characters)
        complex_words = [word for word in words if len(word) > 6]
        complex_word_ratio = len(complex_words) / len(words) if words else 0
        
        # Simple complexity score
        complexity = (avg_sentence_length * 0.4 + complex_word_ratio * 100 * 0.6)
        
        return min(complexity / 20, 1.0)  # Normalize to 0-1
    
    def segment_text_by_topics(self, text: str, max_segments: int = 10) -> List[str]:
        """Segment text into topical sections"""
        if not text:
            return []
        
        # Simple segmentation by paragraphs for now
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filter out very short paragraphs
        segments = [p.strip() for p in paragraphs if len(p.strip()) > 50]
        
        return segments[:max_segments]
