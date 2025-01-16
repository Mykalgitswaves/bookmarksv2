FROM --platform=linux/amd64 python:3.10.9

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "src.main:backend_app", "--host", "0.0.0.0", "--port", "8000"]
