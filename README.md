## Tim's blender Tools

I like code I hate using mouse. Blenders script editor sucks.
I can't blender yet, so I'll just script I bet.

Random tools from a guy that tries to learn blender through scripting only.

### Script usage:

Have the server running in the background

```
python3 server.py
```

Load `blender_update_operator.py` into your blender project and run it.

Now by using the following entry check the script when run is either automaticly relayed to the task server OR it is run from within blender.

```python
if __name__ == "__main__":
    
    # Check if running in blender or from vs code
    prefix = "/".join(bpy.app.binary_path.split("/")[:-1]) if bpy.app.binary_path else "//////"
    if sys.executable.startswith(prefix):
        pass
    else:
        # Not in plender
        script_name = "<path to your script>"
        requests.post("http://localhost:5000/tasks/", json={
            "task": {
                "script_path": script_name,
                "type": "run_script"
            }})

```

> e.g.: simply run the script in vscode by pressing the run-in-terminal button in the upper right corner

### Blender Communicator

A simple bridge to relay any tasks to a running blender instance.

> I made this so I can develop from any code editor and trigger script execution from any terminal in an open blender instance

1. create a timing modal operator that fetches tasks form a local webserver every second
2. create a local webserver that holds and relays a task queue to bender
3. have some api in the local server that allows adding and removing tasks for the queue.

#### Usage

1. Run `python3 server.py` anywher on you system to start the communication server
2. import `blender_update_operator.py` to you current blender project and run it. This start the task listener in the background
3. Push a task to the server task queue by calling `POST /tasks/` e.g.: see `relay_to_blender.py`

