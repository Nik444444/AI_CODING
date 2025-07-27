#!/usr/bin/env python3
"""
Database Persistence Test for API Key Management
Tests database persistence and data integrity
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_database_persistence():
    """Test database persistence by creating, reading, updating, and deleting API keys"""
    print("💾 Testing Database Persistence for API Keys...")
    
    session = requests.Session()
    test_results = []
    
    # Step 1: Get initial state
    print("\n1️⃣ Getting initial API keys...")
    try:
        response = session.get(f"{API_BASE}/api-keys")
        if response.status_code == 200:
            initial_keys = response.json()
            print(f"✅ Initial state: {len(initial_keys)} API keys found")
            for key in initial_keys:
                print(f"   - {key['provider']}: {key['display_name']} (Active: {key['is_active']})")
        else:
            print(f"❌ Failed to get initial state: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting initial state: {str(e)}")
        return False
    
    # Step 2: Create a new API key
    print("\n2️⃣ Creating new API key...")
    test_key_data = {
        "provider": "openai",
        "api_key": "sk-proj-PersistenceTest123456789abcdef",
        "display_name": "Database Persistence Test Key"
    }
    
    try:
        response = session.post(f"{API_BASE}/api-keys", json=test_key_data)
        if response.status_code == 200:
            created_key = response.json()
            key_id = created_key['id']
            print(f"✅ Created API key with ID: {key_id}")
            print(f"   Provider: {created_key['provider']}")
            print(f"   Display Name: {created_key['display_name']}")
            print(f"   Masked Key: {created_key['api_key']}")
        elif response.status_code == 400:
            error_data = response.json()
            if "already exists" in error_data.get('detail', ''):
                print("⚠️  OpenAI key already exists, trying to update instead...")
                # Get existing key ID
                existing_keys = session.get(f"{API_BASE}/api-keys").json()
                openai_key = next((k for k in existing_keys if k['provider'] == 'openai'), None)
                if openai_key:
                    key_id = openai_key['id']
                    print(f"✅ Using existing OpenAI key ID: {key_id}")
                else:
                    print("❌ Could not find existing OpenAI key")
                    return False
            else:
                print(f"❌ Failed to create API key: {error_data}")
                return False
        else:
            print(f"❌ Failed to create API key: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating API key: {str(e)}")
        return False
    
    # Step 3: Verify persistence by reading the key
    print("\n3️⃣ Verifying key persistence...")
    try:
        response = session.get(f"{API_BASE}/api-keys/{key_id}")
        if response.status_code == 200:
            retrieved_key = response.json()
            print(f"✅ Key retrieved successfully:")
            print(f"   ID: {retrieved_key['id']}")
            print(f"   Provider: {retrieved_key['provider']}")
            print(f"   Display Name: {retrieved_key['display_name']}")
            print(f"   Active: {retrieved_key['is_active']}")
            print(f"   Created: {retrieved_key['created_at']}")
        else:
            print(f"❌ Failed to retrieve key: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving key: {str(e)}")
        return False
    
    # Step 4: Update the key
    print("\n4️⃣ Testing key update...")
    update_data = {
        "display_name": "Updated Persistence Test Key",
        "is_active": False
    }
    
    try:
        response = session.put(f"{API_BASE}/api-keys/{key_id}", json=update_data)
        if response.status_code == 200:
            updated_key = response.json()
            print(f"✅ Key updated successfully:")
            print(f"   Display Name: {updated_key['display_name']}")
            print(f"   Active: {updated_key['is_active']}")
            print(f"   Updated: {updated_key['updated_at']}")
        else:
            print(f"❌ Failed to update key: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error updating key: {str(e)}")
        return False
    
    # Step 5: Verify update persistence
    print("\n5️⃣ Verifying update persistence...")
    try:
        response = session.get(f"{API_BASE}/api-keys/{key_id}")
        if response.status_code == 200:
            retrieved_key = response.json()
            if (retrieved_key['display_name'] == update_data['display_name'] and
                retrieved_key['is_active'] == update_data['is_active']):
                print("✅ Update persisted correctly in database")
            else:
                print("❌ Update not persisted correctly")
                return False
        else:
            print(f"❌ Failed to verify update: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verifying update: {str(e)}")
        return False
    
    # Step 6: Test data integrity across multiple requests
    print("\n6️⃣ Testing data integrity across multiple requests...")
    try:
        # Make multiple requests to ensure consistency
        for i in range(3):
            response = session.get(f"{API_BASE}/api-keys")
            if response.status_code == 200:
                keys = response.json()
                our_key = next((k for k in keys if k['id'] == key_id), None)
                if our_key:
                    if our_key['display_name'] != update_data['display_name']:
                        print(f"❌ Data inconsistency detected on request {i+1}")
                        return False
                else:
                    print(f"❌ Key not found on request {i+1}")
                    return False
            else:
                print(f"❌ Request {i+1} failed: {response.status_code}")
                return False
            time.sleep(0.1)  # Small delay between requests
        
        print("✅ Data integrity maintained across multiple requests")
    except Exception as e:
        print(f"❌ Error testing data integrity: {str(e)}")
        return False
    
    # Step 7: Clean up (optional - delete the test key)
    print("\n7️⃣ Cleaning up test data...")
    try:
        response = session.delete(f"{API_BASE}/api-keys/{key_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test key deleted: {result['message']}")
            
            # Verify deletion
            verify_response = session.get(f"{API_BASE}/api-keys/{key_id}")
            if verify_response.status_code == 404:
                print("✅ Deletion verified - key no longer exists")
            else:
                print("⚠️  Key still exists after deletion")
        else:
            print(f"⚠️  Failed to delete test key: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error during cleanup: {str(e)}")
    
    return True

def test_concurrent_access():
    """Test concurrent access to API keys"""
    print("\n🔄 Testing Concurrent Access...")
    
    import threading
    import time
    
    results = []
    
    def make_request(thread_id):
        try:
            session = requests.Session()
            response = session.get(f"{API_BASE}/api-keys")
            if response.status_code == 200:
                keys = response.json()
                results.append(f"Thread {thread_id}: {len(keys)} keys")
                return True
            else:
                results.append(f"Thread {thread_id}: Error {response.status_code}")
                return False
        except Exception as e:
            results.append(f"Thread {thread_id}: Exception {str(e)}")
            return False
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i+1,))
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("Concurrent access results:")
    for result in results:
        print(f"  {result}")
    
    # Check if all requests succeeded
    success_count = sum(1 for r in results if "keys" in r)
    if success_count == 5:
        print("✅ All concurrent requests succeeded")
        return True
    else:
        print(f"❌ Only {success_count}/5 concurrent requests succeeded")
        return False

def main():
    print("🧪 Database Persistence Test for API Key Management")
    print(f"Backend API: {API_BASE}")
    print("=" * 60)
    
    tests = [
        test_database_persistence,
        test_concurrent_access
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("📊 DATABASE PERSISTENCE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL DATABASE TESTS PASSED! Database persistence is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} database tests failed. Check database configuration.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)