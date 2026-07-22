FROM python:3.12-slim

WORKDIR /app

COPY libs/deepagents libs/deepagents
COPY server server

RUN pip install --no-cache-dir -e libs/deepagents \
    && pip install --no-cache-dir -r server/requirements.txt

EXPOSE 10000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "10000"]
