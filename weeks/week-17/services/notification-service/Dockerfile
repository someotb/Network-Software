FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notifications.proto .
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notifications.proto

COPY main.py .

EXPOSE 50051

CMD ["python", "main.py"]
