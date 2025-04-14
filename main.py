import os
import logging
from app import app
from models import db

# Set up logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(host="0.0.0.0", port=5000, debug=True)
