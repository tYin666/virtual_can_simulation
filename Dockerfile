FROM python:3.14-slim

WORKDIR /app
COPY console.py .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "console.py"]
CMD ["--speed", "72", "--interval-ms", "500", "--count", "10"]