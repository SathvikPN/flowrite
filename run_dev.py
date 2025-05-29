#!/usr/bin/env python3
import os
import sys
from app import app, init_db

if __name__ == '__main__':
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Parse command line arguments
    use_reloader = '--no-reload' not in sys.argv
    
    # Initialize database if it doesn't exist
    if not os.path.exists(app.config['DATABASE']):
        print("Initializing development database...")
        init_db()
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=use_reloader  # Can be disabled with --no-reload
    ) 