from starlette.responses import HTMLResponse
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
import requests
from pydantic import BaseModel
import RPi.GPIO as GPIO
from datetime import datetime
from fastapi.templating import Jinja2Templates
from pywizlight import wizlight, PilotBuilder


router = APIRouter(prefix="/sunset")

templates = Jinja2Templates(directory="templates")


living_room_bulb_1 = wizlight("192.168.0.198")
desk_bulb_1 = wizlight("192.168.0.102")
golden_roast_bulb_1 = wizlight("192.168.0.217")

all_lamps = [
     living_room_bulb_1,
     desk_bulb_1,
     golden_roast_bulb_1
]

@router.get("/")
def sunset_root(request: Request):
    return templates.TemplateResponse("sunset.html", {
        "request": request
    })


@router.get("/off")
def off(request: Request, room: str = "all"):
    for lamp in all_lamps:
        lamp.turn_off()
    return RedirectResponse(request.url_for("sunset_root"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/on")
def on(request: Request, room: str = "all"):
    for lamp in all_lamps:
        lamp.turn_on(PilotBuilder())
    return RedirectResponse(request.url_for("sunset_root"), status_code=status.HTTP_303_SEE_OTHER)
