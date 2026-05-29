"""
assembly_line_monitor.py - AI-powered assembly line anomaly detection.
Replace SimulatedSensorFeed with your actual PLC/SCADA connector.
"""

import asyncio, json, os, random
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import urllib.request

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
STATIONS = ["Station-1", "Station-2", "Station-3", "Station-4", "Station-5"]
BASELINE = {
    "temp_f":     {"min": 750, "max": 820},
    "pressure":   {"min": 28,  "max": 35},
    "vibration":  {"min": 0.5, "max": 2.0},
    "cycle_time": {"min": 3.8, "max": 4.5},
}

@dataclass
class SensorReading:
    station: str; timestamp: str
    temp_f: float; pressure: float; vibration: float; cycle_time: float

@dataclass
class Alert:
    station: str; timestamp: str; level: str
    reasoning: str; action: str; reading: dict

class SimulatedSensorFeed:
    """Replace with your actual PLC/SCADA data connector."""
    def __init__(self, fault_probability: float = 0.15):
        self.fault_probability = fault_probability
    def read(self, station: str) -> SensorReading:
        fault = random.random() < self.fault_probability
        m = random.uniform(1.05, 1.25) if fault else random.uniform(0.98, 1.02)
        return SensorReading(
            station=station, timestamp=datetime.now().isoformat(),
            temp_f=round(785*m + random.uniform(-5,5), 1),
            pressure=round(31.5*(2-m) + random.uniform(-0.5,0.5), 1),
            vibration=round(1.2*m + random.uniform(-0.1,0.1), 2),
            cycle_time=round(4.1*(1+(m-1)*0.5) + random.uniform(-0.1,0.1), 2),
        )

def prefilter(r: SensorReading) -> Optional[str]:
    devs = [k for k, v in [("temp_f",r.temp_f),("pressure",r.pressure),
            ("vibration",r.vibration),("cycle_time",r.cycle_time)]
            if v > BASELINE[k]["max"]*1.20 or v < BASELINE[k]["min"]*0.80]
    return "CRITICAL" if len(devs)>=2 else "WARNING_CANDIDATE" if devs else None

def classify(reading: SensorReading, pre: str) -> dict:
    prompt = (f"Assembly line monitor. Station: {reading.station} | "
              f"Temp: {reading.temp_f}F | Pressure: {reading.pressure}PSI | "
              f"Vibration: {reading.vibration}mm/s | Cycle: {reading.cycle_time}s | "
              f"Pre-filter: {pre}\n"
              'Respond ONLY JSON: {"level":"NORMAL|WARNING|CRITICAL|SHUTDOWN","reasoning":"one sentence","action":"action"}')
    payload = json.dumps({"model":"claude-3-haiku-20240307","max_tokens":100,
        "messages":[{"role":"user","content":prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
        headers={"x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(json.loads(r.read())["content"][0]["text"].strip())
    except Exception:
        return {"level":pre.replace("_CANDIDATE",""),"reasoning":"LLM unavailable","action":"Manual inspection"}

def log_alert(alert: Alert):
    icons = {"WARNING":"!","CRITICAL":"!!","SHUTDOWN":"STOP"}
    print(f"[{alert.timestamp[:19]}] [{icons.get(alert.level,'?')} {alert.level}] "
          f"{alert.station} | {alert.reasoning} | {alert.action}")
    with open("alerts.jsonl","a") as f:
        f.write(json.dumps(asdict(alert))+"\n")

async def monitor_station(station: str, feed: SimulatedSensorFeed, interval: float = 2.0):
    while True:
        reading = feed.read(station)
        pre = prefilter(reading)
        cl = classify(reading, pre) if pre else {"level":"NORMAL","reasoning":"Within baseline","action":"None"}
        alert = Alert(station=reading.station, timestamp=reading.timestamp, level=cl["level"],
                      reasoning=cl["reasoning"], action=cl["action"], reading=asdict(reading))
        if alert.level != "NORMAL": log_alert(alert)
        if alert.level == "SHUTDOWN": print(f"SHUTDOWN: {station}"); return
        await asyncio.sleep(interval)

async def main():
    print(f"Assembly Line AI Monitor | {len(STATIONS)} stations | 15% demo fault rate")
    print("-"*60)
    feed = SimulatedSensorFeed(fault_probability=0.15)
    await asyncio.gather(*[monitor_station(s, feed) for s in STATIONS])

if __name__ == "__main__":
    asyncio.run(main())
