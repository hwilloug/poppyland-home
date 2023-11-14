from starlette.responses import HTMLResponse
from fastapi import FastAPI
from pydantic import BaseModel
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Valve(BaseModel):
    gpio: int
    is_open: bool = False
    
    def init(self):
        print(f"Initializing valve {self.gpio}")
        GPIO.setup(self.gpio, GPIO.OUT)
        return self
    
    def open(self):
        print(f"Opening valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.HIGH)
        self.is_open = True
        
    def close(self):
        print(f"Closing valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.LOW)
        self.is_open = False


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
    return valve

@api.get("/valves/close")
def close_valve():
    valve.close()
    led2.off()
    return valve


app = FastAPI()

@app.get("/")
def root():
  return generate_html_response()

def generate_html_response() -> HTMLResponse:
  state = "opened" if valve.is_open else "closed"
  html_content = f"""
  <html>
    <head>
      <title>Poppyland Raincloud</title>
    </head>
    <body>
      <div>
        <h2>Raincloud Status<h2>
        <p>{state}</p>
      </div>
      <div>
        <button onclick="location.href='/valves/open'" type="button">OPEN</button>
        <button onclick="location.href='/valves/close'" type="button">CLOSE</button>
      </div>
    </body>
  </html>
  """
  return HTMLResponse(content=html_content, status_code=200)