import bpy
from bpy.props import IntProperty, FloatProperty
import requests
import time


def execute_task(task):
    print("Executing task: ", task)
    if task["type"] == "run_script":
        filename = task["script_path"]
        try:
            exec(compile(open(filename).read(), filename, 'exec'))
        except Exception as e:
            print("Error while executing script: ", e)

    
class ModalOperator(bpy.types.Operator):
    """
    Tim's Blender socker communicator
    """
    
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Tim's Blender BUS"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    
    prev_time = None

    def modal(self, context, event):
        
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.prev_time is None:
                self.prev_time = time.time()
            else:
                passed_time = abs(self.prev_time - time.time())
                if passed_time > 1.0:
                    self.prev_time = time.time()
                    response = requests.get('http://localhost:5000/tasks/')
                    tasks = response.json()
                    if len(tasks) > 0:
                        print("NEW TASK DETECTED")
                        for task in tasks:
                            execute_task(task)

        return {'PASS_THROUGH'}
    
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
    
def menu_func(self, context):
    self.layout.operator(ModalOperator.bl_idname, text=ModalOperator.bl_label)
    


def register():
    
    bpy.utils.register_class(ModalOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ModalOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
    
    print("Starting modal operator, press ESC to quit.")
    bpy.ops.wm.modal_timer_operator()
