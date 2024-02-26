import bpy
from .version import blender_version


def get_prop_setting(node, prop_name, setting):
    if blender_version._float >= 300:
        return node.id_properties_ui(prop_name).as_dict()[setting]
    else:
        return node['_RNA_UI'][prop_name][setting]


def set_prop_setting(node, prop_name, setting, value):
    if blender_version._float >= 300:
        ui_data = node.id_properties_ui(prop_name)
        if setting == 'default':
            ui_data.update(default=value)
        elif setting == 'min':
            ui_data.update(min=value)
        elif setting == 'max':
            ui_data.update(max=value)     
        elif setting == 'soft_min':
            ui_data.update(soft_min=value)
        elif setting == 'soft_max':
            ui_data.update(soft_max=value)
        elif setting == 'description':
            ui_data.update(description=value)
            
    else:
        if not "_RNA_UI" in node.keys():
            node["_RNA_UI"] = {}   
        node['_RNA_UI'][prop_name][setting] = value
        

def create_custom_prop(node=None, prop_name="", prop_val=1.0, prop_min=0.0, prop_max=1.0, prop_description="", soft_min=None, soft_max=None, default=None):
    if soft_min == None:
        soft_min = prop_min
    if soft_max == None:
        soft_max = prop_max
    
    if blender_version._float < 300:
        if not "_RNA_UI" in node.keys():
            node["_RNA_UI"] = {}    
    
    node[prop_name] = prop_val    
    
    if default == None:
        default = prop_val
    
    if blender_version._float < 300:
        node["_RNA_UI"][prop_name] = {'use_soft_limits':True, 'min': prop_min, 'max': prop_max, 'description': prop_description, 'soft_min':soft_min, 'soft_max':soft_max, 'default':default}
    else:     
        set_prop_setting(node, prop_name, 'min', prop_min)
        set_prop_setting(node, prop_name, 'max', prop_max)
        set_prop_setting(node, prop_name, 'description', prop_description)
        set_prop_setting(node, prop_name, 'soft_min', soft_min)
        set_prop_setting(node, prop_name, 'soft_max', soft_max)
        set_prop_setting(node, prop_name, 'default', default)
        
    # set as overridable
    node.property_overridable_library_set('["'+prop_name+'"]', True)