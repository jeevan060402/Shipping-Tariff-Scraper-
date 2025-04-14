import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Region(db.Model):
    """Model representing a geographical region."""
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    countries = db.relationship('Country', backref='region', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Region {self.name}>"

class Country(db.Model):
    """Model representing a country within a region."""
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    ports = db.relationship('Port', backref='country', lazy=True, cascade="all, delete-orphan")
    tariffs = db.relationship('Tariff', backref='country', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Country {self.name}>"

class Port(db.Model):
    """Model representing a port within a country."""
    __tablename__ = 'ports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    
    def __repr__(self):
        return f"<Port {self.name}>"

class Tariff(db.Model):
    """Model representing a shipping tariff."""
    __tablename__ = 'tariffs'
    
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    liner_name = db.Column(db.String(100), nullable=False)
    port_name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    free_days = db.Column(db.Integer, nullable=True)
    valid_from = db.Column(db.Date, nullable=True, default=datetime.date.today)
    valid_to = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    buckets = db.relationship('TariffBucket', backref='tariff', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tariff {self.port_name} - {self.equipment_type}>"

class TariffBucket(db.Model):
    """Model representing a specific rate bucket for a tariff."""
    __tablename__ = 'tariff_buckets'
    
    id = db.Column(db.Integer, primary_key=True)
    tariff_id = db.Column(db.Integer, db.ForeignKey('tariffs.id'), nullable=False)
    bucket_number = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"<TariffBucket {self.bucket_number} ({self.start_day}-{self.end_day} days): {self.rate}>"
