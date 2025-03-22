# Use official Python 3.10 image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy all files from your project directory to /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (default for FastAPI)
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
