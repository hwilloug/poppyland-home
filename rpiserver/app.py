from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import raincloud


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(raincloud.router)

@app.get("/")
def root():
    return {"message": "Hello, world!"}