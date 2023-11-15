from starlette.responses import HTMLResponse
from fastapi import FastAPI, Request
import requests
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import RPi.GPIO as GPIO
from datetime import datetime
from fastapi.templating import Jinja2Templates
import csv


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
        write_log(f"Opening valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.HIGH)
        self.is_open = True
        self.last_changed = datetime.now()
        
    def close(self):
        write_log(f"Closing valve {self.gpio}")
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
        
    
valve = Valve(gpio=17).init()
led1 = LED(gpio=22).init()
led2 = LED(gpio=27).init()

api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")

@api.on_event("startup")
def startup():
    valve.close()
    led1.on()
    led2.off()

@api.on_event("shutdown")
def shutdown():
    valve.close()
    led1.off()
    led2.off()
    
@api.get("/valves/status")
def valve_status():
    return {"is_open": valve.is_open}

@api.get("/valves/open")
def open_valve():
    valve.open()
    led2.on()
    return generate_html_redirect_response()

@api.get("/valves/close")
def close_valve():
    valve.close()
    led2.off()
    return generate_html_redirect_response()

templates = Jinja2Templates(directory="templates")

@api.get("/")
def root(request: Request):
    response = requests.get(f"https://api.weatherapi.com/v1/forecast.json?q=29715&days=2&key=d25c5b1c56f648249a6222139231411")
    weather_data = response.json()
    logs = get_logs()
    return templates.TemplateResponse("index.html", {"request": request, "valve_state": valve, "weather_data": weather_data, "logs": logs})

def generate_html_redirect_response() -> HTMLResponse:
    html_content = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="1; url='/home'" />
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

def get_logs() -> list({"datetime": str, "message": str}):
    with open('log.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        logs = []
        for row in reader:
            logs.append({
                "datetime": row[0],
                "message": row[1]
            })
        logs.reverse()
        return logs