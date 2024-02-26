import bpy, os

def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)
    
    
def duplicate_object():
    try:
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    except:
        bpy.ops.object.duplicate('TRANSLATION', False)
        
        
def get_object(name):
    return bpy.data.objects.get(name)


def set_active_object(object_name):
     bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
     bpy.data.objects[object_name].select_set(state=True)


def hide_object(obj_to_set):
    obj_to_set.hide_set(True)
    obj_to_set.hide_viewport = True


def is_object_hidden(obj_to_get):
    if obj_to_get.hide_get() == False and obj_to_get.hide_viewport == False:
        return False
    else:
        return True


def append_cs(names=[]):
    context = bpy.context
    scene = context.scene
    addon_directory = os.path.dirname(os.path.abspath(__file__))
    filepath = addon_directory + "\cs.blend"

    # load the objects data in file
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name in names]

    # Add the objects in the scene
    for obj in data_to.objects:
        if obj:
            # link in collec
            scene.collection.objects.link(obj)

            cs_grp = bpy.data.objects.get("cs_grp")
            if cs_grp == None:
                cs_grp = bpy.data.objects.new(name="cs_grp", object_data=None)
                bpy.context.collection.objects.link(cs_grp)
                cs_grp.location = [0,0,0]
                cs_grp.rotation_euler = [0,0,0]
                cs_grp.scale = [1,1,1]

            # parent the custom shape
            obj.parent = cs_grp

            # assign to new collection
            assigned_collections = []
            for collec in cs_grp.users_collection:
                try:
                    collec.objects.link(obj)
                    assigned_collections.append(collec)
                except:# already in collection
                    pass

            if len(assigned_collections):
                # remove previous collections
                for i in obj.users_collection:
                    if not i in assigned_collections:
                        i.objects.unlink(obj)
                # and the scene collection
                try:
                    scene.collection.objects.unlink(obj)
                except:
                    pass
                    