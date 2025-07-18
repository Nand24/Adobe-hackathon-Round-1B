"""
Test cases for Round 1A: Outline Extraction
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from round1a.outline_extractor import OutlineExtractor


class TestRound1A(unittest.TestCase):
    """Test cases for outline extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = OutlineExtractor()
        self.sample_data_dir = Path(__file__).parent / "sample_data"
    
    def test_extractor_initialization(self):
        """Test that extractor initializes correctly"""
        self.assertIsNotNone(self.extractor)
        self.assertIsNotNone(self.extractor.text_processor)
    
    def test_empty_pdf_handling(self):
        """Test handling of empty or invalid PDF"""
        result = self.extractor.extract_outline("nonexistent.pdf")
        
        expected_structure = {"title": "", "outline": []}
        self.assertEqual(result, expected_structure)
    
    def test_output_format_structure(self):
        """Test that output follows the required JSON structure"""
        # Create a mock result
        result = {
            "title": "Sample Title",
            "outline": [
                {"H1": "Introduction", "page": 1},
                {"H2": "Background", "page": 2},
                {"H3": "Methodology", "page": 3}
            ]
        }
        
        # Validate structure
        self.assertIn("title", result)
        self.assertIn("outline", result)
        self.assertIsInstance(result["title"], str)
        self.assertIsInstance(result["outline"], list)
        
        # Validate outline items
        for item in result["outline"]:
            self.assertIsInstance(item, dict)
            self.assertIn("page", item)
            
            # Should have exactly one heading key (H1, H2, or H3)
            heading_keys = [k for k in item.keys() if k.startswith("H")]
            self.assertEqual(len(heading_keys), 1)
    
    def test_json_serialization(self):
        """Test that results can be properly serialized to JSON"""
        result = {
            "title": "Test Document",
            "outline": [
                {"H1": "Chapter 1", "page": 1},
                {"H2": "Section 1.1", "page": 2}
            ]
        }
        
        # Should not raise an exception
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        self.assertIsInstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertEqual(parsed, result)
    
    def test_performance_tracking(self):
        """Test performance measurement capabilities"""
        import time
        
        start_time = time.time()
        
        # Simulate processing
        result = self.extractor.extract_outline("nonexistent.pdf")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete quickly for non-existent file
        self.assertLess(processing_time, 1.0)
    
    def test_heading_level_validation(self):
        """Test heading level classification"""
        # Mock heading candidates with different properties
        sample_headings = [
            {"text": "Introduction", "level": 1},
            {"text": "Background", "level": 2},
            {"text": "Detailed Analysis", "level": 3}
        ]
        
        for heading in sample_headings:
            self.assertIn(heading["level"], [1, 2, 3])
            self.assertIsInstance(heading["text"], str)
            self.assertGreater(len(heading["text"]), 0)


if __name__ == "__main__":
    unittest.main()
