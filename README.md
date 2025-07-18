# Adobe India Hackathon - PDF Intelligence System

## Overview
This project implements a PDF document intelligence system for Adobe India Hackathon Round 1, supporting both outline extraction and persona-driven analysis.

## Rounds

### Round 1A: Document Outline Extraction
- **Task**: Extract structured outlines (Title, H1, H2, H3) from PDFs
- **Performance**: ≤10 seconds for 50-page PDF, ≤200MB models
- **Output**: JSON format with hierarchical headings and page numbers

### Round 1B: Persona-Driven Document Intelligence
- **Task**: Analyze document collections based on user persona and job-to-be-done
- **Performance**: ≤60 seconds for 3-5 documents, ≤1GB models
- **Output**: Ranked relevant sections with importance scores

## Quick Start

### Using Docker (Recommended)
```bash
# Build the container
docker build -t adobe-hackathon .

# Run Round 1A
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe-hackathon python src/main.py --input /app/input --round 1a

# Run Round 1B
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe-hackathon python src/main.py --input /app/input --round 1b
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run Round 1A
python src/main.py --input input/document.pdf --round 1a

# Run Round 1B (requires job_config.json)
python src/main.py --input input/ --round 1b
```

## Project Structure
```
├── src/
│   ├── main.py                       # Entry point
│   ├── round1a/
│   │   └── outline_extractor.py      # Outline extraction
│   ├── round1b/
│   │   ├── document_analyzer.py      # Main analyzer
│   │   ├── persona_processor.py      # Persona processing
│   │   ├── relevance_ranker.py       # Section ranking
│   │   └── section_extractor.py      # Section extraction
│   └── shared/
│       ├── pdf_utils.py              # PDF processing utilities
│       ├── text_processor.py         # NLP utilities
│       └── config.py                 # Configuration
├── tests/                            # Unit tests
├── input/                            # Sample input files
├── output/                           # Generated outputs
├── requirements.txt                  # Dependencies
└── Dockerfile                        # Container setup
```

## Input Format

### Round 1A
- Single PDF or text file
- Automatic fallback to text processing if PyMuPDF unavailable

### Round 1B
- Directory containing documents + `job_config.json`
- Example job_config.json:
```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare comprehensive literature review focusing on methodologies and datasets"
}
```

## Output Format

### Round 1A Output
```json
{
  "title": "Document Title",
  "outline": [
    {
      "section_title": "Introduction",
      "level": 1,
      "page_number": 1,
      "subsections": [...]
    }
  ]
}
```

### Round 1B Output
```json
{
  "metadata": {
    "persona": "...",
    "job_to_be_done": "...",
    "processing_time_seconds": 1.23
  },
  "extracted_sections": [
    {
      "document": "paper1.pdf",
      "page_number": 1,
      "section_title": "Introduction",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [...]
}
```

## Performance
- **Round 1A**: Processes documents in <1 second
- **Round 1B**: Processes multiple documents in <1 second
- **Memory**: Uses fallback mechanisms for minimal dependency requirements
- **Compatibility**: Works with or without PyMuPDF/spaCy installation

## Testing
```bash
# Run all tests
python -m unittest discover tests -v

# Run basic functionality test
python test_basic.py
```

## Dependencies
- **Core**: Python 3.8+
- **Optional**: PyMuPDF (for PDF processing), spaCy (for advanced NLP)
- **Fallback**: Text file processing and basic NLP when dependencies unavailable

## Architecture
- **Modular Design**: Separate components for each round
- **Fallback System**: Graceful degradation when dependencies unavailable
- **Performance Optimized**: Meets all timing constraints
- **Docker Ready**: Containerized for consistent deployment
