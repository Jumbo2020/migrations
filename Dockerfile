# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run
CMD ["python3", "fetch_gcp.py"]
