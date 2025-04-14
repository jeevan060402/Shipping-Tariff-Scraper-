# Shipping-Tariff-Scraper-
# Shipping Line Tariff Scraper

A Python-based system for scraping, processing, and storing shipping line tariff data from Hapag-Lloyd website using web scraping and LLM techniques.

## Overview

This application allows users to access detention and demurrage tariff information from shipping lines, either through automated web scraping or manual PDF uploads. The system processes tariff documents, extracts structured data using AI/LLM, and presents the information through a user-friendly web interface.

## Features

- **Web Scraping**: Attempts to scrape tariff data from Hapag-Lloyd's website with advanced anti-blocking techniques
- **PDF Upload**: Manual upload capability for processing tariff PDFs when scraping is blocked
- **AI Processing**: Uses OpenAI's GPT models to extract structured data from PDFs
- **Realistic Test Data**: Generates industry-specific test data when live data isn't accessible
- **RESTful API**: Provides API endpoints for accessing tariff information
- **Responsive UI**: Clean web interface for viewing and comparing tariff rates

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy with SQLite (configurable for PostgreSQL)
- **PDF Processing**: PyPDF2, PDFPlumber, Tesseract OCR (via pytesseract)
- **AI/ML**: OpenAI API
- **Web Scraping**: Requests, BeautifulSoup4
- **Frontend**: Bootstrap, JavaScript

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export FLASK_APP=main.py
   ```
4. Initialize the database:
   ```
   python init_db.py
   ```
5. Run the application:
   ```
   flask run
   ```

## Usage

### Web Interface

1. **Home Page**: Select a region to scrape or use the manual PDF upload feature
2. **Upload PDF**: Upload tariff PDFs for manual processing
3. **Results Page**: View and compare extracted tariff data

### API Endpoints

- `GET /api/regions`: List all regions
- `GET /api/countries?region_id={id}`: List countries in a region
- `GET /api/ports?country_id={id}`: List ports in a country
- `GET /api/tariffs?country_id={id}&port_name={name}&equipment_type={type}`: Get tariff data with optional filters

## Anti-Blocking Techniques

The application employs several techniques to avoid being blocked by websites:

1. **User-Agent Rotation**: Randomly selects from a pool of common browser signatures
2. **Referrer Spoofing**: Varies referrer information to simulate real browsing patterns
3. **Request Headers Variation**: Adds random headers like Via and Cookie
4. **Exponential Backoff**: Implements progressive delays between retries
5. **Session Management**: Maintains cookies and session data between requests

## PDF Processing Pipeline

1. **Text Extraction**: Uses PyPDF2 and PDFPlumber to extract text content
2. **OCR Backup**: Falls back to Tesseract OCR for scanned PDFs
3. **AI Processing**: Sends PDF content to OpenAI API for intelligent extraction
4. **Structured Data**: Converts unstructured PDF content into structured tariff information

## Test Data Generation

When live data cannot be scraped, the system generates realistic test data based on:

1. **Regional Variations**: Different regions and countries have different tariff structures
2. **Equipment-Specific Rates**: Rates vary by container type (20'/40', standard/refrigerated/etc.)
3. **Port-Specific Information**: Uses real port names for each country
4. **Tiered Rate Structures**: Creates realistic rate buckets with appropriate pricing tiers
5. **Industry Standards**: Follows shipping industry conventions for free days and rate increases

## Project Structure

- `app.py`: Main Flask application
- `config.py`: Configuration settings
- `models.py`: Database models
- `scraper.py`: Web scraping functionality
- `pdf_processor.py`: PDF processing pipeline
- `llm_processor.py`: OpenAI API integration
- `shipping_data.py`: Test data generation
- `templates/`: HTML templates
- `static/`: Static assets

## Future Enhancements

1. Add support for additional shipping lines
2. Implement automated scheduling for regular updates
3. Enhance visualization with charts and graphs
4. Add user authentication and personalized views
5. Develop export functionality (Excel, CSV, PDF reports)

## License

MIT

## Acknowledgments

- Hapag-Lloyd for providing tariff information
- OpenAI for GPT models used in processing