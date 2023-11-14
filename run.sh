cd rpiserver
poetry run uvicorn rpiserver.server:api --reload --port 8080
