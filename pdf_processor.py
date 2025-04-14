import os
import logging
import PyPDF2
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import io
import numpy as np
import re
from PIL import Image
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def is_scanned_pdf(pdf_path):
    """
    Determines if a PDF is a scanned document or contains extractable text.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        bool: True if the PDF is scanned, False if it contains extractable text
    """
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check first 5 pages or all pages if less than 5
            pages_to_check = min(5, len(pdf_reader.pages))
            
            for i in range(pages_to_check):
                page = pdf_reader.pages[i]
                text = page.extract_text()
                
                # If we can extract a significant amount of text, it's probably not scanned
                if text and len(text.strip()) > 100:
                    return False
        
        # If we couldn't extract sufficient text from any page, consider it scanned
        return True
    
    except Exception as e:
        logging.error(f"Error checking if PDF is scanned: {str(e)}")
        # If there's an error, assume it's scanned to use OCR
        return True

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using PyPDF2.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        return text
    
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_with_pdfplumber(pdf_path):
    """
    Extracts text from a PDF using pdfplumber.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        return text
    
    except Exception as e:
        logging.error(f"Error extracting text with pdfplumber: {str(e)}")
        return ""

def extract_text_with_ocr(pdf_path):
    """
    Extracts text from a PDF using OCR (Optical Character Recognition).
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        for i, image in enumerate(images):
            # Perform OCR on the image
            page_text = pytesseract.image_to_string(image, lang='eng')
            if page_text:
                text += page_text + "\n\n"
        
        return text
    
    except Exception as e:
        logging.error(f"Error extracting text with OCR: {str(e)}")
        return ""

def extract_tables_with_pdfplumber(pdf_path):
    """
    Extracts tables from a PDF using pdfplumber.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        list: List of extracted tables
    """
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                if page_tables:
                    for table in page_tables:
                        # Only add non-empty tables
                        if table and any(any(cell for cell in row) for row in table):
                            tables.append(table)
        
        return tables
    
    except Exception as e:
        logging.error(f"Error extracting tables with pdfplumber: {str(e)}")
        return []

def extract_metadata(pdf_path):
    """
    Extracts metadata from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing PDF metadata
    """
    metadata = {}
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
            
            # Add number of pages
            metadata['/PageCount'] = len(pdf_reader.pages)
        
        return metadata
    
    except Exception as e:
        logging.error(f"Error extracting metadata: {str(e)}")
        return {}

def process_pdf(pdf_path):
    """
    Processes a PDF file to extract text, tables, and metadata.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing extracted information
    """
    result = {
        'text': '',
        'tables': [],
        'metadata': {},
        'is_scanned': False,
        'processing_method': '',
        'file_path': pdf_path,
        'file_name': os.path.basename(pdf_path),
    }
    
    try:
        # Extract metadata
        result['metadata'] = extract_metadata(pdf_path)
        
        # Check if PDF is scanned
        result['is_scanned'] = is_scanned_pdf(pdf_path)
        
        # Extract text based on whether PDF is scanned or not
        if result['is_scanned']:
            result['processing_method'] = 'OCR'
            result['text'] = extract_text_with_ocr(pdf_path)
        else:
            # Try pdfplumber first, fall back to PyPDF2 if it fails
            pdfplumber_text = extract_text_with_pdfplumber(pdf_path)
            
            if pdfplumber_text and len(pdfplumber_text.strip()) > 100:
                result['processing_method'] = 'pdfplumber'
                result['text'] = pdfplumber_text
            else:
                result['processing_method'] = 'PyPDF2'
                result['text'] = extract_text_from_pdf(pdf_path)
        
        # Extract tables
        result['tables'] = extract_tables_with_pdfplumber(pdf_path)
        
        # Extract creation date
        try:
            if '/CreationDate' in result['metadata']:
                creation_date_str = result['metadata']['/CreationDate']
                # Remove 'D:' prefix and handle timezone
                if creation_date_str.startswith('D:'):
                    date_str = creation_date_str[2:14]  # Get YYYYMMDDHHMMSS
                    result['creation_date'] = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                else:
                    result['creation_date'] = None
            else:
                result['creation_date'] = None
        except Exception as e:
            logging.warning(f"Error parsing creation date: {str(e)}")
            result['creation_date'] = None
            
        # Try to extract validity period from text
        validity_pattern = r'(?:valid|effective)(?:\s+from\s+|\s+)(\d{1,2}[^\d]{1,2}\w+[^\d]{1,2}\d{4})(?:\s+(?:to|until|through)\s+)(\d{1,2}[^\d]{1,2}\w+[^\d]{1,2}\d{4})'
        validity_matches = re.findall(validity_pattern, result['text'], re.IGNORECASE)
        
        if validity_matches:
            result['valid_from_text'] = validity_matches[0][0]
            result['valid_to_text'] = validity_matches[0][1]
        else:
            result['valid_from_text'] = None
            result['valid_to_text'] = None
        
        logging.info(f"Successfully processed PDF: {pdf_path}")
        return result
    
    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        return result
