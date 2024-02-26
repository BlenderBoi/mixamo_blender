import bpy

def get_current_mode():
    return bpy.context.mode


def restore_current_mode(current_mode):
    if current_mode == 'EDIT_ARMATURE':
        current_mode = 'EDIT'
    bpy.ops.object.mode_set(mode=current_mode)