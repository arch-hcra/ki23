FROM python:3.11-slim

WORKDIR /app

COPY app.py .
COPY test_app.py .

RUN python -m unittest test_app.py

CMD ["python", "app.py"]
