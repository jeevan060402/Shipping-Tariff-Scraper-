import os
import logging
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from config import Config

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    
    Returns:
        conn: SQLite connection object
    """
    try:
        db_path = os.path.join(os.getcwd(), 'tariffs.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {str(e)}")
        raise

def initialize_database():
    """
    Initializes the SQLite database with the required tables.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            region_id INTEGER NOT NULL,
            url TEXT,
            FOREIGN KEY (region_id) REFERENCES regions (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country_id INTEGER NOT NULL,
            FOREIGN KEY (country_id) REFERENCES countries (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tariffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            liner_name TEXT NOT NULL,
            port_name TEXT NOT NULL,
            equipment_type TEXT NOT NULL,
            currency TEXT NOT NULL,
            free_days INTEGER,
            valid_from DATE,
            valid_to DATE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tariff_buckets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tariff_id INTEGER NOT NULL,
            bucket_number INTEGER NOT NULL,
            start_day INTEGER NOT NULL,
            end_day INTEGER NOT NULL,
            rate REAL NOT NULL,
            FOREIGN KEY (tariff_id) REFERENCES tariffs (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("Database initialized successfully")
    
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise

def export_to_excel(output_path=None):
    """
    Exports the tariff data to an Excel file.
    
    Args:
        output_path (str): Path to save the Excel file (optional)
        
    Returns:
        str: Path to the saved Excel file
    """
    try:
        conn = get_db_connection()
        
        # Query to get all tariff data
        query = '''
        SELECT 
            r.name as Region,
            c.name as Country,
            t.liner_name as "Liner Name",
            t.port_name as Port,
            t.equipment_type as "Equipment Type",
            t.currency as Currency,
            t.free_days as "Free Days",
            t.valid_from as "Valid From",
            t.valid_to as "Valid To",
            tb.bucket_number as "Bucket Number",
            tb.start_day as "Start Day",
            tb.end_day as "End Day",
            tb.rate as Rate
        FROM tariffs t
        JOIN countries c ON t.country_id = c.id
        JOIN regions r ON c.region_id = r.id
        JOIN tariff_buckets tb ON t.id = tb.tariff_id
        ORDER BY r.name, c.name, t.port_name, t.equipment_type, tb.bucket_number
        '''
        
        # Load data into DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Set default output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(os.getcwd(), f'tariff_data_{timestamp}.xlsx')
        
        # Ensure directory exists
        Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
        
        # Format date columns
        for date_col in ['Valid From', 'Valid To']:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main sheet with all data
            df.to_excel(writer, sheet_name='All Tariffs', index=False)
            
            # Summary sheet with counts by region and country
            summary = df.groupby(['Region', 'Country']).size().reset_index(name='Tariff Count')
            summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet for each region
            for region in df['Region'].unique():
                region_df = df[df['Region'] == region]
                region_df.to_excel(writer, sheet_name=f'{region}', index=False)
        
        conn.close()
        logging.info(f"Data exported to Excel: {output_path}")
        return output_path
    
    except Exception as e:
        logging.error(f"Error exporting data to Excel: {str(e)}")
        raise
