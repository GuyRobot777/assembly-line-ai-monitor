# Assembly Line AI Monitor

Autonomous AI monitoring agent for assembly line quality control.
Ingests sensor data, classifies anomalies with an LLM, triggers structured alerts.

## Architecture
```
Sensor Feed (simulated / PLC-SCADA)
    |
Pre-filter (rule-based, fast)
    |
LLM Classification Agent (Claude - contextual reasoning)
    |
Alert Router -> [Log | Notify | Escalate | Shutdown]
```

## What It Does
- Monitors temperature, pressure, vibration, cycle time across 5 stations concurrently
- Rule-based pre-filter catches obvious out-of-range readings instantly
- Escalates ambiguous readings to Claude for intelligent contextual classification
- Classifies as: NORMAL / WARNING / CRITICAL / SHUTDOWN
- Logs structured JSONL alerts with full audit trail

## Sample Output
```
[2026-05-28 14:32:01] [! WARNING] Station-3 | Thermal creep, 12% above baseline | Inspect within 2 cycles
[2026-05-28 14:32:05] [!! CRITICAL] Station-1 | Multiple params out of range | Halt station immediately
```

## Stack
- Python 3.11+ asyncio
- Anthropic API (claude-3-haiku - fast, low-cost classification)
- JSONL structured logging

## Usage
```bash
export ANTHROPIC_API_KEY=your_key
python monitor.py
```

## Real-World Extension
Replace `SimulatedSensorFeed` with your PLC/SCADA connector.
Train on historical fault data to improve classification accuracy.
