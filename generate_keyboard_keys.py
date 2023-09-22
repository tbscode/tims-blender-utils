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

    # 1. First we create the keyboard key
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = bpy.context.object
    cube.scale = (2, 1, 0.4)
    cube.name = f"KEY_{id}"
    width = cube.dimensions[0]
    
    if id != 0:
        cube.location[1] = width * id + padding * id
        
    # 2. Then we create the ID help annotation
    text_data = f"Key: {id}"
    text_object = bpy.data.objects.new("Text", bpy.data.curves.new(name="Text", type="FONT"))
    bpy.context.collection.objects.link(text_object)
    text_object.select_set(True)
    bpy.context.view_layer.objects.active = text_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.font.delete()
    bpy.ops.font.text_insert(text=text_data)
    bpy.ops.object.editmode_toggle()
    text_object.name = f"KEY_{id}_ID"

    if id != 0:
        text_object.location[1] = width * id + padding * id
    text_object.location[0] = -0.5
    
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
        
        keys = []
        for i in range(0, 100):
            keys.append(create_key(id=i))
            slightly_rotate_camera()
    else:
        # Not in plender
        script_name = "/home/tim/Data/local/development/tims-blender-tools/generate_keyboard_keys.py"
        requests.post("http://localhost:5000/tasks/", json={
            "task": {
                "script_path": script_name,
                "type": "run_script"
            }})