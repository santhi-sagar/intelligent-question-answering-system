from typing import List, Tuple
import io
import PyPDF2
import pdfplumber
from docx import Document as DocxDocument
import pandas as pd
import openpyxl


def load_pdf(file_bytes: bytes) -> List[Tuple[int, str]]:
    """Extract text from PDF using pdfplumber for better text extraction."""
    pages = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append((page_num, text.strip()))
        
        # Fallback to PyPDF2 if pdfplumber fails
        if not pages:
            with io.BytesIO(file_bytes) as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append((page_num, text.strip()))
        
        return pages if pages else [(1, "No text content found in PDF")]
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return [(1, f"Error loading PDF: {str(e)}")]


def load_docx(file_bytes: bytes) -> List[Tuple[int, str]]:
    """Extract text from DOCX file."""
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        pages = []
        current_page = 1
        current_text = ""
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                current_text += text + "\n"
        
        if current_text.strip():
            pages.append((current_page, current_text.strip()))
        
        return pages if pages else [(1, "No text content found in DOCX")]
    except Exception as e:
        print(f"Error loading DOCX: {e}")
        return [(1, f"Error loading DOCX: {str(e)}")]


def load_text(file_bytes: bytes) -> List[Tuple[int, str]]:
    """Extract text from plain text file."""
    try:
        text = file_bytes.decode('utf-8', errors='ignore')
        return [(1, text.strip())] if text.strip() else [(1, "Empty text file")]
    except Exception as e:
        print(f"Error loading text file: {e}")
        return [(1, f"Error loading text file: {str(e)}")]


def load_csv_xlsx(file_bytes: bytes, is_xlsx: bool) -> List[Tuple[int, str]]:
    """Extract text from CSV or XLSX file."""
    try:
        if is_xlsx:
            # Load XLSX file
            df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        else:
            # Load CSV file
            df = pd.read_csv(io.BytesIO(file_bytes))
        
        pages = []
        current_page = 1
        current_text = ""
        
        # Convert DataFrame to text
        for index, row in df.iterrows():
            row_text = " | ".join([str(cell) for cell in row if pd.notna(cell)])
            if row_text.strip():
                current_text += row_text + "\n"
        
        if current_text.strip():
            pages.append((current_page, current_text.strip()))
        
        return pages if pages else [(1, "No data found in spreadsheet")]
    except Exception as e:
        print(f"Error loading spreadsheet: {e}")
        return [(1, f"Error loading spreadsheet: {str(e)}")]


