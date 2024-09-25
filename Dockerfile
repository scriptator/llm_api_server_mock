FROM python:3.12-slim

WORKDIR /app

COPY ./poetry.lock /app
COPY ./pyproject.toml /app

RUN pip install poetry
RUN poetry install

COPY ./llm_api_server_mock /app/llm_api_server_mock

LABEL org.opencontainers.image.source="https://github.com/hummerichsander/llm_api_server_mock"

CMD ["poetry", "run", "fastapi", "run", "llm_api_server_mock/main.py", "--port", "8080"]
