FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install backend dependencies
COPY web_app/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and required assets
COPY web_app/backend/app ./app
COPY datasets ./datasets
COPY ckpts ./ckpts
COPY models ./models
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
