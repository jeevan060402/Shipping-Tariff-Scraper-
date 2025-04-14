import os
import logging
import json
import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from openai import OpenAI
from config import Config

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI client
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
def extract_tariff_data(pdf_content: Dict[str, Any], country) -> List[Dict[str, Any]]:
    """
    Extracts structured tariff data from PDF content using OpenAI.
    
    Args:
        pdf_content: Dictionary containing processed PDF content
        country: Country object for context
        
    Returns:
        list: List of dictionaries containing structured tariff data
    """
    logging.info(f"Extracting tariff data for {country.name}")
    
    try:
        # Extract text and tables from PDF content
        text = pdf_content.get('text', '')
        tables = pdf_content.get('tables', [])
        
        # Format tables for prompt
        formatted_tables = []
        for i, table in enumerate(tables):
            formatted_table = f"Table {i+1}:\n"
            for row in table:
                formatted_table += " | ".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
            formatted_tables.append(formatted_table)
        
        tables_text = "\n\n".join(formatted_tables)
        
        # Create metadata section for prompt
        metadata = pdf_content.get('metadata', {})
        creation_date = pdf_content.get('creation_date')
        valid_from = pdf_content.get('valid_from_text')
        valid_to = pdf_content.get('valid_to_text')
        
        metadata_text = "Metadata:\n"
        if creation_date:
            metadata_text += f"Creation Date: {creation_date.strftime('%Y-%m-%d')}\n"
        if valid_from:
            metadata_text += f"Valid From: {valid_from}\n"
        if valid_to:
            metadata_text += f"Valid To: {valid_to}\n"
        
        # Construct prompt for OpenAI
        prompt = f"""
You are an expert in extracting shipping tariff information from documents. I'll provide you with content from a PDF document about detention and demurrage tariffs for {country.name}.

Please extract the following information in a structured JSON format:
1. Liner Name (usually Hapag-Lloyd)
2. Ports mentioned in the document
3. Equipment Types (like 20" Dry, 40" Dry, etc.)
4. Currency used for rates
5. Free days allowed before charges apply
6. Tariff rates for different time periods (buckets)

For each port and equipment type combination, provide:
- Port name
- Equipment type
- Currency
- Free days
- Validity period (if mentioned)
- Rate buckets with:
  - Bucket number (1, 2, 3)
  - Start day
  - End day
  - Rate amount

Document Text:
{text[:4000]}  # Truncate to avoid exceeding token limits

{tables_text[:3000] if tables_text else "No tables found."}

{metadata_text}

Country: {country.name}
Region: {country.region.name}

Output the data as a JSON array with each object having this structure:
{{
  "liner_name": "string",
  "port": "string",
  "equipment_type": "string",
  "currency": "string",
  "free_days": number,
  "valid_from": "YYYY-MM-DD",
  "valid_to": "YYYY-MM-DD",
  "buckets": [
    {{
      "bucket_number": number,
      "start_day": number,
      "end_day": number,
      "rate": number
    }}
  ]
}}

If you can't determine a value with certainty, use null. Be precise and extract as many port and equipment type combinations as you can find.
"""

        # Call OpenAI API with the prompt
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a specialized shipping tariff extraction assistant that converts PDF content into structured data."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Extract response
        result_text = response.choices[0].message.content
        
        # Parse JSON
        try:
            # Extract JSON data from response if it's wrapped in markdown
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result_text)
            if json_match:
                # Extract JSON content from markdown code block
                json_str = json_match.group(1)
            else:
                # If not in markdown format, use the raw response
                json_str = result_text
            
            # Parse the JSON
            result_data = json.loads(json_str)
            
            # If the result is wrapped in an extra layer, unwrap it
            if isinstance(result_data, dict) and "tariffs" in result_data:
                tariffs = result_data["tariffs"]
            elif isinstance(result_data, dict) and "data" in result_data:
                tariffs = result_data["data"]
            else:
                tariffs = result_data
                
            # Ensure result is a list
            if not isinstance(tariffs, list):
                tariffs = [tariffs]
            
            logging.info(f"Successfully extracted {len(tariffs)} tariff entries for {country.name}")
            return tariffs
            
        except Exception as e:
            logging.error(f"Error parsing JSON from OpenAI response: {str(e)}")
            logging.debug(f"Response text: {result_text}")
            return []
    
    except Exception as e:
        logging.error(f"Error extracting tariff data: {str(e)}")
        return []

def parse_date(date_str: Optional[str]) -> Optional[date]:
    """
    Parses date string to date object.
    
    Args:
        date_str: Date string
        
    Returns:
        date: Parsed date object or None if parsing fails
    """
    if not date_str or date_str == "null" or date_str.lower() == "none":
        return None
    
    date_formats = [
        "%Y-%m-%d",
        "%d %B %Y",
        "%d-%m-%Y",
        "%B %d, %Y",
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # If none of the formats match, try to extract date using regex
    try:
        date_match = re.search(r'(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})', date_str)
        if date_match:
            day, month, year = map(int, date_match.groups())
            if year < 100:
                year += 2000 if year < 50 else 1900
            return date(year, month, day)
    except Exception:
        pass
    
    logging.warning(f"Could not parse date: {date_str}")
    return None
