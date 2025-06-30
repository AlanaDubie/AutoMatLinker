import maya.cmds as cmds
import os
import re

# texture types config, TODO: config json file
TEXTURE_TYPES = {
    "baseColor": {
        "aliases": ["baseColor", "albedo", "diff", "diffuse"],
        "shaderAttr": "baseColor",
        "colorSpace": "sRGB",
        "outputAttr": "outColor", 
    },
    "normal": {
        "aliases": ["normal", "nrm"],
        "shaderAttr": "normalCamera",
        "colorSpace": "Raw",
        "outputAttr": "outAlpha",  
        "node": "bump2d",         # middle node(s) between file and shader
        "nodeInput": "bumpValue",  # input attribute of the middle node
        "nodeOutput": "outNormal"
    },
    "roughness": {
        "aliases": ["roughness", "rough"],
        "shaderAttr": "specularRoughness",
        "colorSpace": "Raw",
        "outputAttr": "outAlpha",
        "node": "remapValue",  
        "nodeInput": "inputValue",
        "nodeOutput": "outValue"
    },
}

def assign_texture():
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
    file_dir = r"C:\Users\littl\OneDrive\Desktop\AlanaMaya\chess_textures"
    
    for texture_type, config in TEXTURE_TYPES.items():
        found_texture = find_texture(mesh_name, file_dir, config['aliases'])
        print(f"Found {texture_type} texture: {found_texture}")

        if not found_texture:
            print(f"⚠️ No {texture_type} texture found for mesh: {mesh_name}")
            continue

        # Create file texture node and connect to shader's corresponding attribute
        file_node = cmds.shadingNode("file", asTexture=True, name=f"{texture_type}_file")
        cmds.setAttr(f"{file_node}.fileTextureName", f"{found_texture}", type="string")
        # Set color space for the texture
        cmds.setAttr(f"{file_node}.colorSpace", config["colorSpace"], type="string")

        # Connect place2dTexture node
        connect_place2d(file_node)

        # Connect to shader, handles texture types and their specific attributes (bump2d, etc)
        connect_texture(file_node, shader_name, config, texture_type)
        print(f"✅ Connected '{found_texture}' to '{shader_name}.{config['shaderAttr']}'")

def find_texture(mesh_name, texture_dir, aliases):
    """
    Find the texture file for the given mesh name and aliases.
    
    Args:        
        mesh_name (str): The name of the mesh.
        texture_dir (str): The directory where textures are stored.
        aliases (list): List of aliases to search for in the texture file names.

        Returns:
        str: The path to the texture file if found, otherwise None.
    """
    for alias in aliases:
        texture_name = f"{mesh_name}_{alias}.png"
        texture_path = os.path.join(texture_dir, texture_name)

        if os.path.exists(texture_path):
            return texture_path

    return find_shared_texture(mesh_name, texture_dir, aliases)

def connect_place2d(file_node):
    place2d = cmds.shadingNode("place2dTexture", asUtility=True, name=f"{file_node}_place2d")
    cmds.connectAttr(f"{place2d}.outUV", f"{file_node}.uvCoord", force=True)
    cmds.connectAttr(f"{place2d}.outUvFilterSize", f"{file_node}.uvFilterSize", force=True)

    attrs = ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV",
             "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV"]
    for attr in attrs:
        cmds.connectAttr(f"{place2d}.{attr}", f"{file_node}.{attr}", force=True)


def strip_trailing_number(name):
    # Remove trailing underscore + digits (e.g. _01, _12)
    return re.sub(r'_\d+$', '', name)

def find_shared_texture(mesh_name, texture_dir, aliases):
    keywords = mesh_name.split('_')
    best_match = None
    highest_match_count = 0

    # !could optimize later    
    for file_name in os.listdir(texture_dir):

        if not file_name.startswith("shared_"):
            continue

        
        if not any(alias in file_name for alias in aliases):
            continue

        match_count = sum(1 for word in keywords if word in file_name)
        if match_count > highest_match_count:
            highest_match_count = match_count
            best_match = file_name

    if best_match:
        return os.path.join(texture_dir, best_match)
    #  If nothing matched,"no shared texture found"
    return "No shared texture found!"

# Function to assign normal map, roughness, along with specical node attribute (bump2d)
def connect_texture(file_node, shader_name, config, texture_type):
    
    if "node" in config:
        mid_node = cmds.shadingNode(config["node"], asUtility=True, name=f"{texture_type}_{config['node']}")
        cmds.connectAttr(f"{file_node}.{config['outputAttr']}", f"{mid_node}.{config['nodeInput']}", force=True)

        # Special case: Set bump2d mode to Tangent Space Normals for normal maps
        if texture_type == "normal":
            cmds.setAttr(f"{mid_node}.bumpInterp", 1)

        cmds.connectAttr(f"{mid_node}.{config['nodeOutput']}", f"{shader_name}.{config['shaderAttr']}", force=True)
        print(f"🔁 Connected '{file_node}' → {mid_node} → {shader_name}.{config['shaderAttr']}")
    else:
        cmds.connectAttr(f"{file_node}.{config['outputAttr']}", f"{shader_name}.{config['shaderAttr']}", force=True)
        print(f"✅ Connected '{file_node}' to '{shader_name}.{config['shaderAttr']}'")
