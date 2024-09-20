# Use Python 3.11 as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and install dependencies
RUN pip install --upgrade pip
RUN pip install poetry
COPY ./pyproject.toml poetry.lock /app/
RUN poetry install --only main

# Copy the rest of the app code
COPY ./o2_server /app/o2_server
COPY ./o2 /app/o2

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI server with Uvicorn
CMD ["poetry","run", "server"]
