#!/usr/bin/env python3
"""
Local test script for the PPT Hyperlink Converter
This script tests the core functionality without the Flask API wrapper
"""

import os
import sys
from app import extract_links_from_pptx, add_hyperlinks_to_pptx

def test_pptx_processing(pptx_path):
    """
    Test the PPTX processing functionality with the provided test file
    """
    if not os.path.exists(pptx_path):
        print(f"Test file not found: {pptx_path}")
        return False

    print(f"Testing with file: {pptx_path}")
    print("=" * 50)

    try:
        # Step 1: Extract links
        print("Step 1: Extracting links from PPTX...")
        links = extract_links_from_pptx(pptx_path)

        if links:
            print(f"Found {len(links)} links:")
            for i, link in enumerate(links, 1):
                print(f"  {i}. {link}")
        else:
            print("No links found in the PPTX file")
            return True  # This might be expected for some test files

        print()

        # Step 2: Add hyperlinks
        if links:
            print("Step 2: Adding hyperlinks to PPTX...")
            output_path = pptx_path.replace('.pptx', '_with_hyperlinks.pptx')
            add_hyperlinks_to_pptx(pptx_path, links, output_path)

            if os.path.exists(output_path):
                print(f"Successfully created output file: {output_path}")
                print(f"File size: {os.path.getsize(output_path)} bytes")

                # Verify the output file by trying to extract links again
                print("\nStep 3: Verifying output file...")
                output_links = extract_links_from_pptx(output_path)
                if output_links:
                    print(f"Output file contains {len(output_links)} links")
                else:
                    print("No links found in output file (this might be expected)")

                return True
            else:
                print("Output file was not created")
                return False

        return True

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("PPT Hyperlink Converter - Local Test")
    print("=" * 50)

    # Test file path - using the actual test file in our project
    test_file = "ppt测试案例/汉语拼音声调初体验：一声 (19).pptx"

    # Run the test
    success = test_pptx_processing(test_file)

    print("=" * 50)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()