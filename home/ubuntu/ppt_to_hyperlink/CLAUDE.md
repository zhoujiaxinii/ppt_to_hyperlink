# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This project is a Flask-based RESTful API that automatically converts media and game links within PPTX files into clickable hyperlinks. It integrates with Tencent Cloud COS for cloud storage. The entire application logic is contained within `app.py`.

## Common Commands

### Development
*   **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
*   **Run the application (local):**
    ```bash
    # Set required environment variables for Tencent Cloud COS
    export COS_SECRET_ID=your_secret_id
    export COS_SECRET_KEY=your_secret_key
    export COS_REGION=your_region
    export COS_BUCKET=your_bucket

    python app.py
    ```
*   **Run with Docker (recommended):**
    ```bash
    docker-compose up --build -d
    ```

### Testing
*   **Run tests:**
    ```bash
    python test_local.py
    ```
