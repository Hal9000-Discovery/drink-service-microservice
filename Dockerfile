# ------------------------------------
# Base image
# ------------------------------------
FROM python:3.13-slim

# Prevent Python from buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
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
# Install Python dependencies
# ------------------------------------
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------
# Copy project files
# ------------------------------------
COPY . /app

# Expose Flask port
EXPOSE 5001

# Flask environment
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_CONFIG=production

# Start the service
CMD ["python", "main.py"]
