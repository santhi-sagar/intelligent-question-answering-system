#!/usr/bin/env python3
import requests

# Quick test
base_url = "http://localhost:8000/api"

# Upload small doc
content = "SRM University offers engineering programs. Contact: admissions@srmuniv.ac.in"
files = {"file": ("quick.txt", content, "text/plain")}
print("Uploading...")
upload = requests.post(f"{base_url}/ingest/file", files=files, timeout=10)
print(f"Upload: {upload.status_code} - {upload.json()}")

# Wait 2 seconds
import time
time.sleep(2)

# Check status
doc_id = upload.json()["document_id"]
status = requests.get(f"{base_url}/status/{doc_id}", timeout=5)
print(f"Status: {status.json()}")

# Ask question
ask = requests.post(f"{base_url}/ask", json={"question": "What is SRM University?"}, timeout=10)
print(f"Ask: {ask.json()}")
