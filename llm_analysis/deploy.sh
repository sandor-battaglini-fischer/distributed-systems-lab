#!/bin/bash

# Kill any existing gunicorn processes
pkill gunicorn

# Build the React app
cd client
npm install
npm run build
cd ..

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server using gunicorn in the background
gunicorn --config server/gunicorn_config.py --chdir server wsgi:app --daemon

# Wait for the server to start
sleep 5

# Check if the server is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "Server started successfully"
else
    echo "Server failed to start"
    exit 1
fi 