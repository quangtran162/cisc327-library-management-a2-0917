# Use official Python image
FROM python:3.13-slim

# Workdir inside container
WORKDIR /app

# Install system deps (if sqlite headers needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Ensure Python finds your app package
ENV PYTHONPATH=/app

# Flask listens on 0.0.0.0:5000 in app.py[file:51]
EXPOSE 5000

# Default command: run your existing app.py
CMD ["python", "app.py"]
