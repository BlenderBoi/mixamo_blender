import bpy

def get_data_bone(name):
    return bpy.context.active_object.data.bones.get(name)


def set_bone_collection(armt, databone, coll_name, multi=False):
    if databone is None:
        return

    armt = armt.data

    coll = None
    for c in armt.collections:
        if c.name == coll_name:
            coll = c
            break

    if coll is None:
        coll = armt.collections.new(coll_name)

    colls_to_remove_from = None
    if not multi:
        colls_to_remove_from = [c for c in databone.collections]

    r = coll.assign(databone)

    if colls_to_remove_from is not None:
        for c in colls_to_remove_from:
            c.unassign(databone)

    # ~ databone.layers[layer_idx] = True

    # ~ for i, lay in enumerate(databone.layers):
        # ~ if i != layer_idx:
            # ~ databone.layers[i] = False
