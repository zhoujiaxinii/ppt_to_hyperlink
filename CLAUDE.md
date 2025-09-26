# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a Flask-based RESTful API that automatically converts media and game links within PPTX files into clickable hyperlinks. It's designed for scenarios like education and training to automate the processing of presentation files with numerous media resources. The application is integrated with Tencent Cloud COS for cloud storage. The core logic is in `app.py`.

## Core Features

- **Media and Game Link Recognition**: Automatically identifies audio, video, and specific game links.
- **Hyperlink Conversion**: Converts identified plain text links into clickable hyperlinks.
- **Cloud Storage Integration**: Supports uploading processed files to Tencent Cloud COS.
- **RESTful API**: Provides API endpoints for integration.
- **Docker Support**: Includes a full setup for containerized deployment.

## Technology Stack

- **Python 3.8+**: Main programming language.
- **Flask**: Web framework.
- **python-pptx**: Library for manipulating PowerPoint files.
- **qcloud-cos-python-sdk-v5**: Tencent Cloud COS SDK.
- **Docker**: For containerization.

## Development and Deployment

### Local Development

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set environment variables for Tencent Cloud COS**:
    ```bash
    export COS_SECRET_ID=your_secret_id
    export COS_SECRET_KEY=your_secret_key
    export COS_REGION=your_region
    export COS_BUCKET=your_bucket
    ```
3.  **Run the application**:
    ```bash
    python home/ubuntu/ppt_to_hyperlink/app.py
    ```

### Docker Deployment (Recommended)

1.  **Build and start the services**:
    ```bash
    docker-compose up --build -d
    ```
2.  **View service status**:
    ```bash
    docker-compose ps
    ```
3.  **View logs**:
    ```bash
    docker-compose logs -f
    ```

### Testing

Run the local test script with a specific PPTX file:

```bash
python home/ubuntu/ppt_to_hyperlink/test_local_file.py 'd:\code\ppt_to_hyperlink_project\ppt测试案例\汉语拼音声调初体验：一声 (15).pptx'
```

## API Usage

- **Base URL**: `http://localhost:5000`
- **Endpoints**:
    - `POST /process_pptx`: Processes a PPTX file from a given URL.
    - `GET /health`: Health check.
    - `GET /`: API documentation.

### Example Request

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"pptx_url": "https://example.com/test.pptx"}' \
     http://localhost:5000/process_pptx
```

## Project Structure

```
ppt_to_hyperlink/
├── app.py                 # Flask API main application
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image build file
├── docker-compose.yml     # Docker Compose configuration
├── test_local_file.py     # Local test script
└── README.md              # Project documentation
```

## Link Recognition Rules

- **Media Links**: `.mp3`, `.wav`, `.ogg`, `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`.
- **Game Links**: URLs matching `https://domain.com/path/index.html?data_url=https://domain.com/path/game.json`.
