
import os
import shutil
from datetime import datetime
from app import extract_links_from_pptx, add_hyperlinks_to_pptx

def test_local_pptx(input_path, output_dir):
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        print(f"Processing file: {input_path}")

        # 1. Extract links
        links = extract_links_from_pptx(input_path)
        if not links:
            print("No links found to process.")
            # Still, copy the original file to the output directory
            shutil.copy(input_path, output_dir)
            return

        print(f"Found {len(links)} links: {links}")

        # 2. Add hyperlinks
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"hyperlink_converted_{timestamp}.pptx"
        output_path = os.path.join(output_dir, output_filename)

        add_hyperlinks_to_pptx(input_path, links, output_path)

        print(f"Successfully processed file and saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_local_file.py <path_to_pptx_file>")
        sys.exit(1)

    pptx_file_path = sys.argv[1]

    # The output directory is also on the user's machine
    output_folder = 'D:\\code\\ppt_to_hyperlink_project\\ppt处理后案例'


    test_local_pptx(pptx_file_path, output_folder)
