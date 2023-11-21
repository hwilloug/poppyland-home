from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from apps import raincloud, sunset
from fastapi import Request
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(raincloud.router)
app.include_router(sunset.router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request
    })