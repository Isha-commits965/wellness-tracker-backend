# Use a lightweight Python image
FROM python:3.12-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Run database migrations and start the application
# CMD ["/bin/bash", "-c", "alembic upgrade head && python start_production.py"]
# The start command is now handled by Render's service configuration (render.yaml)
# This Dockerfile is primarily for building the image.