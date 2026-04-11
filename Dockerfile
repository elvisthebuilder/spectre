# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Maigret, Holehe, and Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/dist/cache/*

# Set the working directory in the container
WORKDIR /app

# Copy the backend requirements file into the container
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Playwright and its system dependencies
RUN pip install playwright && \
    playwright install-deps chromium && \
    playwright install chromium

# Copy the rest of the application code
COPY . /app

# Ensure intelligence is treated as a package
RUN touch /app/backend/intelligence/__init__.py

# Set environment path so modules are found correctly
ENV PYTHONPATH="/app/backend:${PYTHONPATH}"

# Expose the port (though for stdio MCP it isn't strictly necessary)
# EXPOSE 8000

# The default command runs the MCP server via stdio
ENTRYPOINT ["python", "backend/mcp_server.py"]
