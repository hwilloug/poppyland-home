cd rpiserver
poetry run uvicorn app:app --reload --port 8080 --root-path /home
