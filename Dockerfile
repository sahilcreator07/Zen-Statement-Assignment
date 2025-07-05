FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p data output

# Set environment variables
ENV PYTHONPATH=/app

# Run the agent
CMD ["python", "src/agentic_main.py"]
