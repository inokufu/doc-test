# Use the official Python image from the Docker Hub
FROM python:3.11-bullseye

WORKDIR /app
COPY . /app

RUN apt-get update \
    && pip install pipenv

RUN pipenv install --system --deploy

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
