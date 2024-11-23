# Build stage for React app
FROM node:18 AS client-builder
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

# Production stage
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./server/

# Copy built React app
COPY --from=client-builder /app/client/build ./server/static/

# Set working directory to server folder
WORKDIR /app/server

# Create plots directory
RUN mkdir -p static/plots

# Expose port
EXPOSE 5000

# Run gunicorn
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"] 