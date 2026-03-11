FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CHAINLIT_HOST=0.0.0.0
ENV CHAINLIT_PORT=8000

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential graphviz \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /workspace/requirements.txt

COPY src /workspace/src

EXPOSE 8000

CMD ["chainlit", "run", "src/app.py", "-w", "--host", "0.0.0.0", "--port", "8000"]
