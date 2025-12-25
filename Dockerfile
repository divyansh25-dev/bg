# Use a lightweight version of Python
FROM python:3.9-slim

# Install system dependencies required for image processing
# (These are linux libraries needed for the AI to "see" images)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a clear folder for the AI models so they don't get lost
# This helps the app find the downloaded BiRefNet model
RUN mkdir -p /root/.u2net

# Copy the rest of the code
COPY . .

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]