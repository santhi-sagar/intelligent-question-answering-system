# Document Status Verification Guide

## Overview
This guide explains how to verify whether document embeddings have been created after uploading a file to SRM UniChat.

## How It Works

### 1. File Upload Process
When you upload a file:
1. File is uploaded to `/api/ingest/file` endpoint
2. Returns `{"status": "queued", "document_id": "uuid"}` 
3. Document is stored in database with "queued" status
4. Background processing creates chunks and embeddings
5. Status changes to "processed" when complete

### 2. Status Checking
The system provides real-time status checking:
- **API Endpoint**: `GET /api/ingest/status/{document_id}`
- **Frontend**: Automatic polling every 2 seconds
- **Manual Check**: Refresh button in the UI

## Verification Methods

### Method 1: Using the Web Interface
1. Upload a file through the web interface
2. The interface will automatically show:
   - Upload progress
   - Processing status (Queued/Processed)
   - Number of chunks created
   - Real-time updates

### Method 2: Using the API Directly
```bash
# Check status of your document
curl -X GET "http://localhost:8000/api/ingest/status/76394822-f9bf-4ac2-ab31-d0b14cb0af8a"
```

Response:
```json
{
  "document_id": "76394822-f9bf-4ac2-ab31-d0b14cb0af8a",
  "title": "19. Library Policy of SRM University - AP (1).pdf",
  "status": "processed",
  "chunk_count": 15,
  "message": "Document processed successfully with 15 chunks",
  "created_at": "2024-01-10T02:58:54.123456"
}
```

### Method 3: Using the Test Script
```bash
# Run the test script
python test_document_status.py
```

## Status Meanings

| Status | Description | Chunk Count | Meaning |
|--------|-------------|-------------|---------|
| `queued` | Document uploaded but not processed | 0 | Waiting for processing |
| `processed` | Document fully processed | >0 | Embeddings created and ready |

## What Happens During Processing

1. **File Upload**: Document stored in database
2. **Text Extraction**: Content extracted from PDF/DOCX
3. **Chunking**: Text split into manageable chunks
4. **Embedding Creation**: Each chunk converted to vector embeddings
5. **Storage**: Embeddings stored in pgvector database
6. **Status Update**: Status changed to "processed"

## Troubleshooting

### Document Stuck in "Queued" Status
- Check if the backend processing pipeline is running
- Verify database connection
- Check server logs for errors

### No Chunks Created
- Ensure the file format is supported
- Check if the file is corrupted
- Verify text extraction is working

### API Errors
- Ensure backend server is running on port 8000
- Check CORS settings
- Verify database is accessible

## API Endpoints

### Check Document Status
```
GET /api/ingest/status/{document_id}
```

**Response:**
```json
{
  "document_id": "string",
  "title": "string", 
  "status": "queued" | "processed",
  "chunk_count": number,
  "message": "string",
  "created_at": "ISO datetime string"
}
```

### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "db": true,
  "embeddings_ready": true
}
```

## Frontend Features

The web interface provides:
- **Real-time Status Updates**: Automatic polling every 2 seconds
- **Visual Progress Indicators**: Upload progress and processing status
- **Manual Refresh**: Button to check status immediately
- **Detailed Information**: Document title, chunk count, timestamps
- **Error Handling**: Clear error messages and retry options

## Next Steps

Once a document shows "processed" status:
1. The document is ready for search and Q&A
2. You can ask questions about the uploaded content
3. The AI will use the embeddings to find relevant information
4. Citations will reference the specific chunks from your document

## Example Workflow

1. **Upload**: Upload "Library Policy.pdf"
2. **Monitor**: Watch status change from "queued" to "processed"
3. **Verify**: See "15 chunks created" message
4. **Query**: Ask "What is the library policy for late returns?"
5. **Get Answer**: AI responds with relevant information from your document
