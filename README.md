## Tim's blender Tools

I like code I hate using mouse. Blenders script editor sucks.
I can't blender yet, so I'll just script I bet.

Random tools from a guy that tries to learn blender through scripting only.

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

