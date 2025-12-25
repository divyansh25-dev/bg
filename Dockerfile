FROM python:3.10-slim

# Install system libraries (Required for Alpha Matting image operations)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create folder for AI models
RUN mkdir -p /root/.u2net

COPY . .

# Explicitly bind to Port 10000 for Render
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
