"""
Main entry point for Adobe India Hackathon PDF Intelligence System
Handles both Round 1A (outline extraction) and Round 1B (persona-driven analysis)
"""

import os
import sys
import argparse
import json
import time
import signal
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.dirname(__file__))

from round1a.outline_extractor import OutlineExtractor
from round1a.ml_outline_extractor import MLOutlineExtractor
from round1b.document_analyzer import DocumentAnalyzer
from round1b.ml_relevance_ranker import MLRelevanceRanker
from shared.config import Config


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Processing timeout exceeded")


def process_with_timeout(func, timeout_seconds, *args, **kwargs):
    """Execute function with timeout protection for Adobe constraints"""
    try:
        # Set up timeout signal (Unix/Linux only)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
        
        result = func(*args, **kwargs)
        
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)  # Cancel alarm
        
        return result, None
        
    except TimeoutError:
        return {"title": "", "outline": []}, f"Timeout: Processing exceeded {timeout_seconds}s limit"
    except Exception as e:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)  # Cancel alarm
        return {"title": "", "outline": []}, str(e)


def process_round1a(input_dir: str, output_dir: str):
    """Process Round 1A: Extract outlines from PDFs using ML-enhanced approach"""
    print("Starting Round 1A: Document Outline Extraction")
    
    # Try ML-enhanced extractor first, fallback to basic
    try:
        extractor = MLOutlineExtractor()
        ml_available = True
        print("✓ Using ML-enhanced outline extraction")
    except Exception as e:
        print(f"Warning: ML extractor failed, using basic extractor: {e}")
        extractor = OutlineExtractor()
        ml_available = False
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Handle both single files and directories
    if input_path.is_file():
        # Single file input
        all_files = [input_path] if input_path.suffix.lower() in ['.pdf', '.txt'] else []
    else:
        # Directory input
        pdf_files = list(input_path.glob("*.pdf"))
        txt_files = list(input_path.glob("*.txt"))
        all_files = pdf_files + txt_files
    
    if not all_files:
        print("No PDF or text files found in input directory")
        return
    
    for file_path in all_files:
        print(f"Processing: {file_path.name}")
        start_time = time.time()
        
        try:
            # Extract outline
            outline_data = extractor.extract_outline(str(file_path))
            
            # Generate output filename
            output_file = output_path / f"{file_path.stem}.json"
            
            # Save results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline_data, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            print(f"✅ Completed {file_path.name} in {processing_time:.2f}s")
            
            # Check performance constraint (10s for 50 pages)
            if processing_time > Config.ROUND1A_MAX_TIME:
                print(f"⚠️  Warning: Processing time ({processing_time:.2f}s) exceeds limit ({Config.ROUND1A_MAX_TIME}s)")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
            # Create empty output for failed files
            output_file = output_path / f"{file_path.stem}.json"
            with open(output_file, 'w') as f:
                json.dump({"title": "", "outline": []}, f)


def process_round1b(input_dir: str, output_dir: str):
    """Process Round 1B: Persona-driven document analysis"""
    print("Starting Round 1B: Persona-Driven Document Intelligence")
    
    analyzer = DocumentAnalyzer()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Handle both single files and directories
    if input_path.is_file():
        # Single file input - look for job config in same directory
        job_config_file = input_path.parent / "job_config.json"
        all_files = [input_path] if input_path.suffix.lower() in ['.pdf', '.txt'] else []
    else:
        # Directory input - look for job config in input directory
        job_config_file = input_path / "job_config.json"
        pdf_files = list(input_path.glob("*.pdf"))
        txt_files = list(input_path.glob("*.txt"))
        all_files = pdf_files + txt_files
    
    if not job_config_file.exists():
        print("❌ job_config.json not found in input directory")
        return
    
    # Load job configuration
    with open(job_config_file, 'r', encoding='utf-8') as f:
        job_config = json.load(f)
    
    if not all_files:
        print("No PDF or text files found in input directory")
        return
    
    print(f"Processing {len(all_files)} documents for persona analysis")
    start_time = time.time()
    
    try:
        # Analyze documents based on persona and job
        analysis_result = analyzer.analyze_documents(
            pdf_files=all_files,  # Updated to handle both PDF and text files
            persona=job_config.get("persona", {}).get("role", ""),
            job_to_be_done=job_config.get("job_to_be_done", {}).get("task", "")
        )
        
        # Save results
        output_file = output_path / "challenge1b_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        processing_time = time.time() - start_time
        print(f"✅ Completed persona analysis in {processing_time:.2f}s")
        
        # Check performance constraint (60s for 3-5 documents)
        if processing_time > Config.ROUND1B_MAX_TIME:
            print(f"⚠️  Warning: Processing time ({processing_time:.2f}s) exceeds limit ({Config.ROUND1B_MAX_TIME}s)")
            
    except Exception as e:
        print(f"❌ Error in persona analysis: {str(e)}")
        # Create empty output for failed analysis
        output_file = output_path / "challenge1b_output.json"
        with open(output_file, 'w') as f:
            json.dump({"metadata": {}, "extracted_sections": [], "subsection_analysis": []}, f)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Adobe India Hackathon PDF Intelligence System')
    parser.add_argument('--round', choices=['1a', '1b'], default='1a',
                        help='Round to execute (1a for outline extraction, 1b for persona analysis)')
    parser.add_argument('--input', default='/app/input',
                        help='Input directory path')
    parser.add_argument('--output', default='/app/output',
                        help='Output directory path')
    
    args = parser.parse_args()
    
    print(f"Adobe India Hackathon - Round {args.round.upper()}")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print("-" * 50)
    
    # Verify input directory exists
    if not os.path.exists(args.input):
        print(f"❌ Input directory not found: {args.input}")
        sys.exit(1)
    
    # Process based on round
    if args.round == '1a':
        process_round1a(args.input, args.output)
    elif args.round == '1b':
        process_round1b(args.input, args.output)
    
    print("-" * 50)
    print("Processing completed!")


if __name__ == "__main__":
    main()
