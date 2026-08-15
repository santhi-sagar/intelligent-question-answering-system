#!/usr/bin/env python3
"""
End-to-End UI Testing Script for SRM UniChat
Tests the complete workflow through the web interface
"""

import requests
import time
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WEB_URL = "http://localhost:5173"
API_BASE = f"{BASE_URL}/api"

def log_step(step, message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {status}: {step} - {message}")

def test_api_health():
    """Test 1: API Health Check"""
    log_step("TEST-1", "Testing API Health Check")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_step("TEST-1", f"✅ API Health: {data}", "SUCCESS")
            return True
        else:
            log_step("TEST-1", f"❌ API Health failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_step("TEST-1", f"❌ API Health error: {str(e)}", "ERROR")
        return False

def test_web_interface():
    """Test 2: Web Interface Accessibility"""
    log_step("TEST-2", "Testing Web Interface Accessibility")
    try:
        response = requests.get(WEB_URL, timeout=10)
        if response.status_code == 200:
            log_step("TEST-2", f"✅ Web Interface accessible: {response.status_code}", "SUCCESS")
            return True
        else:
            log_step("TEST-2", f"❌ Web Interface failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_step("TEST-2", f"❌ Web Interface error: {str(e)}", "ERROR")
        return False

def test_document_list():
    """Test 3: Document List Endpoint"""
    log_step("TEST-3", "Testing Document List Endpoint")
    try:
        response = requests.get(f"{API_BASE}/admin/docs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_step("TEST-3", f"✅ Document List: {len(data)} documents found", "SUCCESS")
            for doc in data:
                log_step("TEST-3", f"  📄 Document: {doc.get('title', 'Unknown')} (ID: {doc.get('id', 'Unknown')})", "INFO")
            return True
        else:
            log_step("TEST-3", f"❌ Document List failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_step("TEST-3", f"❌ Document List error: {str(e)}", "ERROR")
        return False

def test_file_upload():
    """Test 4: File Upload Functionality"""
    log_step("TEST-4", "Testing File Upload Functionality")
    
    # Create a test document
    test_content = """
    This is a test document for SRM UniChat.
    
    SRM University is a leading private university in India.
    It offers various programs in engineering, management, medicine, and other fields.
    
    The university has multiple campuses across India including:
    - Chennai (Main Campus)
    - Delhi NCR
    - Amaravati
    - Sikkim
    
    Key features:
    - World-class infrastructure
    - Experienced faculty
    - Industry partnerships
    - Research opportunities
    - Global exposure programs
    """
    
    test_file_path = "test_ui_document.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "text/plain")}
            response = requests.post(f"{API_BASE}/ingest/file", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            document_id = data.get("document_id")
            log_step("TEST-4", f"✅ File Upload successful: Document ID = {document_id}", "SUCCESS")
            log_step("TEST-4", f"  📄 Title: {data.get('title', 'Unknown')}", "INFO")
            log_step("TEST-4", f"  📊 Status: {data.get('status', 'Unknown')}", "INFO")
            return document_id
        else:
            log_step("TEST-4", f"❌ File Upload failed: {response.status_code} - {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("TEST-4", f"❌ File Upload error: {str(e)}", "ERROR")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_document_status(document_id):
    """Test 5: Document Status Checking"""
    if not document_id:
        log_step("TEST-5", "❌ Skipping Document Status - No document ID", "ERROR")
        return False
    
    log_step("TEST-5", f"Testing Document Status for ID: {document_id}")
    try:
        response = requests.get(f"{API_BASE}/status/{document_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            chunks = data.get("chunks", 0)
            log_step("TEST-5", f"✅ Document Status: {status} (Chunks: {chunks})", "SUCCESS")
            
            if status == "queued":
                log_step("TEST-5", "  ⏳ Document is queued for processing", "INFO")
            elif status == "processed":
                log_step("TEST-5", "  ✅ Document has been processed", "SUCCESS")
            else:
                log_step("TEST-5", f"  ❓ Unknown status: {status}", "WARNING")
            
            return True
        else:
            log_step("TEST-5", f"❌ Document Status failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_step("TEST-5", f"❌ Document Status error: {str(e)}", "ERROR")
        return False

def test_ask_endpoint():
    """Test 6: Ask Endpoint Functionality"""
    log_step("TEST-6", "Testing Ask Endpoint Functionality")
    
    test_questions = [
        "What is SRM University?",
        "Tell me about the campuses",
        "What programs are offered?",
        "How can I apply?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        log_step("TEST-6", f"  Question {i}: {question}")
        try:
            payload = {"question": question}
            response = requests.post(f"{API_BASE}/ask", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer_html", "No answer")
                sources = data.get("sources", [])
                
                log_step("TEST-6", f"    ✅ Answer received: {len(answer)} characters", "SUCCESS")
                log_step("TEST-6", f"    📚 Sources: {len(sources)} found", "INFO")
                
                # Log first 100 characters of answer
                answer_preview = answer.replace('<p>', '').replace('</p>', '')[:100]
                log_step("TEST-6", f"    💬 Answer preview: {answer_preview}...", "INFO")
                
            else:
                log_step("TEST-6", f"    ❌ Question {i} failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            log_step("TEST-6", f"    ❌ Question {i} error: {str(e)}", "ERROR")
    
    return True

def test_database_entries():
    """Test 7: Database Entries Verification"""
    log_step("TEST-7", "Testing Database Entries")
    try:
        # Get all documents
        response = requests.get(f"{API_BASE}/admin/docs", timeout=10)
        if response.status_code == 200:
            documents = response.json()
            log_step("TEST-7", f"✅ Database contains {len(documents)} documents", "SUCCESS")
            
            for doc in documents:
                doc_id = doc.get("id")
                title = doc.get("title", "Unknown")
                created_at = doc.get("created_at", "Unknown")
                
                log_step("TEST-7", f"  📄 Document: {title}", "INFO")
                log_step("TEST-7", f"    ID: {doc_id}", "INFO")
                log_step("TEST-7", f"    Created: {created_at}", "INFO")
                
                # Check status for each document
                status_response = requests.get(f"{API_BASE}/status/{doc_id}", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status", "unknown")
                    chunks = status_data.get("chunks", 0)
                    log_step("TEST-7", f"    Status: {status} (Chunks: {chunks})", "INFO")
                else:
                    log_step("TEST-7", f"    Status: Failed to check", "WARNING")
            
            return True
        else:
            log_step("TEST-7", f"❌ Database query failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_step("TEST-7", f"❌ Database query error: {str(e)}", "ERROR")
        return False

def main():
    """Main test execution"""
    print("=" * 80)
    print("🚀 SRM UniChat End-to-End UI Testing")
    print("=" * 80)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {}
    
    # Run all tests
    test_results["API Health"] = test_api_health()
    test_results["Web Interface"] = test_web_interface()
    test_results["Document List"] = test_document_list()
    
    # File upload test
    document_id = test_file_upload()
    test_results["File Upload"] = document_id is not None
    
    # Document status test
    test_results["Document Status"] = test_document_status(document_id)
    
    # Ask endpoint test
    test_results["Ask Endpoint"] = test_ask_endpoint()
    
    # Database verification
    test_results["Database Entries"] = test_database_entries()
    
    # Summary
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs above for details.")
    
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
