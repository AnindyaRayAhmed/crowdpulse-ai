FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Expose port 8080 mapping
EXPOSE 8080

# Cloud run requires the default command to start the web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
