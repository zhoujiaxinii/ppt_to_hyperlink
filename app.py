from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import os
import requests
import zipfile
import tempfile
import re
import shutil
from datetime import datetime
from pptx import Presentation
from qcloud_cos import CosConfig, CosS3Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Tencent Cloud COS Configuration
# 请在环境变量中设置以下配置或在此处填写您的COS信息
COS_SECRET_ID = os.environ.get("COS_SECRET_ID", "YOUR_SECRET_ID")
COS_SECRET_KEY = os.environ.get("COS_SECRET_KEY", "YOUR_SECRET_KEY")
COS_REGION = os.environ.get("COS_REGION", "YOUR_REGION")  # e.g., "ap-nanjing"
COS_BUCKET = os.environ.get("COS_BUCKET", "YOUR_BUCKET")

# Initialize COS client
cos_config = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
cos_client = CosS3Client(cos_config)

def extract_links_from_pptx(pptx_path):
    """
    Extract media and game links from PPTX file by examining its XML content

    Args:
        pptx_path (str): Path to the PPTX file

    Returns:
        set: Set of unique links found in the PPTX file
    """
    links = set()

    # Media link pattern (audio/video files)
    media_pattern = r'https?://[a-zA-Z0-9./_-]+\.(mp3|mp4|wav|avi|mov|wmv|flv|ogg|webm)'

    # Game link pattern (index.html?data_url=...json)
    game_pattern = r'https?://[a-zA-Z0-9./_-]+/index\.html\?data_url=https?://[a-zA-Z0-9./_%-]+?\.json'

    try:
        # Extract PPTX file (which is essentially a ZIP file)
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(pptx_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)

            # Walk through all files in the extracted directory
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.xml') or file.endswith('.rels'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()

                                # Find media links
                                media_matches = re.findall(media_pattern, content)
                                for match in media_matches:
                                    # Reconstruct full URL
                                    full_match = re.search(media_pattern.replace(r'\.(mp3|mp4|wav|avi|mov|wmv|flv|ogg|webm)', f'.{match}'), content)
                                    if full_match:
                                        links.add(full_match.group(0))

                                # Find game links
                                game_matches = re.findall(game_pattern, content)
                                links.update(game_matches)

                        except Exception as e:
                            logger.warning(f"Error reading file {file_path}: {str(e)}")
                            continue

    except Exception as e:
        logger.error(f"Error extracting links from PPTX: {str(e)}")
        raise

    return links

def add_hyperlinks_to_pptx(pptx_path, links, output_path):
    """
    Add hyperlinks to text in PPTX file that matches the extracted links

    Args:
        pptx_path (str): Path to the input PPTX file
        links (set): Set of links to convert to hyperlinks
        output_path (str): Path for the output PPTX file
    """
    try:
        # Load the presentation
        prs = Presentation(pptx_path)

        # Track conversions for logging
        conversions_made = 0

        # Iterate through all slides
        for slide_idx, slide in enumerate(prs.slides):
            # Iterate through all shapes in the slide
            for shape_idx, shape in enumerate(slide.shapes):
                # Check if shape has text frame
                if hasattr(shape, 'text_frame') and shape.has_text_frame:
                    # Iterate through all paragraphs in the text frame
                    for para_idx, paragraph in enumerate(shape.text_frame.paragraphs):
                        paragraph_text = paragraph.text

                        # Check if any link is present in this paragraph
                        for link in links:
                            if link in paragraph_text:
                                logger.info(f"Found link '{link}' in slide {slide_idx + 1}, shape {shape_idx + 1}, paragraph {para_idx + 1}")

                                # Clear existing runs
                                paragraph.clear()

                                # Add new run with hyperlink
                                run = paragraph.add_run()
                                run.text = link
                                run.hyperlink.address = link

                                conversions_made += 1
                                break  # Only process one link per paragraph

        # Save the modified presentation
        prs.save(output_path)
        logger.info(f"Successfully processed PPTX file. Made {conversions_made} hyperlink conversions.")

    except Exception as e:
        logger.error(f"Error adding hyperlinks to PPTX: {str(e)}")
        raise

def upload_to_cos(file_path, cos_key):
    """
    Upload file to Tencent Cloud COS

    Args:
        file_path (str): Local file path
        cos_key (str): Key (path) in COS bucket

    Returns:
        str: COS download URL
    """
    try:
        # Upload file to COS
        with open(file_path, 'rb') as file_data:
            cos_client.put_object(
                Bucket=COS_BUCKET,
                Body=file_data,
                Key=cos_key,
                StorageClass='STANDARD'
            )

        # Construct download URL
        download_url = f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{cos_key}"
        logger.info(f"File uploaded to COS successfully: {download_url}")

        return download_url

    except Exception as e:
        logger.error(f"Error uploading to COS: {str(e)}")
        raise

@app.route('/process_pptx', methods=['POST'])
def process_pptx():
    """
    Process PPTX file: download, extract links, add hyperlinks, upload to COS

    Expected JSON payload:
    {
        "pptx_url": "https://example.com/file.pptx"
    }

    Returns:
        JSON response with COS download URL
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'pptx_url' not in data:
            raise BadRequest("Missing 'pptx_url' in request body")

        pptx_url = data['pptx_url']
        logger.info(f"Processing PPTX from URL: {pptx_url}")

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download PPTX file
            logger.info("Downloading PPTX file...")
            response = requests.get(pptx_url, stream=True)
            response.raise_for_status()

            # Save downloaded file
            input_pptx_path = os.path.join(temp_dir, "input.pptx")
            with open(input_pptx_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded PPTX file to: {input_pptx_path}")

            # Extract links from PPTX
            logger.info("Extracting links from PPTX...")
            links = extract_links_from_pptx(input_pptx_path)
            logger.info(f"Found {len(links)} links: {list(links)}")

            if not links:
                logger.warning("No links found in PPTX file")
                return jsonify({
                    "success": False,
                    "message": "No media or game links found in the PPTX file"
                }), 400

            # Add hyperlinks to PPTX
            logger.info("Adding hyperlinks to PPTX...")
            output_pptx_path = os.path.join(temp_dir, "output.pptx")
            add_hyperlinks_to_pptx(input_pptx_path, links, output_pptx_path)

            # Generate unique filename for COS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cos_key = f"processed_pptx/hyperlink_converted_{timestamp}.pptx"

            # Upload to COS
            logger.info("Uploading processed PPTX to COS...")
            download_url = upload_to_cos(output_pptx_path, cos_key)

            return jsonify({
                "success": True,
                "message": "PPTX file processed successfully",
                "download_url": download_url,
                "links_found": list(links),
                "links_converted": len(links)
            })

    except requests.RequestException as e:
        logger.error(f"Error downloading PPTX file: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error downloading PPTX file: {str(e)}"
        }), 400

    except Exception as e:
        logger.error(f"Error processing PPTX: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error processing PPTX: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PPT Hyperlink Converter"})

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "service": "PPT Hyperlink Converter API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process_pptx": {
                "description": "Process PPTX file to add hyperlinks",
                "payload": {
                    "pptx_url": "URL of the PPTX file to process"
                },
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "download_url": "string (COS download URL)",
                    "links_found": "array of strings",
                    "links_converted": "number"
                }
            },
            "GET /health": "Health check endpoint"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)