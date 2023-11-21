from starlette.responses import HTMLResponse
from fastapi import APIRouter, Request
import requests
from pydantic import BaseModel
import RPi.GPIO as GPIO
from datetime import datetime
from fastapi.templating import Jinja2Templates
import csv


router = APIRouter()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Valve(BaseModel):
    gpio: int
    is_open: bool = False
    last_changed: datetime = datetime.now()
    
    def init(self):
        print(f"Initializing valve {self.gpio}")
        GPIO.setup(self.gpio, GPIO.OUT)
        return self
    
    def open(self):
        print(f"Opening valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.HIGH)
        self.is_open = True
        self.last_changed = datetime.now()
        
    def close(self):
        print(f"Closing valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.LOW)
        self.is_open = False
        self.last_changed = datetime.now()


class LED(BaseModel):
    gpio: int
    is_on: bool = False
    
    def init(self):
        print(f"Initializing LED {self.gpio}")
        GPIO.setup(self.gpio, GPIO.OUT)
        return self
    
    def on(self):
        print(f"Turning on LED {self.gpio}")
        GPIO.output(self.gpio, GPIO.HIGH)
        self.is_on = True
        
    def off(self):
        print(f"Turning off LED {self.gpio}")
        GPIO.output(self.gpio, GPIO.LOW)
        self.is_on = False
    
valve = Valve(gpio=18).init()
led1 = LED(gpio=22).init()
led2 = LED(gpio=27).init()

@router.on_event("startup")
def startup():
    write_log("Starting up...")
    valve.close()
    led1.on()
    led2.off()


@router.on_event("shutdown")
def shutdown():
    write_log("Shutting down...")
    valve.close()
    led1.off()
    led2.off()
    
    
@router.get("/raincloud/status")
def valve_status():
    return {"is_open": valve.is_open}


@router.get("/raincloud/open")
def open_valve():
    if not valve.is_open:
        write_log(f"Opening valve {valve.gpio}")
        valve.open()
        led2.on()
    return generate_html_redirect_response()


@router.get("/raincloud/close")
def close_valve():
    if valve.is_open:
        write_log(f"Closing valve {valve.gpio}")
        valve.close()
        led2.off()
    return generate_html_redirect_response()


templates = Jinja2Templates(directory="templates")


@router.get("/raincloud")
def root(request: Request):
    response = requests.get(f"https://api.weatherapi.com/v1/forecast.json?q=29715&days=2&key=d25c5b1c56f648249a6222139231411")
    weather_data = response.json()
    response = requests.get(f"https://api.weatherapi.com/v1/astronomy.json?q=29715&dt={datetime.today().strftime('%Y-%m-%d')}&key=d25c5b1c56f648249a6222139231411")
    astro_data = response.json()
    moon_phase = astro_data.get("astronomy", {}).get("astro", {}).get("moon_phase")
    if moon_phase == "New Moon":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f311.svg"
    elif moon_phase == "Waxing Crescent":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f312.svg"
    elif moon_phase == "First Quarter":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f313.svg"
    elif moon_phase == "Waxing Gibbous":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f314.svg"
    elif moon_phase == "Full Moon":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f315.svg"
    elif moon_phase == "Waning Gibbous":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f316.svg"
    elif moon_phase == "Last Quarter":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f317.svg"
    elif moon_phase == "Waning Crescent":
        moon_image = "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/svg/1f318.svg"
    logs = get_logs()
    time_in_state_split = str(datetime.now() - valve.last_changed).split(':')
    time_in_state = {
            "hours": time_in_state_split[0],
            "minutes": time_in_state_split[1],
            "seconds": time_in_state_split[2].split('.')[0]
        }
    return templates.TemplateResponse("raincloud_index.html", {
        "request": request,
        "valve_state": valve,
        "time_in_state": time_in_state,
        "weather_data": weather_data,
        "astro_data": astro_data,
        "moon_image": moon_image,
        "logs": logs,
        "today": datetime.now()
    })


def generate_html_redirect_response() -> HTMLResponse:
    html_content = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="1; url='/raincloud'" />
      </head>
      <body>
          <p>Processing...</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


def write_log(message: str) -> None:
    with open('log.csv', 'a', newline='') as csvfile:
        writer =csv.writer(csvfile, delimiter=",")
        writer.writerow([datetime.now(), message])


def get_logs() -> list({"datetime": datetime, "message": str}):
    with open('log.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        logs = []
        for row in reader:
            logs.append({
                "datetime": datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'),
                "message": row[1]
            })
        logs.reverse()
        return logs