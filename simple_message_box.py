import bpy

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


#Shows a message box with a specific message 
ShowMessageBox("This is a message") 

#Shows a message box with a message and custom title
ShowMessageBox("This is a message", "This is a custom title")

#Shows a message box with a message, custom title, and a specific icon
ShowMessageBox("This is a message", "This is a custom title", 'ERROR')