FROM python:3.11-slim as base


RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements/shared.txt /app/requirements/shared.txt

RUN pip install --no-cache-dir --upgrade pip==23.3.1 \
    && pip install --no-cache-dir -r requirements/shared.txt

FROM base as train
COPY requirements/train.txt /app/requirements/train.txt
RUN pip install --no-cache-dir -r requirements/train.txt
COPY train .
ENV ENV=train
CMD ["python", "main.py"]

FROM base as inference
COPY requirements/inference.txt /app/requirements/inference.txt
RUN pip install --no-cache-dir -r requirements/inference.txt
ENV ENV=inference
COPY inference inference
CMD ["gunicorn", "inference.main:app", "-w 4", "-k uvicorn.workers.UvicornWorker", "-b 0.0.0.0:5000"]

EXPOSE 5000
