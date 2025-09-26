#!/usr/bin/env python3
"""
Test script for the improved PPT Hyperlink Converter API
Tests the fixes for timeout and 500 errors
"""

import requests
import json
import time
import sys

# Test configuration
API_BASE_URL = "http://localhost:5000"
TEST_FILE_URL = "https://ztonxue-test-1320844702.cos.ap-guangzhou.myqcloud.com/ppt%E6%B8%B8%E6%88%8F%E9%93%BE%E6%8E%A5.pptx"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("[PASS] Health endpoint working")
            return True
        else:
            print(f"[FAIL] Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Health endpoint error: {str(e)}")
        return False

def test_process_pptx():
    """Test the main PPTX processing endpoint"""
    print("Testing PPTX processing endpoint...")

    payload = {
        "pptx_url": TEST_FILE_URL
    }

    try:
        print(f"Sending request to process: {TEST_FILE_URL}")
        start_time = time.time()

        response = requests.post(
            f"{API_BASE_URL}/process_pptx",
            json=payload,
            timeout=120,  # 2 minutes timeout
            headers={'Content-Type': 'application/json'}
        )

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Response status: {response.status_code}")

        try:
            response_data = response.json()
            print(f"Response data:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"Raw response: {response.text}")

        if response.status_code == 200:
            print("[PASS] PPTX processing successful")
            return True
        else:
            print(f"[FAIL] PPTX processing failed: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("[FAIL] Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"[FAIL] Processing error: {str(e)}")
        return False

def test_invalid_url():
    """Test error handling with invalid URL"""
    print("Testing error handling with invalid URL...")

    payload = {
        "pptx_url": "https://invalid-url-that-does-not-exist.com/file.pptx"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/process_pptx",
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        response_data = response.json()

        if response.status_code == 400 and not response_data.get('success', True):
            print("✅ Error handling working correctly")
            print(f"📋 Error response: {response_data.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error test failed: {str(e)}")
        return False

def test_missing_payload():
    """Test error handling with missing payload"""
    print("Testing error handling with missing payload...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/process_pptx",
            json={},  # Empty payload
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 400:
            print("✅ Missing payload validation working")
            return True
        else:
            print(f"❌ Unexpected response for missing payload: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Missing payload test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Starting API Fix Validation Tests")
    print("=" * 50)

    tests = [
        ("Health Check", test_health_endpoint),
        ("PPTX Processing", test_process_pptx),
        ("Invalid URL Handling", test_invalid_url),
        ("Missing Payload Handling", test_missing_payload)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! API fixes are working correctly.")
        return True
    else:
        print("Some tests failed. Please check the server logs.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)