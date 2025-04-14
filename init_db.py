import os
import logging
from app import app
from models import db

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize database
with app.app_context():
    logging.info("Creating database tables...")
    db.create_all()
    logging.info("Database tables created successfully!")