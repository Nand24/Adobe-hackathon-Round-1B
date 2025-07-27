# Adobe India Hackathon - Round 1 Solution

**"Connecting the Dots" Challenge - Complete Round 1 Solution**

Extract structured outlines from PDFs and power them up with persona-driven document intelligence.

## What This Does

**Round 1A**: Extract document outlines (title and headings H1, H2, H3) from PDF files  
**Round 1B**: Analyze document sections and provide persona-driven insights

## Input/Output

### Round 1A - Document Outline
**Input**: PDF files (up to 50 pages)  
**Output**: JSON with structure:
```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 }
  ]
}
```

### Round 1B - Persona Analysis
**Input**: PDF files + persona type (student/researcher/professional)  
**Output**: JSON with sections and persona-specific insights:
```json
{
  "sections": [
    {
      "title": "Introduction",
      "content": "Content text...",
      "page_start": 1,
      "page_end": 2
    }
  ],
  "personas": {
    "student": {
      "relevant_sections": [0],
      "insights": ["Key learning concepts"],
      "recommendations": ["Start with basics"]
    }
  }
}
```

## Technologies Used

- **Python 3.13**: Core runtime
- **PyMuPDF**: PDF processing
- **DistilBERT**: Heading classification (66MB)
- **Sentence-BERT**: Text similarity (90MB)
- **spaCy**: Natural language processing (43MB)
- **Total Model Size**: 199MB (under 200MB limit)

## How to Build and Run

### Docker (Recommended)
```bash
# Build
docker build --platform linux/amd64 -t adobe-solution .

# Run Round 1A
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe-solution --round 1a

# Run Round 1B
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe-solution --round 1b --persona student
```

### Local Development
```bash
pip install -r requirements.txt
python src/main.py --round 1a --input ./input --output ./output
python src/main.py --round 1b --input ./input --output ./output --persona student
```

## Project Structure

```
├── Dockerfile              # AMD64 Docker configuration
├── requirements.txt         # Python dependencies
├── src/
│   ├── main.py             # Entry point
│   ├── round1a/            # Document outline extraction
│   │   ├── outline_extractor.py
│   │   └── ml_outline_extractor.py
│   ├── round1b/            # Persona-driven analysis
│   │   ├── document_analyzer.py
│   │   ├── section_extractor.py
│   │   ├── persona_processor.py
│   │   └── relevance_ranker.py
│   └── shared/             # Shared utilities
│       ├── config.py
│       ├── pdf_utils.py
│       └── text_processor.py
├── input/                  # Place PDFs here
└── output/                 # Results appear here
```

## Performance

- **Speed**: < 1 second per PDF (well under 10s limit)
- **Memory**: Efficient with automatic fallbacks
- **Platform**: AMD64 compatible, CPU-only
- **Network**: Fully offline operation

## Adobe Hackathon Compliance

✅ Round 1A: Extracts title and H1/H2/H3 headings in exact format  
✅ Round 1B: Persona-driven section analysis and insights  
✅ Under 10 seconds per 50-page PDF  
✅ Models under 200MB total  
✅ Works offline (no network calls)  
✅ AMD64 Docker compatible  
✅ Processes from `/app/input` to `/app/output`  

Built for Adobe India Hackathon Round 1 - "Connecting the Dots" Challenge
