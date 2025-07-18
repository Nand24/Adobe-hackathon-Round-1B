"""
Configuration settings for Adobe India Hackathon
"""

class Config:
    # Performance constraints
    ROUND1A_MAX_TIME = 10  # seconds for 50-page PDF
    ROUND1B_MAX_TIME = 60  # seconds for 3-5 documents
    MAX_MODEL_SIZE_1A = 200  # MB
    MAX_MODEL_SIZE_1B = 1000  # MB
    
    # System constraints
    MAX_RAM_USAGE = 16  # GB
    CPU_CORES = 8
    
    # PDF processing settings
    MAX_PDF_PAGES = 50
    MIN_HEADING_LENGTH = 3
    MAX_HEADING_LENGTH = 200
    
    # Heading detection thresholds
    FONT_SIZE_THRESHOLD = 0.1  # Relative to average font size
    HEADING_POSITION_THRESHOLD = 0.2  # Relative to page height
    
    # NLP model settings
    MAX_SEQUENCE_LENGTH = 512
    BATCH_SIZE = 16
    
    # Relevance scoring weights
    SEMANTIC_WEIGHT = 0.4
    KEYWORD_WEIGHT = 0.25
    STRUCTURAL_WEIGHT = 0.2
    QUALITY_WEIGHT = 0.15
    
    # File paths
    MODELS_DIR = "models"
    TEMP_DIR = "temp"
    
    # Output format settings
    JSON_INDENT = 2
    ENSURE_ASCII = False
