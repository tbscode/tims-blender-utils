import bpy
from mido import MidiFile
mid = MidiFile('/home/tim/Data/local/development/blender_experiments/cc_test.mid')

def filter_tracks_for_control(timeline, control_node=1):
    out = []
    end_time = 0
    for event in timeline:
        end_time += event.time
        if (event.type == "control_change") and (event.control == control_node):
            out.append(event)
            
    return out, end_time
    
print(mid.tracks)
midi_track = mid.tracks[0]
midi_tracks_controlls, midi_end_time = filter_tracks_for_control(midi_track, 1)

print("MIDI end time", midi_end_time)

def attach_midi_animation_to_scene_obj(obj_name):
    obj = bpy.data.objects[obj_name]

    print(obj)

    def find_animation_modifier(scene_obj):
        for gnmod in scene_obj.modifiers:
            if gnmod.type == "NODES":
                print(f"TBS: {gnmod.name}")
                if gnmod.name.startswith("MIDI_"):
                    return gnmod.name
            else:
                continue
        return None
            
    current_animation_node = find_animation_modifier(obj)
    
    # If the annimation geometry node doesn't exist we create and attach it
    if current_animation_node is None:
        # Then we create a new geomerty node modifier
        animation_node_name = f"MIDI_{obj_name}"
        gnmod = obj.modifiers.new(animation_node_name, "NODES")
        node_group_name = f"MIDI_{obj_name}_nodegroup"
        
        node_group = bpy.data.node_groups.new(name=node_group_name, type="GeometryNodeTree")
        gnmod.node_group = node_group
        current_animation_node = animation_node_name
        
        node_group.inputs.new(type = "NodeSocketGeometry", name = "GeometryIn")
        node_group.outputs.new(type = "NodeSocketGeometry", name = "GeometryOut") 
        # Now we created the modifier and the GeometryNodeTree
        # Next we need to add Input and Output Nodes
        
        group_input = node_group.nodes.new(type="NodeGroupInput")
        group_output = node_group.nodes.new(type="NodeGroupOutput")
        group_output.is_active_output = True
        print("TBS ", dir(node_group), node_group.active_output, node_group.inputs, node_group.outputs)
        
        float_curve = node_group.nodes.new(type="ShaderNodeFloatCurve")
        
        node_group.links.new(
            group_input.outputs[0],
            group_output.inputs[0]
        )
        
        step_dist = 0.1
        
        bpy.context.view_layer.update()

        total_time = 0
        for event in midi_tracks_controlls:
            total_time += event.time
            
        # Now we create scaled event times from 0.0 to 1.0
        scaled_events = []
        st = 0.0
        for event in midi_tracks_controlls:
            st += float(event.time) / float(total_time)
            _scaled = {
                "time": st,
                "value": float(event.value) / 128.0
            }
            print(_scaled)
            scaled_events.append(_scaled)
            float_curve.mapping.curves[0].points.new(_scaled["value"], _scaled["time"])
            float_curve.mapping.curves[0].points[-1].handle_type = 'VECTOR'
        print(scaled_events)
        float_curve.mapping.update()
        
    else:
        # If The geometry script node already exists we *only* update the FloatCurve
        pass # TODO:
            
    # get the current float curve
    # ...
        
attach_midi_animation_to_scene_obj('Cube')

for group in bpy.data.node_groups:
    print("TBS type", group.type)