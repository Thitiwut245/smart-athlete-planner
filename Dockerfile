# --- Dockerfile ---
FROM python:3.11-slim

# set working directory
WORKDIR /app

# copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy rest of the project
COPY . .

# expose port for uvicorn
EXPOSE 8000

# environment variable for uvicorn
ENV PYTHONUNBUFFERED=1

# start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
