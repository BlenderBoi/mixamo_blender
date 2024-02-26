import bpy

def get_edit_bone(name):
    return bpy.context.object.data.edit_bones.get(name)


def copy_bone_transforms(bone1, bone2):
    # copy editbone bone1 transforms to bone 2
    bone2.head = bone1.head.copy()
    bone2.tail = bone1.tail.copy()
    bone2.roll = bone1.roll


def create_edit_bone(bone_name, deform=False):
    b = get_edit_bone(bone_name)
    if b == None:
        b = bpy.context.active_object.data.edit_bones.new(bone_name)
        b.use_deform = deform
    return b