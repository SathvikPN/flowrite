#!/bin/bash

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=app.py
export GUNICORN_BIND=${GUNICORN_BIND:-"0.0.0.0:8000"}
export GUNICORN_LOG_LEVEL=${GUNICORN_LOG_LEVEL:-"info"}
export SECRET_KEY=${SECRET_KEY:-$(python3 -c "import secrets; print(secrets.token_hex(32))")}

# Create necessary directories
mkdir -p logs

# Start Gunicorn with configuration
exec gunicorn -c gunicorn.conf.py app:app 