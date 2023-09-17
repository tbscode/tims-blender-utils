import bpy
from bpy.props import IntProperty, FloatProperty
import requests


class ModalOperator(bpy.types.Operator):
    """
    Tim's Blender socker communicator
    """
    
    bl_idname = "object.modal_operator"
    bl_label = "Tim's Blender BUS"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()

    def modal(self, context, event):
        
        if event.type in {'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # Always fetch the dev server `localhost:8128/tasks`
        
        response = requests.post('http://localhost:8128/tasks')
        print(response.json())

        
        return {'RUNNING_MODAL'}


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

    bpy.ops.object.modal_operator('INVOKE_DEFAULT')