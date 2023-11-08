bl_info = {
    "name": "Camera Linking",
    "description": "Adds the ability to disable/enable visibility of collections based on active camera.",
    "author": "Dylan Alexander",
    "version": (0, 1),
    "blender": (3, 3, 0),  # Blender version compatibility
    "category": "Camera",
    "auto": True
}

import bpy
from bpy.props import BoolProperty

### Visbility Toggling ###

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
                    
### REGISTER & RUN ###

# Registration
def register():
    bpy.app.handlers.depsgraph_update_post.append(add_camera_custom_properties)
    bpy.app.handlers.frame_change_post.append(toggle_visibility)

def unregister():
    if toggle_visibility in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(toggle_visibility)
    if add_camera_custom_properties in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(add_camera_custom_properties)

if __name__ == "__main__":
    register()