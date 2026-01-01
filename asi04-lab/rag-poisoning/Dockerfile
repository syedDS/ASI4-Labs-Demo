FROM python:3.11-slim

WORKDIR /app

RUN pip install chromadb

COPY seed.py .

CMD ["python", "seed.py"]
