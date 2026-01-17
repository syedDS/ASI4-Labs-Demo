FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY app.py .

RUN mkdir -p /packages

EXPOSE 8081

CMD ["python", "app.py"]
