# ============================================================================
# SendCloud to AWS S3 - Flask Webhook Receiver Docker Image
# ============================================================================
# Multi-stage build strategy to reduce final image size:
# - Stage 1 (builder): Install all Python dependencies in isolated venv
# - Stage 2 (final): Copy only the venv and application code, discard build tools
# This approach eliminates ~500MB of build-only packages from the final image
# ============================================================================

# ============================================================================
# STAGE 1: Builder Stage
# ============================================================================
# Use python:3.10-slim as base - lightweight Python image (165MB vs 900MB full)
# Matches project's Python 3.10 requirement
FROM python:3.10-slim AS builder

WORKDIR /app

# Copy requirements.txt first (before application code)
# Docker caches layers, so dependencies only reinstall if requirements.txt changes
# Application code changes won't trigger expensive pip install re-execution
COPY requirements.txt .

# Create isolated virtual environment in /opt/venv
# Benefits: Cleaner PATH management and explicit dependency isolation
# Add venv bin directory to PATH for pip install commands
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip, setuptools, and wheel to latest versions
# --no-cache-dir: Skip pip's cache to reduce build context and layer size (~100MB)
# This ensures compatibility with all package wheels and avoids version issues
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: Final Production Image
# ============================================================================
# Use same python:3.10-slim base for consistency
# The builder stage is discarded, keeping only the compiled venv (~50MB)
FROM python:3.10-slim

WORKDIR /app

# Copy pre-built virtual environment from builder stage
# This venv contains all compiled Python packages ready to use
# Much faster than re-installing dependencies in production image
COPY --from=builder /opt/venv /opt/venv

# Copy application source code and configuration
# Order matters: app/ and config/ are application core
COPY app/ ./app/
COPY config/ ./config/
COPY run.py .

# Copy requirements.txt for reference/documentation in container
# Useful for debugging and verifying container contents
COPY requirements.txt .

# Create logs directory with proper permissions
# Application logger writes rotated logs here (10MB per file, 10 backups)
# Pre-creating ensures directory exists even if app starts before writing logs
RUN mkdir -p logs

# ============================================================================
# Environment Configuration
# ============================================================================
# Add venv bin to PATH so python/pip commands use venv binaries
ENV PATH="/opt/venv/bin:$PATH"

# PYTHONUNBUFFERED=1: Disable Python output buffering
# Ensures logs appear immediately in docker logs (don't wait for buffer flush)
# Critical for monitoring and debugging containerized applications

# FLASK_ENV=production: Enable production mode
# Disables debug mode, enables error handling optimizations, and security features
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# ============================================================================
# Health Check Configuration
# ============================================================================
# Docker health check - monitors container status continuously
# - --interval=30s: Check health every 30 seconds
# - --timeout=10s: Allow 10 seconds for health check to complete before timeout
# - --start-period=5s: Wait 5 seconds for app startup before first health check
# - --retries=3: Mark unhealthy after 3 consecutive failed checks (90 seconds total)
# Calls /health endpoint which validates app initialization and AWS connectivity
# Enables Docker orchestration tools (Kubernetes, ECS) to automatically restart unhealthy containers
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# ============================================================================
# Port Exposure
# ============================================================================
# Document that Flask app listens on port 5000
# EXPOSE doesn't publish ports - use docker run -p flag or docker-compose for mapping
# Example: docker run -p 5000:5000 sendcloud-to-s3
EXPOSE 5000

# ============================================================================
# Application Startup
# ============================================================================
# CMD: Default command when container starts
# Runs Flask application via run.py which calls create_app() factory
# Application expects these env vars from container: FLASK_ENV, FLASK_HOST, FLASK_PORT,
# SENDCLOUD_APP_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET
CMD ["python", "run.py"]
