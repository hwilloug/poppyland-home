from starlette.responses import HTMLResponse
from fastapi import FastAPI
from pydantic import BaseModel
import RPi.GPIO as GPIO
from datetime import datetime


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
        
    
valve = Valve(gpio=17).init()
led1 = LED(gpio=22).init()
led2 = LED(gpio=27).init()

api = FastAPI()

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

@api.get("/")
def root():
  return generate_html_root_response()

def generate_html_root_response() -> HTMLResponse:
  state = "opened" if valve.is_open else "closed"
  state_color = "blue" if valve.is_open else "green"
  time_in_state = datetime.now() - valve.last_changed
  html_content = f"""
  <html style="background-color: dodgerblue; color: white;">
    <head>
      <title>Poppyland Raincloud</title>
    </head>
    <body>
      <div id="header">
        <h1>Poppyland Raincloud</h1>
      </div>
      <div id="tile-container" style="display: flex; flex-direction: row; gap: 50px;">
        <div id="status" style="background-color: white; color: black; border: 1px solid lightgrey; padding: 20px;">
          <h2>Raincloud Status<h2>
          <p style="color: {state_color}">{state}</p>
          <p>Time in this state: {time_in_state}</p>
        </div>
        <div id="controls" style="background-color: white; color: black;">
          <button onclick="location.href='/api/valves/open'" type="button" style="padding: 50px; background-color: blue; color: white; border-radius: 50px;">OPEN</button>
          <button onclick="location.href='/api/valves/close'" type="button" style="padding: 50px; background-color: green; color: white; border-radius: 50px;">CLOSE</button>
        </div>
      </div>
    </body>
  </html>
  """
  return HTMLResponse(content=html_content, status_code=200)

def generate_html_redirect_response() -> HTMLResponse:
    html_content = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="1; url='/api'" />
      </head>
      <body>
          <p>Processing...</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)