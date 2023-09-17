"""
### Blender Midi Simulation Node

## Usage 

Import the script to blender and run it one!

- Then you have the new `MidiSimulationNode`

### Simulatrion node params

Creates a simple midi geometry node group
that accepts the following params

(str) midi_path: Absolute path to midi file
(str) trigger_type: Control or Track
If control the node will create a time dependant float curve based on 

(list<str>) filters: A list of control event types that should be filtered
E.g.: If you want to trigger only on a specify control event type `control_change`

[Optional] control_id: set a filter for a certain control id
> only use with Control tirgger type

[Optional] note_id: Id of the note you want to be filtered
> only use with 'Track' trigger type

"""
import requests
import bpy
import sys
import os

def get_midi_simulation_node():
    """
    Create input and output for simulation zone
    uses:
    - GeometryNodeSimulationInput
    - 
    """
    pass

def create_midi_simulation_node():
    
    node_group = bpy.data.node_groups.new(name="MidiSimulationNode", type="GeometryNodeTree")
    node_group.inputs.new(type = "NodeSocketGeometry", name = "GeometryIn")

    group_input = node_group.nodes.new(type="NodeGroupInput")
    
if __name__ == "__main__":
    
    # Check if running in blender or from vs code
    prefix = "/".join(bpy.app.binary_path.split("/")[:-1]) if bpy.app.binary_path else "//////"
    if sys.executable.startswith(prefix):
        # In blender:
        import bpy
        from mathutils import Euler

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_rotation.rotate(Euler((0, 0, 0.9)))
    else:
        # Not in plender
        script_name = "/home/tim/Data/local/development/tims-blender-tools/create_midi_geometry_node.py"
        requests.post("http://localhost:5000/tasks/", json={
            "task": {
                "script_path": script_name,
                "type": "run_script"
            }})