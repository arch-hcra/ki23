FROM python:3.10-slim

WORKDIR /app


RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
