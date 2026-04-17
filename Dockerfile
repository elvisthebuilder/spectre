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

# Create a non-root user (Hugging Face standard)
RUN useradd -m -u 1000 user
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend:${PYTHONPATH}"
ENV SPECTRE_TRANSPORT=http
ENV PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/dist/cache/*

# Install Playwright system dependencies (as root)
RUN pip install playwright && \
    playwright install-deps chromium

# Prepare permissions for non-root execution
RUN chown -R user:user /app
USER user

# Install Python dependencies (as non-root)
COPY --chown=user:user backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --user -r backend/requirements.txt

# Install Playwright browsers (as non-root, in user home)
RUN python -m playwright install chromium

# Copy application source
COPY --chown=user:user . .

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure intelligence is a package
RUN touch /app/backend/intelligence/__init__.py

# Expose the HF standard port
EXPOSE 7860

# Default command launches the unified FastAPI app in HTTP mode
ENTRYPOINT ["python", "backend/mcp_server.py"]
