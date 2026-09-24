# Basic Dockerfile for the Flask chat app

FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the app
COPY . .

EXPOSE 5000

CMD ["python", "wsgi.py"]
