# --- STAGE 1: Frontend Build ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy frontend source
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm build

# --- STAGE 2: Final Production Image ---
FROM python:3.11-slim
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend:${PYTHONPATH}"
ENV SPECTRE_TRANSPORT=http
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/dist/cache/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Playwright and dependencies
RUN pip install playwright && \
    playwright install-deps chromium && \
    playwright install chromium

# Copy application source
COPY . .

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure intelligence is a package
RUN touch /app/backend/intelligence/__init__.py

# Expose the production port
EXPOSE 8000

# Default command launches the unified FastAPI app in HTTP mode
ENTRYPOINT ["python", "backend/mcp_server.py"]
