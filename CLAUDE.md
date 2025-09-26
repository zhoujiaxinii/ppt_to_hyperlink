# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based RESTful API service that automatically converts media and game links within PPTX files into clickable hyperlinks. The application downloads PPTX files, extracts embedded media/game links using XML parsing, converts them to hyperlinks, and uploads processed files to Tencent Cloud COS for download.

## Architecture

### Core Application Structure
- **Single-file Flask app** (`app.py`): Contains all API endpoints and business logic
- **Timeout management**: Uses custom threading-based timeout decorators for Windows compatibility
- **Stream processing**: Downloads and processes files in chunks to handle large files efficiently
- **Retry mechanisms**: Built-in retry logic for file downloads and COS uploads
- **Regex-based extraction**: Pre-compiled regex patterns for performance optimization

### Key Components
- **Link extraction**: Parses PPTX XML content to find media and game URLs using zipfile extraction
- **Hyperlink conversion**: Uses python-pptx library to modify presentation files
- **Cloud storage**: Integrates with Tencent Cloud COS for file storage and retrieval
- **Performance optimization**: 1-minute API timeout with optimized processing pipeline

## Common Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_REGION=your_region
export COS_BUCKET=your_bucket

# Run the application
python app.py
```

### Docker Development
```bash
# Build and run with Docker Compose (recommended)
docker-compose up --build -d

# View service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Testing
```bash
# Run local functionality test (bypasses API)
python test_local.py

# Test API endpoint with cURL
curl -X POST -H "Content-Type: application/json" \
     -d '{"pptx_url": "https://example.com/test.pptx"}' \
     http://localhost:5000/process_pptx

# Health check
curl http://localhost:5000/health
```

## Development Notes

### Environment Configuration
- **Required**: All COS_* environment variables must be set for cloud storage functionality
- **Without COS config**: Application will start but /process_pptx endpoint will fail with config errors
- **Timeout settings**: API_TIMEOUT (60s) and PROCESSING_TIMEOUT (45s) are optimized for 1-minute processing

### File Processing Pipeline
1. **Download** (with size limits and streaming)
2. **Extract links** (ZIP extraction + XML parsing with regex)
3. **Add hyperlinks** (python-pptx modification)
4. **Upload to COS** (with retry mechanism)

### Link Detection Rules
- **Media files**: .mp3, .mp4, .wav, .avi, .mov, .wmv, .flv, .ogg, .webm
- **Game links**: `index.html?data_url=*.json` pattern
- **Performance**: Uses pre-compiled regex patterns for efficient matching

### Error Handling Strategy
- **Timeout errors**: Custom TimeoutException with threading-based implementation
- **Download errors**: Exponential backoff retry with size validation
- **Processing errors**: Comprehensive logging with error classification
- **API responses**: Structured error responses with error_type classification

### Performance Considerations
- **File size limit**: 50MB maximum for faster processing
- **Chunk size**: 64KB chunks for optimal download speed
- **Timeout decorators**: Applied to long-running operations (extraction: 20s, hyperlinks: 15s)
- **Memory efficiency**: Uses temporary directories and stream processing

### Code Patterns
- **Timeout decorator pattern**: `@with_timeout(seconds)` for operation limits
- **Retry pattern**: Consistent retry logic across download and upload operations
- **Context managers**: Extensive use of `tempfile.TemporaryDirectory()` for cleanup
- **Logging strategy**: Structured logging with performance metrics and error classification