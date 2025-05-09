FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 6490

CMD ["python", "src/app.py"] 