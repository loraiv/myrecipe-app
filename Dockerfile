FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend /app

ENV FLASK_APP=app
CMD ["flask", "run", "--host=0.0.0.0"]
