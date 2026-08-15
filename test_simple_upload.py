#!/usr/bin/env python3
"""
Simple test to verify document processing pipeline
"""

import requests
import time
from datetime import datetime

def test_simple_upload():
    """Test a simple file upload and processing"""
    print("🧪 Testing Simple Document Upload and Processing")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Create a simple test document
    test_content = """
    SRM University is a leading private university in India.
    
    Founded in 1985, SRM University has grown to become one of India's premier educational institutions.
    
    The university offers programs in:
    - Engineering and Technology
    - Management
    - Medicine and Health Sciences
    - Science and Humanities
    - Law
    - Architecture
    
    SRM University has multiple campuses:
    - Chennai (Main Campus)
    - Delhi NCR
    - Amaravati
    - Sikkim
    
    The university is known for its world-class infrastructure, experienced faculty,
    industry partnerships, and global exposure programs.
    """
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Uploading test document...")
    
    try:
        files = {"file": ("srm_test.txt", test_content, "text/plain")}
        response = requests.post(f"{base_url}/ingest/file", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get("document_id")
            status = data.get("status")
            message = data.get("message", "")
            
            print(f"✅ Upload successful!")
            print(f"   Document ID: {doc_id}")
            print(f"   Status: {status}")
            print(f"   Message: {message}")
            
            # Wait a moment for processing
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Waiting for processing...")
            time.sleep(5)
            
            # Check status
            status_response = requests.get(f"{base_url}/status/{doc_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                final_status = status_data.get("status")
                chunks = status_data.get("chunk_count", 0)
                
                print(f"📊 Final Status: {final_status}")
                print(f"📊 Chunks: {chunks}")
                
                if final_status == "processed" and chunks > 0:
                    print("🎉 SUCCESS: Document was processed successfully!")
                    
                    # Test ask endpoint
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing ask endpoint...")
                    ask_payload = {"question": "What is SRM University?"}
                    ask_response = requests.post(f"{base_url}/ask", json=ask_payload, timeout=15)
                    
                    if ask_response.status_code == 200:
                        ask_data = ask_response.json()
                        answer = ask_data.get("answer_html", "")
                        sources = ask_data.get("sources", [])
                        
                        print(f"✅ Ask endpoint working!")
                        print(f"   Answer: {answer[:200]}...")
                        print(f"   Sources: {len(sources)}")
                        
                        if "I don't have enough information" not in answer:
                            print("🎉 SUCCESS: RAG pipeline is working!")
                        else:
                            print("⚠️  RAG pipeline returned placeholder response")
                    else:
                        print(f"❌ Ask endpoint failed: {ask_response.status_code}")
                else:
                    print("❌ Document was not processed properly")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_simple_upload()
