FROM python:3.11-slim


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN mkdir -p /app/resources/uploads/images /app/resources/uploads/audio /tmp/avatars /tmp/podcast_audio /tmp/podcast_covers /tmp/playlist_covers


EXPOSE 8000


CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]