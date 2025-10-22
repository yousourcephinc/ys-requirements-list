FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create guides directory if it doesn't exist
RUN mkdir -p guides

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV GCP_PROJECT_ID=requirements-mcp-server
ENV GCP_LOCATION=us-central1
ENV PYTHONPATH=/app

# Command to run the MCP server with gunicorn
WORKDIR /app/mcp
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 guides_mcp_http_server:app