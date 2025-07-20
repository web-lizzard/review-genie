# Stage 1: Install uv
FROM python:3.13.2-slim as uv-installer

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Stage 2: Bootstrap project for development
FROM python:3.13.2-slim as development

# Copy uv from previous stage
COPY --from=uv-installer /usr/local/bin/uv /usr/local/bin/uv
COPY --from=uv-installer /usr/local/bin/uvx /usr/local/bin/uvx

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code (needed before uv sync for editable install)
COPY domain/ ./domain/
COPY application/ ./application/
COPY adapters/ ./adapters/
COPY bootstrap/ ./bootstrap/
COPY run_web_server.py ./

# Install all dependencies including dev dependencies
RUN uv sync

# Run the application
CMD ["uv", "run", "run_web_server.py"]

# Stage 3: Export requirements for production
FROM python:3.13.2-slim as requirements-export

# Copy uv from first stage
COPY --from=uv-installer /usr/local/bin/uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code (needed for uv to understand project structure)
COPY domain/ ./domain/
COPY application/ ./application/
COPY adapters/ ./adapters/
COPY bootstrap/ ./bootstrap/
COPY run_web_server.py ./

# Export production requirements without editable installs and hashes
RUN uv export --format requirements-txt --no-dev --no-hashes --no-editable > requirements_temp.txt && \
    grep -v "^\\.$" requirements_temp.txt > requirements.txt && \
    rm requirements_temp.txt

# Stage 4: Production image
FROM python:3.13.2-slim as production

# Set working directory
WORKDIR /app

# Copy requirements.txt from export stage
COPY --from=requirements-export /app/requirements.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Copy source code
COPY domain/ ./domain/
COPY application/ ./application/
COPY adapters/ ./adapters/
COPY bootstrap/ ./bootstrap/
COPY run_web_server.py ./

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run_web_server.py"]
