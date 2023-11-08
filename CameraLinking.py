bl_info = {
    "name": "Camera Linking",
    "description": "Control visibility of collections based on active camera.",
    "author": "Dylan Alexander",
    "version": (0, 3),
    "blender": (3, 3, 0),  # Blender version compatibility
    "category": "Camera",
    "auto": True
}

import bpy
from bpy.props import BoolProperty
from bpy.app.handlers import persistent

### Visbility Toggling ###
@persistent
def toggle_visibility(dummy):

    camera_names = [obj.name for obj in bpy.data.objects if obj.type == 'CAMERA']

    # 1. Loop through all collections
    for collection in bpy.data.collections:
        # Define the list of custom properties to check for
        custom_properties_to_check = camera_names  # Update with your custom property names

        # 2. Compare custom property names with the name of the active camera
        if bpy.context.scene.camera:
            active_camera_name = bpy.context.scene.camera.name

            # Check if any of the custom properties are set to True
            any_property_true = any(collection.get(key) and key == active_camera_name for key in custom_properties_to_check)

            # 3. Change visibility of the collection
            if any_property_true:
                collection.hide_viewport = False
                collection.hide_render = False
            else:
                collection.hide_viewport = True
                collection.hide_render = True
        else:
            collection.hide_viewport = True
            collection.hide_render = True

# Function to add custom properties to collections
@persistent
def add_camera_custom_properties(dummy):
    # Get the list of cameras in the scene
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]

    # Iterate over the cameras and their names
    for camera in cameras:
        camera_name = camera.name

        # Iterate over all collections
        for collection in bpy.data.collections:
            # Check if the custom property with the camera's name doesn't exist
            if camera_name not in collection:
                # Add a custom property with the camera's name and set it as a boolean
                collection[camera_name] = True
        
        # Iterate over all collections again to check and delete custom properties
        for collection in bpy.data.collections:
            for prop_name in collection.keys():
                if prop_name not in [camera.name for camera in cameras]:
                    del collection[prop_name]
                    
### UI ###

class CustomCategory(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Camera Linking", default="Camera Linking")

bpy.utils.register_class(CustomCategory)
bpy.types.Scene.my_custom_category = bpy.props.PointerProperty(type=CustomCategory)


# Define a Panel for the Properties Editor
class CustomPropertiesPanel(bpy.types.Panel):
    bl_label = "Camera Linking"
    bl_idname = "PT_CustomPropertiesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Camera Linking'

    def draw(self, context):
        layout = self.layout

        # Get the selected object
        obj = context.object
        if obj is not None:
            collection = obj.users_collection[0]
            collection_name = collection.name

            # Check if the selected collection has custom properties
            if collection_name in bpy.data.collections:
                custom_props = bpy.data.collections[collection_name].items()

                # Create a column for custom properties
                column = layout.column()
                column.label(text=f"{collection_name}:")

                for prop_name, prop_value in custom_props:
                    # Create a row for each custom property
                    row = layout.row()

                    # Add a checkbox
                    row.prop(bpy.data.collections[collection_name], f'["{prop_name}"]', text='', toggle=True)

                    # Add the custom property name and value
                    row.label(text=prop_name)
                    row.prop(bpy.data.collections[collection_name], prop_name)

                    
### REGISTER & RUN ###

# Registration
def register():
    bpy.utils.register_class(CustomPropertiesPanel)
    bpy.app.handlers.depsgraph_update_post.append(add_camera_custom_properties)
    bpy.app.handlers.frame_change_post.append(toggle_visibility)

def unregister():
    bpy.utils.unregister_class(CustomPropertiesPanel)
    if toggle_visibility in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(toggle_visibility)
    if add_camera_custom_properties in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(add_camera_custom_properties)

if __name__ == "__main__":
    register()