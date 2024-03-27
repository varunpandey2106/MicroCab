import os
import databases

# Replace 'your_password', 'your_username', 'your_host', 'your_database', and 'your_port' with your actual values
POSTGRES_PASSWORD = 'boombamboom'
POSTGRES_USER = 'varunpandey'
POSTGRES_HOST = 'localhost'
POSTGRES_DB = 'mr'
POSTGRES_PORT = '5432'

# Construct PostgreSQL URL
DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# Create a databases.Database instance
database = databases.Database(DATABASE_URL)
