import json, logging
from typing import Optional
from urllib import request
from urllib.error import URLError

logger = logging.getLogger(__name__)
_LHM_URL = "http://localhost:8085/data.json"
_TIMEOUT = 2

def _walk(node, sensor_type, results):
    for child in node.get("Children", []):
        if child.get("Text", "").strip() == sensor_type:
            for leaf in child.get("Children", []):
                try:
                    val = float(leaf.get("Value", "").split()[0])
                    results.append({"name": leaf.get("Text", ""), "value": val})
                except (ValueError, IndexError):
                    pass
        else:
            _walk(child, sensor_type, results)

def _fetch(category):
    try:
        with request.urlopen(_LHM_URL, timeout=_TIMEOUT) as r:
            data = json.loads(r.read().decode())
        results = []
        _walk(data, category, results)
        return results
    except Exception as e:
        logger.debug("LHM fetch error: %s", e)
        return []

def is_lhm_available():
    return len(_fetch("Temperatures")) > 0

def get_cpu_temp():
    sensors = _fetch("Temperatures")
    if not sensors:
        return None
    # Intel: "CPU Package"
    for s in sensors:
        if "cpu package" in s["name"].lower():
            return round(s["value"], 1)
    # AMD: "Core (Tctl/Tdie)" — primary AMD die temperature
    for s in sensors:
        if "tctl" in s["name"].lower() or "tdie" in s["name"].lower():
            return round(s["value"], 1)
    # Any sensor with "cpu" in name
    for s in sensors:
        if "cpu" in s["name"].lower():
            return round(s["value"], 1)
    # Fallback: first temperature sensor in list
    return round(sensors[0]["value"], 1)

def get_gpu_temp():
    sensors = _fetch("Temperatures")
    if not sensors:
        return None
    for s in sensors:
        name = s["name"].lower()
        if "gpu core" in name:
            return round(s["value"], 1)
    for s in sensors:
        if "gpu" in s["name"].lower():
            return round(s["value"], 1)
    return None

def get_fan_rpms():
    # ASUS FA506QM fan is EC-locked — LHM cannot read it.
    # Returning None, None so watcher falls back to WMI/psutil.
    sensors = _fetch("Fan")
    if not sensors:
        return None, None
    cpu_rpm = gpu_rpm = None
    for s in sensors:
        name = s["name"].lower()
        rpm  = int(round(s["value"]))
        if "gpu" in name:
            if gpu_rpm is None: gpu_rpm = rpm
        elif cpu_rpm is None:
            cpu_rpm = rpm
        elif gpu_rpm is None:
            gpu_rpm = rpm
    return cpu_rpm, gpu_rpm
