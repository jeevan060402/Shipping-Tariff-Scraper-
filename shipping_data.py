"""
Shipping industry specific data generation.
This module provides realistic shipping industry data for testing purposes
when real data cannot be scraped from the shipping line websites.
"""
import random
from datetime import datetime, timedelta

# Common container equipment types and their dimensions
EQUIPMENT_TYPES = {
    "20' Standard (20SD)": {"length": "20'", "height": "8'6\"", "description": "General purpose container"},
    "40' Standard (40SD)": {"length": "40'", "height": "8'6\"", "description": "General purpose container"},
    "40' High Cube (40HC)": {"length": "40'", "height": "9'6\"", "description": "High cube container"},
    "45' High Cube (45HC)": {"length": "45'", "height": "9'6\"", "description": "High cube container"},
    "20' Refrigerated (20RF)": {"length": "20'", "height": "8'6\"", "description": "Refrigerated container"},
    "40' Refrigerated (40RF)": {"length": "40'", "height": "9'6\"", "description": "Refrigerated high cube container"},
    "20' Open Top (20OT)": {"length": "20'", "height": "8'6\"", "description": "Open top container"},
    "40' Open Top (40OT)": {"length": "40'", "height": "8'6\"", "description": "Open top container"},
    "20' Flat Rack (20FR)": {"length": "20'", "height": "8'6\"", "description": "Flat rack container"},
    "40' Flat Rack (40FR)": {"length": "40'", "height": "8'6\"", "description": "Flat rack container"},
    "20' Tank (20TK)": {"length": "20'", "height": "8'6\"", "description": "Tank container for liquids"},
}

# Major shipping lines
SHIPPING_LINES = [
    "Hapag-Lloyd",
    "Maersk",
    "MSC",
    "CMA CGM",
    "COSCO",
    "ONE (Ocean Network Express)",
    "Evergreen",
    "Yang Ming",
    "HMM",
    "ZIM",
]

# Currency codes commonly used in shipping
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CNY", "SGD"]

# Region and country mappings with major ports
REGIONS_COUNTRIES_PORTS = {
    "North America": {
        "United States": [
            "Los Angeles/Long Beach", "New York/New Jersey", "Savannah", 
            "Seattle/Tacoma", "Houston", "Oakland", "Norfolk", "Charleston", 
            "Miami", "Baltimore"
        ],
        "Canada": [
            "Vancouver", "Montreal", "Halifax", "Prince Rupert", "Toronto"
        ],
        "Mexico": [
            "Manzanillo", "Veracruz", "Altamira", "Lazaro Cardenas", "Ensenada"
        ],
    },
    "South America": {
        "Brazil": [
            "Santos", "Paranagua", "Rio de Janeiro", "Itajai", "Rio Grande"
        ],
        "Argentina": [
            "Buenos Aires", "Rosario", "Zarate", "Bahia Blanca"
        ],
        "Chile": [
            "San Antonio", "Valparaiso", "Iquique", "Antofagasta", "Coronel"
        ],
        "Colombia": [
            "Cartagena", "Buenaventura", "Barranquilla", "Santa Marta"
        ],
        "Peru": [
            "Callao", "Paita", "Matarani"
        ],
    },
    "Europe": {
        "Germany": [
            "Hamburg", "Bremerhaven", "Wilhelmshaven", "Duisburg"
        ],
        "Netherlands": [
            "Rotterdam", "Amsterdam"
        ],
        "Belgium": [
            "Antwerp", "Zeebrugge"
        ],
        "United Kingdom": [
            "Felixstowe", "Southampton", "London Gateway", "Liverpool"
        ],
        "Spain": [
            "Algeciras", "Barcelona", "Valencia", "Bilbao"
        ],
        "Italy": [
            "Genoa", "La Spezia", "Naples", "Gioia Tauro", "Trieste"
        ],
        "France": [
            "Le Havre", "Marseille-Fos", "Dunkirk"
        ],
    },
    "Asia": {
        "China": [
            "Shanghai", "Ningbo-Zhoushan", "Shenzhen", "Guangzhou-Nansha", 
            "Qingdao", "Tianjin", "Xiamen", "Dalian"
        ],
        "Singapore": [
            "Singapore"
        ],
        "Malaysia": [
            "Port Klang", "Tanjung Pelepas", "Penang"
        ],
        "Japan": [
            "Tokyo", "Yokohama", "Nagoya", "Kobe", "Osaka"
        ],
        "South Korea": [
            "Busan", "Incheon", "Gwangyang"
        ],
        "Taiwan": [
            "Kaohsiung", "Taipei", "Keelung", "Taichung"
        ],
        "Vietnam": [
            "Ho Chi Minh City", "Hai Phong", "Da Nang", "Cai Mep"
        ],
        "India": [
            "Mumbai", "Chennai", "Mundra", "Kolkata", "Cochin"
        ],
    },
    "Middle East": {
        "United Arab Emirates": [
            "Dubai (Jebel Ali)", "Abu Dhabi", "Sharjah", "Fujairah"
        ],
        "Saudi Arabia": [
            "Jeddah", "King Abdullah", "Dammam"
        ],
        "Oman": [
            "Salalah", "Sohar"
        ],
        "Qatar": [
            "Doha"
        ],
        "Israel": [
            "Haifa", "Ashdod"
        ],
    },
    "Africa": {
        "Egypt": [
            "Port Said", "Alexandria", "Damietta", "Sokhna"
        ],
        "South Africa": [
            "Durban", "Cape Town", "Port Elizabeth", "Coega"
        ],
        "Morocco": [
            "Tanger Med", "Casablanca"
        ],
        "Nigeria": [
            "Lagos (Apapa)", "Tin Can Island", "Onne"
        ],
        "Kenya": [
            "Mombasa"
        ],
    },
    "Oceania": {
        "Australia": [
            "Sydney", "Melbourne", "Brisbane", "Fremantle", "Adelaide"
        ],
        "New Zealand": [
            "Auckland", "Tauranga", "Lyttelton", "Napier", "Wellington"
        ],
    },
}

def get_free_days_range(country, equipment_type):
    """
    Return realistic free days range based on country and equipment type.
    Different countries and equipment types have different standard free days.
    """
    # Base free days
    base_free_days = 7
    
    # Refrigerated containers typically have shorter free time
    if "Refrigerated" in equipment_type:
        base_free_days -= 2
    
    # Adjust by region/country typical practices
    if country in REGIONS_COUNTRIES_PORTS["North America"].keys():
        base_free_days += 1
    elif country in REGIONS_COUNTRIES_PORTS["Asia"].keys():
        if country == "China":
            base_free_days -= 1
        elif country == "Singapore":
            base_free_days += 1
    elif country in REGIONS_COUNTRIES_PORTS["Europe"].keys():
        if country in ["Germany", "Netherlands", "Belgium"]:
            base_free_days += 2
    
    # Add some natural variation (±1 day)
    variation = random.choice([-1, 0, 0, 0, 1])
    free_days = max(3, base_free_days + variation)  # Minimum 3 days free time
    
    return free_days

def get_detention_demurrage_rates(country, equipment_type):
    """
    Generate realistic detention and demurrage rates based on country and equipment type.
    Returns a list of rate buckets with start_day, end_day, and rate values.
    """
    buckets = []
    free_days = get_free_days_range(country, equipment_type)
    
    # Base rate depends on container size
    if "20'" in equipment_type:
        base_rate = random.uniform(25.0, 35.0)
    elif "40'" in equipment_type or "45'" in equipment_type:
        base_rate = random.uniform(50.0, 70.0)
    else:
        base_rate = random.uniform(40.0, 60.0)
    
    # Specialty equipment has higher rates
    if any(specialty in equipment_type for specialty in ["Refrigerated", "Open Top", "Flat Rack", "Tank"]):
        base_rate *= random.uniform(1.5, 2.0)
    
    # Adjust by region/country
    if country in REGIONS_COUNTRIES_PORTS["North America"].keys():
        base_rate *= random.uniform(1.1, 1.3)  # Higher rates in North America
    elif country in REGIONS_COUNTRIES_PORTS["Asia"].keys():
        if country == "Singapore":
            base_rate *= random.uniform(1.2, 1.4)  # Higher in Singapore
        else:
            base_rate *= random.uniform(0.8, 1.0)  # Slightly lower in other Asian countries
    
    # Round to nearest dollar
    base_rate = round(base_rate)
    
    # First period (typically 1-5 days after free time)
    start_day = free_days + 1
    end_day = start_day + random.randint(4, 6) - 1
    buckets.append({
        "bucket_number": 1,
        "start_day": start_day,
        "end_day": end_day,
        "rate": base_rate
    })
    
    # Second period (typically ~7 days)
    start_day = end_day + 1
    end_day = start_day + random.randint(6, 8) - 1
    buckets.append({
        "bucket_number": 2,
        "start_day": start_day,
        "end_day": end_day,
        "rate": base_rate * random.uniform(1.8, 2.2)  # Approximately double
    })
    
    # Third period (until ~30 days)
    start_day = end_day + 1
    end_day = start_day + random.randint(13, 17) - 1
    buckets.append({
        "bucket_number": 3,
        "start_day": start_day,
        "end_day": end_day,
        "rate": base_rate * random.uniform(2.8, 3.5)  # Approximately triple
    })
    
    # Final period (indefinite)
    start_day = end_day + 1
    end_day = 999  # Effectively unlimited
    buckets.append({
        "bucket_number": 4,
        "start_day": start_day,
        "end_day": end_day,
        "rate": base_rate * random.uniform(3.8, 4.5)  # Approximately quadruple
    })
    
    # Round all rates to nearest dollar (or 0.5 for some currencies)
    for bucket in buckets:
        bucket["rate"] = round(bucket["rate"] * 2) / 2
    
    return buckets

def generate_realistic_tariff_data(country_name, region_name):
    """
    Generate realistic tariff data for a country.
    
    Args:
        country_name: Name of the country
        region_name: Name of the region
        
    Returns:
        list: List of tariff dictionaries
    """
    # Get ports for this country based on our mapping
    if region_name in REGIONS_COUNTRIES_PORTS and country_name in REGIONS_COUNTRIES_PORTS[region_name]:
        ports = REGIONS_COUNTRIES_PORTS[region_name][country_name]
    else:
        # Fallback to some generic port names
        ports = ["Main Port", "Secondary Port"]
    
    # Choose a subset of equipment types (usually not all types are listed)
    equipment_types = random.sample(list(EQUIPMENT_TYPES.keys()), 
                                   k=random.randint(3, min(6, len(EQUIPMENT_TYPES))))
    
    # Choose shipping line (for testing we'll use Hapag-Lloyd)
    shipping_line = "Hapag-Lloyd"
    
    # Choose currency (most commonly USD for international shipping)
    currency = random.choice(["USD", "USD", "USD", "EUR"])  # Weighted toward USD
    
    # Validity period (typically 3-6 months validity)
    today = datetime.now().date()
    valid_from = today - timedelta(days=random.randint(0, 30))  # Start date sometimes in the past
    validity_period = random.randint(90, 180)  # 3-6 months
    valid_to = valid_from + timedelta(days=validity_period)
    
    # Generate tariffs for each port and equipment type
    tariffs = []
    
    for port in ports:
        for equipment_type in equipment_types:
            free_days = get_free_days_range(country_name, equipment_type)
            rate_buckets = get_detention_demurrage_rates(country_name, equipment_type)
            
            tariff = {
                "liner_name": shipping_line,
                "port": port,
                "equipment_type": equipment_type,
                "currency": currency,
                "free_days": free_days,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "buckets": rate_buckets
            }
            
            tariffs.append(tariff)
    
    return tariffs