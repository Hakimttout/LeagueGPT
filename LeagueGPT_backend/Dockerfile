# Dockerfile
FROM python:3.10-slim

WORKDIR /app/LeagueGPT_backend

ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY LeagueGPT_backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
