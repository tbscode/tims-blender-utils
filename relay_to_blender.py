import requests


script_name = "/home/tim/Data/local/development/tims-blender-tools/simple_message_box.py"
requests.post("http://localhost:5000/tasks/", json={
    "task": {
        "script_path": script_name,
        "type": "run_script"
    }})