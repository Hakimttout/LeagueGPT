# LeagueGPT_backend/Dockerfile

# Use slim Python image for minimal size
FROM python:3.10-slim

# Set working directory
WORKDIR /app/LeagueGPT_backend

# Add LeagueGPT project directory to Python path
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Copy requirements file and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full backend source code into the container
COPY . /app

# Expose the port used by Django
EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
