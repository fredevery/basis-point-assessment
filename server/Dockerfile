# BasisPoint Django Backend Dockerfile
FROM python:3.13.5-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "basispoint.wsgi:application", "--bind", "0.0.0.0:8000"]
