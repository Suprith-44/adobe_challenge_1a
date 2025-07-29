# Use official Python 3.10 slim image for smaller size
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system-level dependencies (for building wheels etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# Copy your script, requirements, and files folder
COPY test.py .
COPY requirements.txt .
COPY files/ files/

# Create the output directory
RUN mkdir -p output

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run your PDF processor
CMD ["python", "process_pdfs.py"]
