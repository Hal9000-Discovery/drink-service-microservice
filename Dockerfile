# ------------------------------------
# Base image
# ------------------------------------
FROM python:3.13-slim

# Prevent Python from buffering output (makes logging immediate)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# ------------------------------------
# Install ODBC drivers and dependencies
# ------------------------------------
RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https unixodbc unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------
# Copy dependency files & install Python libs
# ------------------------------------
# Copy requirements first for better Docker build caching
COPY requirements.txt .

# Install dependencies (like Flask, SQLAlchemy, pyodbc, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------
# Copy the entire project into the container
# ------------------------------------
COPY . .

# ------------------------------------
# Environment setup for Flask app
# ------------------------------------
# Expose the internal port Flask will run on
EXPOSE 5001

# Default environment variables
ENV FLASK_CONFIG=production
ENV PORT=5001

# ------------------------------------
# Run the application
# ------------------------------------
# Use environment variable for the port
CMD ["python", "main.py"]
