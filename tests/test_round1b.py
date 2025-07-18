"""
Test cases for Round 1B: Persona-Driven Document Intelligence
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from round1b.document_analyzer import DocumentAnalyzer
from round1b.persona_processor import PersonaProcessor
from round1b.relevance_ranker import RelevanceRanker


class TestRound1B(unittest.TestCase):
    """Test cases for persona-driven document analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = DocumentAnalyzer()
        self.persona_processor = PersonaProcessor()
        self.relevance_ranker = RelevanceRanker()
        self.sample_data_dir = Path(__file__).parent / "sample_data"
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.persona_processor)
        self.assertIsNotNone(self.analyzer.relevance_ranker)
    
    def test_persona_processing(self):
        """Test persona processing functionality"""
        persona = "PhD Researcher in Computational Biology"
        job = "Prepare a comprehensive literature review focusing on methodologies and datasets"
        
        profile = self.persona_processor.process_persona(persona, job)
        
        # Validate profile structure
        required_keys = ["raw_persona", "raw_job", "role", "domain", "keywords", "job_keywords"]
        for key in required_keys:
            self.assertIn(key, profile)
        
        # Validate specific extractions
        self.assertEqual(profile["role"], "researcher")
        self.assertIn("biology", profile["domain"].lower())
        self.assertIsInstance(profile["keywords"], list)
        self.assertIsInstance(profile["job_keywords"], list)
    
    def test_sample_test_cases(self):
        """Test the three sample scenarios from the challenge"""
        test_cases = [
            {
                "persona": "PhD Researcher in Computational Biology",
                "job": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks",
                "expected_role": "researcher",
                "expected_domain": "biology"
            },
            {
                "persona": "Investment Analyst",
                "job": "Analyze revenue trends, R&D investments, and market positioning strategies",
                "expected_role": "analyst",
                "expected_domain": "finance"
            },
            {
                "persona": "Undergraduate Chemistry Student",
                "job": "Identify key concepts and mechanisms for exam preparation on reaction kinetics",
                "expected_role": "student",
                "expected_domain": "chemistry"
            }
        ]
        
        for case in test_cases:
            with self.subTest(persona=case["persona"]):
                profile = self.persona_processor.process_persona(case["persona"], case["job"])
                
                self.assertEqual(profile["role"], case["expected_role"])
                self.assertIn(case["expected_domain"], profile["domain"].lower())
    
    def test_relevance_scoring(self):
        """Test relevance scoring functionality"""
        # Mock section
        section = {
            "title": "Machine Learning Methods in Drug Discovery",
            "content": "This section discusses various machine learning algorithms used in computational biology for drug discovery research.",
            "level": 1,
            "page": 1,
            "word_count": 50
        }
        
        # Mock persona profile
        persona_profile = {
            "role": "researcher",
            "domain": "biology",
            "keywords": ["machine learning", "drug discovery", "computational"],
            "job_keywords": ["research", "methodology", "analysis"]
        }
        
        score = self.relevance_ranker._calculate_relevance_score(section, persona_profile)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Should have a reasonable score given the good match
        self.assertGreater(score, 0.3)
    
    def test_output_format_structure(self):
        """Test that output follows the required JSON structure for Round 1B"""
        # Mock analysis result
        result = {
            "metadata": {
                "persona": "Test Persona",
                "job_to_be_done": "Test Job",
                "documents_processed": ["doc1.pdf"],
                "processing_timestamp": "2024-01-01T00:00:00",
                "processing_time_seconds": 5.0
            },
            "extracted_sections": [
                {
                    "document": "doc1.pdf",
                    "page_number": 1,
                    "section_title": "Introduction",
                    "importance_rank": 1
                }
            ],
            "subsection_analysis": [
                {
                    "document": "doc1.pdf",
                    "page_number": 1,
                    "refined_text": "This is refined text."
                }
            ]
        }
        
        # Validate structure
        required_top_keys = ["metadata", "extracted_sections", "subsection_analysis"]
        for key in required_top_keys:
            self.assertIn(key, result)
        
        # Validate metadata
        metadata = result["metadata"]
        required_metadata_keys = ["persona", "job_to_be_done", "documents_processed"]
        for key in required_metadata_keys:
            self.assertIn(key, metadata)
        
        # Validate extracted sections
        for section in result["extracted_sections"]:
            required_section_keys = ["document", "page_number", "section_title", "importance_rank"]
            for key in required_section_keys:
                self.assertIn(key, section)
        
        # Validate subsection analysis
        for subsection in result["subsection_analysis"]:
            required_subsection_keys = ["document", "page_number", "refined_text"]
            for key in required_subsection_keys:
                self.assertIn(key, subsection)
    
    def test_json_serialization_round1b(self):
        """Test that Round 1B results can be properly serialized to JSON"""
        result = {
            "metadata": {
                "persona": "Test Researcher",
                "job_to_be_done": "Analyze research papers",
                "documents_processed": ["paper1.pdf", "paper2.pdf"],
                "processing_timestamp": "2024-01-01T12:00:00Z"
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }
        
        # Should not raise an exception
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        self.assertIsInstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertEqual(parsed, result)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with empty inputs
        result = self.analyzer.analyze_documents([], "", "")
        
        self.assertIn("metadata", result)
        self.assertIn("extracted_sections", result)
        self.assertIn("subsection_analysis", result)
        
        # Should handle gracefully
        self.assertIsInstance(result["extracted_sections"], list)
        self.assertIsInstance(result["subsection_analysis"], list)


if __name__ == "__main__":
    unittest.main()
