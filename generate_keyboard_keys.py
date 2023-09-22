import requests
import bpy
import sys
import os
from mido import MidiFile
import mido

            
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

def process_midi_file():

    mid = MidiFile('/home/tim/Data/local/development/tims-blender-tools/for_elise_by_beethoven.mid')
    tempo_event = [msg.tempo for msg in mid.tracks[0] if msg.type == 'set_tempo']

    if tempo_event:
        tempo = tempo_event[0]
    else:
        tempo = 500000  # Default value if not in the MIDI

    BPM = mido.tempo2bpm(tempo)

    total_ticks = sum(sum(msg.time for msg in track) for track in mid.tracks)

    length_in_seconds = mido.tick2second(total_ticks , mid.ticks_per_beat, tempo)

    print("Tempo: {} BPM".format(BPM))
    print("Length: {} seconds".format(length_in_seconds))
    
    return mid, {
        "tempo": BPM,
        "length": length_in_seconds,
        "ticks": total_ticks,
    }

def generate_midi_node(mid, midi_info):
    
    # Create the simple node group
    geometry_nodes = bpy.data.node_groups.new(type='GeometryNodeTree',name="MidiNodeHandler")
    geometry_nodes.inputs.new('NodeSocketFloat', "Total Time")
    geometry_nodes.inputs[0].default_value = 0.0 # TODO: calculate the total time from the midi file and put it here
    geometry_nodes.inputs[0].attribute_domain = 'POINT'
    
    group_input = geometry_nodes.nodes.new("NodeGroupInput")
    # Now we also need a simple scene time note to output the scene time dependant midi value
    scene_time = geometry_nodes.nodes.new("GeometryNodeInputSceneTime")
    
    math = geometry_nodes.nodes.new("ShaderNodeMath")
    math.operation = 'DIVIDE'
    math.inputs[2].default_value = 0.5
    
    

    # Now In oder to determine which outputs wee need we need to first analyze the midi file
    # For that we basicly need to consider all 'note_on' and 'note_off' events
    TOTAL_TICKS = float(midi_info["ticks"])
    TRACK = 0
    points_by_note = {}
    for event in mid.tracks[TRACK]:
        if event.type in ["note_on", "note_off"]:
            
            if event.note not in points_by_note:
                points_by_note[event.note] = []
            points_by_note[event.note].append({
                "time": float(event.time) / TOTAL_TICKS,
                "velocity": float(event.velocity) / 128.0,
            })
    notes_used = list(points_by_note.keys())
    
    # Now for every note we create a float curve and an output


    

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
            
        mid, midi_info = process_midi_file()
        generate_midi_node(mid, midi_info)
    else:
        # Not in plender
        script_name = "/home/tim/Data/local/development/tims-blender-tools/generate_keyboard_keys.py"
        requests.post("http://localhost:5000/tasks/", json={
            "task": {
                "script_path": script_name,
                "type": "run_script"
            }})