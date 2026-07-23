import json
def save_state(filepath: str, data: dict):
    with open(filepath, 'w') as f:
        json.dump(data, f)
