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

def get_midi_simulation_node():
    pass

def create_midi_simulation_node():
    pass