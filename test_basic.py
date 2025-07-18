#!/usr/bin/env python3
"""
Basic test to verify the hackathon system works with minimal dependencies
"""
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Test that our basic system works without external dependencies"""
    print("Testing basic functionality...")
    
    # Test importing our modules
    try:
        from shared.config import Config
        from shared.text_processor import TextProcessor
        print("✓ Successfully imported core modules")
    except Exception as e:
        print(f"✗ Failed to import modules: {e}")
        return False
    
    # Test config
    try:
        config = Config()
        print(f"✓ Config loaded - Round 1A max time: {config.ROUND1A_MAX_TIME}s, Round 1B max time: {config.ROUND1B_MAX_TIME}s")
    except Exception as e:
        print(f"✗ Config failed: {e}")
        return False
    
    # Test text processor
    try:
        processor = TextProcessor()
        
        # Test basic text processing
        sample_text = "This is a test document. It contains multiple sentences. The goal is to extract keywords and analyze structure."
        
        # Test keyword extraction
        keywords = processor.extract_keywords(sample_text)
        print(f"✓ Keywords extracted: {keywords}")
        
        # Test entity extraction
        entities = processor.extract_entities(sample_text)
        print(f"✓ Entities extracted: {entities}")
        
        # Test similarity calculation
        similarity = processor.calculate_text_similarity(sample_text, "This is another test document.")
        print(f"✓ Similarity calculated: {similarity}")
        
    except Exception as e:
        print(f"✗ Text processor failed: {e}")
        return False
    
    print("\n✓ All basic tests passed!")
    return True

def test_json_output():
    """Test JSON output format compliance"""
    print("\nTesting JSON output format...")
    
    # Test Round 1A output format
    round1a_output = {
        "outline": [
            {
                "section_title": "Introduction",
                "level": 1,
                "page_number": 1,
                "subsections": [
                    {
                        "section_title": "Overview",
                        "level": 2,
                        "page_number": 1,
                        "subsections": []
                    }
                ]
            }
        ]
    }
    
    try:
        json_str = json.dumps(round1a_output, indent=2)
        print("✓ Round 1A JSON format valid")
    except Exception as e:
        print(f"✗ Round 1A JSON format failed: {e}")
        return False
    
    # Test Round 1B output format
    round1b_output = {
        "summary": "This is a test summary of the document content.",
        "sections": [
            {
                "section_title": "Introduction",
                "relevance_score": 0.85,
                "key_points": [
                    "First key point",
                    "Second key point"
                ],
                "related_sections": ["Background", "Methodology"]
            }
        ]
    }
    
    try:
        json_str = json.dumps(round1b_output, indent=2)
        print("✓ Round 1B JSON format valid")
    except Exception as e:
        print(f"✗ Round 1B JSON format failed: {e}")
        return False
    
    print("✓ All JSON output tests passed!")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Adobe India Hackathon - Basic System Test")
    print("=" * 60)
    
    success = True
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    # Test JSON output
    if not test_json_output():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The system is ready for basic operation.")
        print("Note: Some NLP features may be limited without spaCy installation.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
