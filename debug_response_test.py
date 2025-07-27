#!/usr/bin/env python3
"""
Debug Response Content Test
Investigates the JSON parsing issue
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
FRONTEND_DOMAIN = "https://kodix.netlify.app"

def debug_response_content():
    """Debug the response content to understand JSON parsing issue"""
    print("🔍 Debugging Response Content...")
    
    headers = {
        'Origin': FRONTEND_DOMAIN,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    test_data = {
        "provider": "openai",
        "api_key": "sk-proj-DebugTest123456789abcdef",
        "display_name": "Debug Test Key"
    }
    
    session = requests.Session()
    
    try:
        print("Making POST request...")
        response = session.post(f"{API_BASE}/api-keys", json=test_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding')}")
        
        print(f"\nRaw Response Content (first 500 chars):")
        print(repr(response.content[:500]))
        
        print(f"\nResponse Text (first 500 chars):")
        print(repr(response.text[:500]))
        
        # Try to decode JSON manually
        try:
            data = response.json()
            print(f"\nJSON Decoded Successfully:")
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError as e:
            print(f"\nJSON Decode Error: {e}")
            print(f"Error at position: {e.pos}")
            if len(response.text) > e.pos:
                print(f"Character at error position: {repr(response.text[e.pos])}")
        
        # Check if response is compressed
        if response.headers.get('Content-Encoding') == 'br':
            print("\n⚠️  Response is Brotli compressed!")
            try:
                import brotli
                decompressed = brotli.decompress(response.content)
                print(f"Decompressed content: {decompressed.decode('utf-8')}")
            except ImportError:
                print("Brotli library not available for manual decompression")
            except Exception as e:
                print(f"Error decompressing: {e}")
        
        # Test with different Accept-Encoding
        print("\n🔄 Testing without compression...")
        headers_no_compression = headers.copy()
        headers_no_compression['Accept-Encoding'] = 'identity'
        
        response2 = session.post(f"{API_BASE}/api-keys", json=test_data, headers=headers_no_compression)
        print(f"Status Code: {response2.status_code}")
        print(f"Content-Encoding: {response2.headers.get('Content-Encoding')}")
        print(f"Response Text: {response2.text}")
        
        try:
            data2 = response2.json()
            print(f"JSON Decoded Successfully (no compression):")
            print(json.dumps(data2, indent=2))
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error (no compression): {e}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

def test_get_request():
    """Test GET request to see if it has the same issue"""
    print("\n🔍 Testing GET Request...")
    
    headers = {
        'Origin': FRONTEND_DOMAIN,
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    
    try:
        response = session.get(f"{API_BASE}/api-keys", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding')}")
        
        print(f"\nResponse Text (first 200 chars):")
        print(response.text[:200])
        
        try:
            data = response.json()
            print(f"\n✅ JSON Decoded Successfully:")
            print(f"Found {len(data)} API keys")
            for key in data:
                print(f"  - {key['provider']}: {key['display_name']}")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Decode Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

def main():
    print("🧪 Debug Response Content Test")
    print(f"Backend API: {API_BASE}")
    print("=" * 60)
    
    debug_response_content()
    test_get_request()

if __name__ == "__main__":
    main()