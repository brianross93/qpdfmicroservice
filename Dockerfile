# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install qpdf
RUN apt-get update && apt-get install -y qpdf && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Environment variables for production
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    NAME="World"

# Run app.py when the container launches
# Run the app with Gunicorn (3 workers)
CMD ["gunicorn", "-b", "0.0.0.0:5001", "--workers", "3", "app:app"]
