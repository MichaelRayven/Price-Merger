import json
import os


def load_json(path):
    try:
        with open(os.path.abspath(path), "r") as file:
            data = json.loads(file.read())
            return data
    except Exception as err:
        print(err)
        return None
    
def save_json(path, content):
    try:
        with open(os.path.abspath(path), "w") as file:
            file.write(json.dumps(content))
            return True
    except Exception as err:
        print(err)
        return False