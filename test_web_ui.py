#!/usr/bin/env python3
"""
Web UI Testing Script - Simulates browser interactions
"""

import requests
import time
from datetime import datetime

def test_web_ui_components():
    """Test web UI components and endpoints"""
    print("🌐 Testing Web UI Components")
    print("=" * 50)
    
    base_url = "http://localhost:5173"
    api_url = "http://localhost:8000/api"
    
    # Test 1: Main page load
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Testing main page load...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            print(f"   Content length: {len(response.text)} characters")
        else:
            print(f"❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {e}")
    
    # Test 2: Static assets
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing static assets...")
    assets_to_test = [
        "/src/main.tsx",
        "/src/App.tsx", 
        "/src/styles.css"
    ]
    
    for asset in assets_to_test:
        try:
            response = requests.get(f"{base_url}{asset}", timeout=5)
            if response.status_code == 200:
                print(f"✅ Asset {asset} loads successfully")
            else:
                print(f"⚠️  Asset {asset} status: {response.status_code}")
        except Exception as e:
            print(f"❌ Asset {asset} error: {e}")
    
    # Test 3: API endpoints from frontend perspective
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing API endpoints...")
    
    # Health check
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health API: {data}")
        else:
            print(f"❌ Health API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health API error: {e}")
    
    # Document list
    try:
        response = requests.get(f"{api_url}/admin/docs", timeout=5)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Document API: {len(docs)} documents available")
        else:
            print(f"❌ Document API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Document API error: {e}")
    
    # Test 4: File upload simulation
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing file upload...")
    test_content = "This is a test file for UI testing."
    
    try:
        files = {"file": ("ui_test.txt", test_content, "text/plain")}
        response = requests.post(f"{api_url}/ingest/file", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get("document_id")
            print(f"✅ File upload successful: {doc_id}")
            
            # Check status
            status_response = requests.get(f"{api_url}/status/{doc_id}", timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Document status: {status_data.get('status')} ({status_data.get('chunks', 0)} chunks)")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
        else:
            print(f"❌ File upload failed: {response.status_code}")
    except Exception as e:
        print(f"❌ File upload error: {e}")
    
    # Test 5: Ask endpoint
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing ask endpoint...")
    try:
        payload = {"question": "Test question from UI"}
        response = requests.post(f"{api_url}/ask", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer_html", "")
            print(f"✅ Ask endpoint: {len(answer)} character response")
            print(f"   Preview: {answer[:100]}...")
        else:
            print(f"❌ Ask endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ask endpoint error: {e}")
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Web UI testing completed!")

if __name__ == "__main__":
    test_web_ui_components()
