# We upgrade to Python 3.10-slim which has better repository support
FROM python:3.10-slim

# Fix: We replaced 'libgl1-mesa-glx' with 'libgl1' which is the modern standard
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the folder for AI models
RUN mkdir -p /root/.u2net

# Copy the rest of the code
COPY . .

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
