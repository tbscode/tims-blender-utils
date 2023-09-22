import requests
import bpy
import sys
import os

            
def slightly_rotate_camera():
    import bpy
    from mathutils import Euler

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_rotation.rotate(Euler((0, 0, 0.3)))

def clear_prev(scene):
    for obj in scene.objects:
        if obj.name.startswith("KEY_"):
            obj.select_set(True)
            bpy.ops.object.delete() 
        else:
            obj.select_set(False)
            
    
def create_key(
        id=0,
        padding=0.1,
    ):

    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = bpy.context.object
    cube.scale = (2, 1, 0.4)
    cube.name = f"KEY_{id}"
    width = cube.dimensions[0]
    
    if id != 0:
        cube.location[1] = width * id + padding * id
    
    return cube
    

if __name__ == "__main__":
    
    # Check if running in blender or from vs code
    prefix = "/".join(bpy.app.binary_path.split("/")[:-1]) if bpy.app.binary_path else "//////"
    if sys.executable.startswith(prefix):
        # In blender:
        scene = bpy.context.scene
        clear_prev(scene)
        slightly_rotate_camera()
        #create_key(id=0)
        key1 = create_key(id=0)
        slightly_rotate_camera()
        key2 = create_key(id=1)
        slightly_rotate_camera()
    else:
        # Not in plender
        script_name = "/home/tim/Data/local/development/tims-blender-tools/generate_keyboard_keys.py"
        requests.post("http://localhost:5000/tasks/", json={
            "task": {
                "script_path": script_name,
                "type": "run_script"
            }})