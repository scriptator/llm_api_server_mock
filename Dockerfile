FROM python:3.12-slim

WORKDIR /app

COPY ./poetry.lock /app
COPY ./pyproject.toml /app

RUN pip install poetry
RUN poetry install

COPY ./openai_api_server_mock /app/openai_api_server_mock

CMD ["poetry", "run", "fastapi", "run", "openai_api_server_mock/main.py", "--port", "8000"]