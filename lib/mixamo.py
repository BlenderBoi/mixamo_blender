import bpy
from .bones_pose import *
from .bones_data import *
from ..definitions import naming

def get_mixamo_prefix():    
    p = ""
    rig = bpy.context.active_object    
    
    if 'mixamo_prefix' in rig.data.keys():
        p = rig.data["mixamo_prefix"]
        
    else:     
        for dbone in rig.data.bones:
            if dbone.name.startswith("mixamorig") and ':' in dbone.name:
                p = dbone.name.split(':')[0]+':'
                break
        
        try:
            rig.data["mixamo_prefix"] = p
        except:# context error
            pass
    
    return p
    
    
def get_mix_name(name, use_prefix):
    if not use_prefix:
        return name
    else:        
        p = get_mixamo_prefix()
        return p+name
            
            
def get_bone_side(bone_name):
    if bone_name.endswith("_Left"):
        return "Left"
    elif bone_name.endswith("_Right"):
        return "Right"