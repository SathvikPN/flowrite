import os
import sys

# Add your project directory to the sys.path
project_home = '/home/sathvikpn/flowrite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # Replace with your actual secret key

# Import your Flask app
from app import app as application  # PythonAnywhere looks for 'application' 