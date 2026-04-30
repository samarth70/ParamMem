# Stage 1: Build the React frontend
FROM node:20 AS build-stage
WORKDIR /app/src/web
COPY src/web/package*.json ./
RUN npm install
COPY src/web/ ./
RUN npm run build

# Stage 2: Setup the Python backend
FROM python:3.10-slim
WORKDIR /app
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire source code
COPY . .

# Copy the built frontend from build-stage to the root dist folder
COPY --from=build-stage /app/src/web/dist /app/dist

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Command to run the backend
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "7860"]
