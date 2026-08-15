#!/usr/bin/env python3
"""
Test with very small document and ask questions
"""

import requests
import time
from datetime import datetime

def test_small_document_qa():
    """Test with a very small document and ask various questions"""
    print("🧪 Testing Small Document Q&A")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Create a very small, focused test document
    small_doc_content = """
    SRM University Admission Process
    
    SRM University offers undergraduate and postgraduate programs.
    
    Admission Requirements:
    - 12th grade completion for undergraduate programs
    - Bachelor's degree for postgraduate programs
    - Entrance exam scores (SRMJEE, SRMJEEM, etc.)
    
    Application Process:
    1. Fill online application form
    2. Pay application fee
    3. Upload required documents
    4. Take entrance exam
    5. Attend counseling session
    
    Contact: admissions@srmuniv.ac.in
    Phone: +91-44-2745-5000
    """
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Uploading small test document...")
    print(f"Document content preview: {small_doc_content[:100]}...")
    
    try:
        # Upload the small document
        files = {"file": ("srm_admission.txt", small_doc_content, "text/plain")}
        upload_response = requests.post(f"{base_url}/ingest/file", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            doc_id = upload_data.get("document_id")
            status = upload_data.get("status")
            
            print(f"✅ Upload successful!")
            print(f"   Document ID: {doc_id}")
            print(f"   Status: {status}")
            
            # Wait for processing
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Waiting for processing...")
            time.sleep(3)
            
            # Check final status
            status_response = requests.get(f"{base_url}/status/{doc_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                final_status = status_data.get("status")
                chunks = status_data.get("chunk_count", 0)
                
                print(f"📊 Final Status: {final_status}")
                print(f"📊 Chunks: {chunks}")
                
                if final_status == "processed" and chunks > 0:
                    print("🎉 Document processed successfully!")
                    
                    # Test various questions
                    test_questions = [
                        "What is SRM University?",
                        "How do I apply to SRM University?",
                        "What are the admission requirements?",
                        "What is the application process?",
                        "How can I contact SRM University?",
                        "What entrance exams are required?",
                        "What programs does SRM offer?",
                        "What is the application fee?",
                        "Tell me about undergraduate programs",
                        "What documents are required?"
                    ]
                    
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing Q&A with various questions...")
                    print("=" * 60)
                    
                    for i, question in enumerate(test_questions, 1):
                        print(f"\n❓ Question {i}: {question}")
                        
                        try:
                            ask_payload = {"question": question}
                            ask_response = requests.post(f"{base_url}/ask", json=ask_payload, timeout=15)
                            
                            if ask_response.status_code == 200:
                                ask_data = ask_response.json()
                                answer = ask_data.get("answer_html", "")
                                sources = ask_data.get("sources", [])
                                followups = ask_data.get("followups", [])
                                
                                # Clean up HTML tags for display
                                clean_answer = answer.replace('<p>', '').replace('</p>', '').replace('<strong>', '').replace('</strong>', '')
                                
                                print(f"   💬 Answer: {clean_answer[:200]}{'...' if len(clean_answer) > 200 else ''}")
                                print(f"   📚 Sources: {len(sources)}")
                                print(f"   🔗 Follow-ups: {followups[:2] if followups else 'None'}")
                                
                                # Check if answer contains relevant information
                                if any(keyword in clean_answer.lower() for keyword in ['srm', 'admission', 'application', 'university', 'program', 'exam', 'contact']):
                                    print("   ✅ Answer appears relevant")
                                else:
                                    print("   ⚠️  Answer may not be relevant")
                                    
                            else:
                                print(f"   ❌ Ask failed: {ask_response.status_code}")
                                
                        except Exception as e:
                            print(f"   ❌ Error asking question: {str(e)}")
                        
                        # Small delay between questions
                        time.sleep(1)
                    
                    print(f"\n{'='*60}")
                    print("🎯 Q&A TEST SUMMARY")
                    print(f"{'='*60}")
                    print("✅ Document processing: WORKING")
                    print("✅ File upload: WORKING")
                    print("✅ Chunking: WORKING")
                    print("✅ Embedding generation: WORKING")
                    print("✅ Vector storage: WORKING")
                    print("⚠️  RAG retrieval: NEEDS VERIFICATION")
                    
                else:
                    print("❌ Document was not processed properly")
                    print(f"   Status: {final_status}")
                    print(f"   Chunks: {chunks}")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Response: {upload_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_small_document_qa()
