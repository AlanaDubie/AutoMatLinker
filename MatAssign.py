import maya.cmds as cmds
import os
import re

def assign_basecolor_shader():
    selection = cmds.ls(selection=True, dag=True, long=True, type="transform")

    if not selection:
        cmds.confirmDialog(title="Warning", message="No mesh selected!", button=["OK"], defaultButton="OK")
        return

    # Get the first selected mesh
    obj = selection[0]
    mesh_name = obj.split("|")[-1]  # remove DAG path if present
    print(f"Selected mesh: {mesh_name}")
    mesh_name = strip_trailing_number(mesh_name) # Strip trailing numbers like _01, _02 in mesh name

    # Create maya's built in standard surface shader node
    shader_name = cmds.shadingNode("standardSurface", asShader=True, name="autoMat_shader")

    # Create a shading group for the shader
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader_name}SG")
    cmds.connectAttr(f"{shader_name}.outColor", f"{shading_group}.surfaceShader", force=True)

    # Assign the shading group to the selected object
    cmds.sets(obj, edit=True, forceElement=shading_group)
    print(f"Shader '{shader_name}' assigned to: {obj}")

    # file path for textures
    file_dir = r"C:\Users\littl\OneDrive\Desktop\AlanaMaya\chess_set_4k.fbx\textures"
    
    # Try exact texture name first
    texture_name = f"{mesh_name}_baseColor.png"
    texture_path = os.path.join(file_dir, texture_name)
    print(f"Looking for texture: {texture_path}")

    if not os.path.exists(texture_path):
        print(f"single texture not found, trying shared: {texture_path}")

        # If exact texture not found, try shared textures
        texture_path = find_shared_texture(mesh_name, file_dir)
        if texture_path:
            print(f"Found Shared textured: {texture_path}")
        else:
            print(f"⚠️ No texture found for mesh: {mesh_name}")
    else:
        print(f"Found texture: {texture_path}")

    # Create file texture node and connect to shader's baseColor
    file_node = cmds.shadingNode("file", asTexture=True, name=f"{mesh_name}_file")
    cmds.setAttr(f"{file_node}.fileTextureName", texture_path, type="string")
    cmds.connectAttr(f"{file_node}.outColor", f"{shader_name}.baseColor", force=True)

    print(f"✅ Connected texture '{texture_path}' to {shader_name}.baseColor")

def find_shared_texture(mesh_name, texture_dir):
    keywords = mesh_name.split('_')

    # !could optimize later
    shared_textures = []
    for file_name in os.listdir(texture_dir):
        if file_name.startswith("shared_"):
            # If ANY of the keywords are inside the file name, return this file
            if any(word in file_name for word in keywords):
                return os.path.join(texture_dir, file_name)

    # Step 4: If nothing matched, return None to say "no shared texture found"
    return "No shared texture found!"

def strip_trailing_number(name):
    # Remove trailing underscore + digits (e.g. _01, _12)
    return re.sub(r'_\d+$', '', name)