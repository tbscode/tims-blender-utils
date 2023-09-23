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
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
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
        
    # Make sure the object is selected and is the active object
    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube

    # Apply transformations
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
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
    from mido import MidiFile
    import mido

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
    
    # Delete previous versions of the nodegoup
    for ng in bpy.data.node_groups:
        if ng.name.startswith("MidiNodeHandler"):
            bpy.data.node_groups.remove(ng)
    
    # Create the simple node group
    geometry_nodes = bpy.data.node_groups.new(type='GeometryNodeTree',name="MidiNodeHandler")
    geometry_nodes.inputs.new('NodeSocketFloat', "Total Frames")

    geometry_nodes.inputs[0].default_value = float(midi_info["ticks"])
    geometry_nodes.inputs[0].attribute_domain = 'POINT'
    
    group_input = geometry_nodes.nodes.new("NodeGroupInput")
    group_output = geometry_nodes.nodes.new("NodeGroupOutput")
    # Now we also need a simple scene time note to output the scene time dependant midi value
    scene_time = geometry_nodes.nodes.new("GeometryNodeInputSceneTime")
    
    math = geometry_nodes.nodes.new("ShaderNodeMath")
    math.operation = 'DIVIDE'
    math.inputs[2].default_value = 0.5
    
    # Link the scene time and the total time to the math node
    geometry_nodes.links.new(
        scene_time.outputs[1],
        math.inputs[0]
    )
    geometry_nodes.links.new(
        group_input.outputs[0],
        math.inputs[1]
    )

    # Now In oder to determine which outputs wee need we need to first analyze the midi file
    # For that we basicly need to consider all 'note_on' and 'note_off' events
    TOTAL_TICKS = float(midi_info["ticks"])
    TRACK = 1
    points_by_note = {}
    time = 0
    for event in mid.tracks[TRACK]:
        print("EV", event)
        if event.type in ["note_on", "note_off"]:
            
            time += event.time
            
            if event.note not in points_by_note:
                points_by_note[event.note] = []
            points_by_note[event.note].append({
                "time": float(time) / TOTAL_TICKS,
                "velocity": float(event.velocity) / 128.0,
            })
            
    #print("TBS", "\n", points_by_note, mid.tracks[0])
    
    # Now for every note we create a float curve and an output
    for note in points_by_note:
        # First create the float curve
        float_curve = geometry_nodes.nodes.new(type="ShaderNodeFloatCurve")
        for point in points_by_note[note]:
            float_curve.mapping.curves[0].points.new(point["time"], point["velocity"])
            
        for point in float_curve.mapping.curves[0].points:
            point.handle_type = 'VECTOR'
        float_curve.mapping.update()
        
        # Then create the output node
        output_name = f"NOTE_{note}"
        geometry_nodes.outputs.new('NodeSocketFloat', output_name)
        geometry_nodes.outputs[-1].attribute_domain = 'POINT'
        
        # Then link the nodes match note to float curve input
        geometry_nodes.links.new(
            math.outputs[0],
            float_curve.inputs[1]
        )
        
        # And the float curve output to the newly created output socket
        geometry_nodes.links.new(
            float_curve.outputs[0],
            group_output.inputs[output_name]
        )
        
    return {
        "notes": list(points_by_note.keys())
    }

def attach_geonode_modifier_to_key(key, id):
    geo_nodes_modifier = key.modifiers.new(name=f"key_{id}_geonode", type='NODES')
    
    
    geo_nodes = bpy.data.node_groups.new(type='GeometryNodeTree',name="KEY_MODIFIER_{}".format(id))

    g_input = geo_nodes.inputs.new(type="NodeSocketGeometry",name="Geometry")
    g_output = geo_nodes.outputs.new(type="NodeSocketGeometry",name="Geometry")
    
    group_input = geo_nodes.nodes.new("NodeGroupInput")
    group_output = geo_nodes.nodes.new("NodeGroupOutput")
    
    midi_group_node = geo_nodes.nodes.new('GeometryNodeGroup')
    midi_group_node.node_tree = bpy.data.node_groups["MidiNodeHandler"]
    
    # The object position
    position = geo_nodes.nodes.new("GeometryNodeInputPosition")
    
    # get only Y and Z
    seperate_xyz = geo_nodes.nodes.new("ShaderNodeSeparateXYZ")

    # combine Y and Z with the X from the midi_group_node
    combine_xyz = geo_nodes.nodes.new("ShaderNodeCombineXYZ")
    
    geo_nodes.links.new(
        midi_group_node.outputs[f"NOTE_{id}"],
        combine_xyz.inputs[0]
    )
    
    geo_nodes.links.new(
        position.outputs[0],
        seperate_xyz.inputs[0]
    )
    
    geo_nodes.links.new(
        seperate_xyz.outputs[1],
        combine_xyz.inputs[1]
    )
    
    geo_nodes.links.new(
        seperate_xyz.outputs[2],
        combine_xyz.inputs[2]
    )
    
    set_pos_node = geo_nodes.nodes.new("GeometryNodeSetPosition")
    
    geo_nodes.links.new(
        group_input.outputs[0], 
        set_pos_node.inputs[0]
    )

    geo_nodes.links.new(
        combine_xyz.outputs[0],
        set_pos_node.inputs[2]
    )
    
    geo_nodes.links.new(
        set_pos_node.outputs[0],
        group_output.inputs[0]
    )
    
    # set the nodegroup modifier
    geo_nodes_modifier.node_group = geo_nodes
    

    

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
        midi_node_info = generate_midi_node(mid, midi_info)
        
        bpy.context.scene.frame_end = int(60.0 * float(midi_info["length"]))
        
        
        for ng in bpy.data.node_groups:
            if ng.name.startswith("KEY_MODIFIER_"):
                bpy.data.node_groups.remove(ng)
        
        # Now we can add a modifier to all the keys
        for i, key in enumerate(keys):
            if i in midi_node_info["notes"]:
                attach_geonode_modifier_to_key(key, i)

        #attach_geonode_modifier_to_key(keys[84], 84)
    else:
        # Not in plender
        script_name = "/home/tim/Data/local/development/tims-blender-tools/generate_keyboard_keys.py"
        requests.post("http://localhost:5000/tasks/", json={
            "task": {
                "script_path": script_name,
                "type": "run_script"
            }})