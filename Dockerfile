FROM python:3.12-slim

WORKDIR /app

# Install runtime deps only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and necessary modules
COPY app ./app
COPY constraints.py tools.py ./

# Cloud Run expects the app to listen on $PORT
ENV PORT=8080
EXPOSE 8080

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
