FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
RUN mkdir -p /app/favicons

VOLUME ["/app/favicons"]

EXPOSE 5000

CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0", "--port=5000"]

