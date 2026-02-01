# ChaosClaw Dockerfile
# The Trust Sentinel for AI Agents

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY chaosclaw/ ./chaosclaw/

# Set Python path
ENV PYTHONPATH=/app

# Run ChaosClaw
CMD ["python", "-m", "chaosclaw.main"]
