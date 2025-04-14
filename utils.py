import os
import logging
import re
import json
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def sanitize_string(s: Optional[str]) -> str:
    """
    Sanitizes a string by removing invalid characters and trimming whitespace.
    
    Args:
        s: String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if s is None:
        return ""
    
    # Replace common problematic characters
    s = s.replace('\u2013', '-')  # en dash
    s = s.replace('\u2014', '-')  # em dash
    s = s.replace('\u2018', "'")  # left single quote
    s = s.replace('\u2019', "'")  # right single quote
    s = s.replace('\u201c', '"')  # left double quote
    s = s.replace('\u201d', '"')  # right double quote
    
    # Remove control characters
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)
    
    return s.strip()

def parse_currency(value: str) -> Optional[str]:
    """
    Parses currency code from a string.
    
    Args:
        value: String containing currency information
        
    Returns:
        str: Currency code or None if not found
    """
    if not value:
        return None
    
    # Common currency codes
    currency_patterns = {
        'USD': r'USD|US\$|\$',
        'EUR': r'EUR|€',
        'GBP': r'GBP|£',
        'INR': r'INR|₹',
        'AED': r'AED|د.إ',
        'SGD': r'SGD|S\$',
        'CNY': r'CNY|¥|RMB',
        'JPY': r'JPY|¥|円',
        'AUD': r'AUD|A\$',
        'CAD': r'CAD|C\$',
        'HKD': r'HKD|HK\$',
    }
    
    for currency_code, pattern in currency_patterns.items():
        if re.search(pattern, value, re.IGNORECASE):
            return currency_code
    
    return None

def parse_number(value: Union[str, int, float, None]) -> Optional[float]:
    """
    Parses a numeric value from various input types.
    
    Args:
        value: Value to parse
        
    Returns:
        float: Parsed number or None if parsing fails
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove currency symbols and other non-numeric characters
        cleaned = re.sub(r'[^\d\.-]', '', value)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None

def format_date(date_obj: Optional[date]) -> Optional[str]:
    """
    Formats a date object to string.
    
    Args:
        date_obj: Date object to format
        
    Returns:
        str: Formatted date string or None if input is None
    """
    if date_obj is None:
        return None
    
    return date_obj.strftime('%Y-%m-%d')

def get_date_from_str(date_str: Optional[str]) -> Optional[date]:
    """
    Converts a date string to a date object.
    
    Args:
        date_str: Date string
        
    Returns:
        date: Date object or None if parsing fails
    """
    if not date_str:
        return None
    
    date_formats = [
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%b %d, %Y',
        '%d %b %Y',
        '%B %d, %Y',
        '%d %B %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def ensure_directory_exists(path: str) -> None:
    """
    Ensures that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)

def normalize_equipment_type(equipment_type: str) -> str:
    """
    Normalizes equipment type strings.
    
    Args:
        equipment_type: Equipment type string
        
    Returns:
        str: Normalized equipment type
    """
    if not equipment_type:
        return ""
    
    equipment_type = sanitize_string(equipment_type)
    
    # Common patterns and normalizations
    patterns = [
        (r'20[\'\"]?\s*D(?:RY)?', '20" Dry'),
        (r'40[\'\"]?\s*D(?:RY)?', '40" Dry'),
        (r'40[\'\"]?\s*H(?:C|igh Cube)', '40" High Cube'),
        (r'45[\'\"]?\s*H(?:C|igh Cube)?', '45" High Cube'),
        (r'20[\'\"]?\s*RF|20[\'\"]?\s*Reefer', '20" Reefer'),
        (r'40[\'\"]?\s*RF|40[\'\"]?\s*Reefer', '40" Reefer'),
        (r'Special Equipment', 'Special Equipment')
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, equipment_type, re.IGNORECASE):
            return replacement
    
    return equipment_type

def create_report(data: List[Dict[str, Any]], output_path: Optional[str] = None) -> str:
    """
    Creates a report from tariff data.
    
    Args:
        data: List of tariff data dictionaries
        output_path: Path to save the report
        
    Returns:
        str: Path to the saved report
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Add total count row
        summary = pd.DataFrame([{
            'Report Type': 'Total Tariffs',
            'Count': len(df),
            'Date Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
        # Set default output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(os.getcwd(), f'tariff_report_{timestamp}.xlsx')
        
        # Ensure directory exists
        Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary.to_excel(writer, sheet_name='Summary', index=False)
            df.to_excel(writer, sheet_name='Tariff Data', index=False)
            
            # Add additional sheets if needed
            if 'country' in df.columns:
                country_summary = df.groupby('country').size().reset_index(name='count')
                country_summary.to_excel(writer, sheet_name='By Country', index=False)
        
        logging.info(f"Report created successfully: {output_path}")
        return output_path
    
    except Exception as e:
        logging.error(f"Error creating report: {str(e)}")
        raise
