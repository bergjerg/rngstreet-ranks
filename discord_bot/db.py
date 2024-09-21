# db.py

import mysql.connector
from config import DB_SETTINGS

def get_db_connection():
    """Establish a new database connection."""
    return mysql.connector.connect(**DB_SETTINGS)
