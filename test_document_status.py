#!/usr/bin/env python3
"""
Test script to verify document status endpoint
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_document_status():
    # Test with the document ID from your upload
    document_id = "76394822-f9bf-4ac2-ab31-d0b14cb0af8a"
    
    print(f"Testing document status for ID: {document_id}")
    print("=" * 50)
    
    try:
        # Check document status
        response = requests.get(f"{API_BASE}/api/ingest/status/{document_id}")
        
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Document status retrieved successfully!")
            print(f"Document Title: {status_data['title']}")
            print(f"Status: {status_data['status']}")
            print(f"Chunk Count: {status_data['chunk_count']}")
            print(f"Message: {status_data['message']}")
            print(f"Created At: {status_data['created_at']}")
            
            if status_data['status'] == 'processed':
                print("\n🎉 Document has been processed and embeddings are ready!")
            else:
                print("\n⏳ Document is still being processed...")
                
        elif response.status_code == 404:
            print("❌ Document not found. Make sure the document ID is correct.")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test the health endpoint"""
    print("\nTesting API health...")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API is healthy!")
            print(f"Database: {health_data['db']}")
            print(f"Embeddings Ready: {health_data['embeddings_ready']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    test_health()
    test_document_status()
    
    print("\n" + "=" * 50)
    print("To test with a new document:")
    print("1. Upload a file using the web interface")
    print("2. Copy the document_id from the response")
    print("3. Update the document_id variable in this script")
    print("4. Run the script again")
