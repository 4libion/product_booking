FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
      curl \
      postgresql-client \
      netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN chmod +x wait_for_db.sh

CMD ["sh", "wait_for_db.sh", "db"]
