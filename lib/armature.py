import bpy

def restore_armature_layers(layers_select):
    # restore the armature layers visibility
    # ~ for i in range(0, 32):
        # ~ bpy.context.active_object.data.layers[i] = layers_select[i]
    for c in bpy.context.active_object.data.collections:
        if c.name in layers_select:
            c.is_visible = layers_select[c.name]
        else:
            c.is_visible = False


def enable_all_armature_layers():
    # enable all layers
    # and return the list of each layer visibility
    # ~ _layers = bpy.context.active_object.data.layers
    # ~ layers_select = []
    # ~ for i in range(0, 32):
        # ~ layers_select.append(_layers[i])
    # ~ for i in range(0, 32):
        # ~ bpy.context.active_object.data.layers[i] = True

    layers_select = {}
    for c in bpy.context.active_object.data.collections:
        layers_select[c.name] = c.is_visible
        c.is_visible = True

    return layers_select
