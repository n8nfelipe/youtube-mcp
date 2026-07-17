FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD YOUTUBE_API_KEY=dummy python healthcheck.py

ENTRYPOINT ["python", "server.py"]
