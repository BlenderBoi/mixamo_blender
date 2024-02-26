import bpy

class ARP_blender_version:
    _string = bpy.app.version_string
    blender_v = bpy.app.version
    _float = blender_v[0]*100+blender_v[1]+blender_v[2]*0.01
    #_char = bpy.app.version_string

blender_version = ARP_blender_version()


def convert_drivers_cs_to_xyz(armature):
    # Blender 3.0 requires Vector3 custom_shape_scale values
    # convert single uniform driver to vector3 array drivers
    drivers_armature = [i for i in armature.animation_data.drivers]

    for dr in drivers_armature:
        if 'custom_shape_scale' in dr.data_path:
            if not 'custom_shape_scale_xyz' in dr.data_path:
                for i in range(0, 3):
                    new_dr = armature.animation_data.drivers.from_existing(src_driver=dr)
                    new_dr.data_path = new_dr.data_path.replace('custom_shape_scale', 'custom_shape_scale_xyz')
                    new_dr.array_index = i
                    new_dr.driver.expression += ''# update hack

                armature.driver_remove(dr.data_path, dr.array_index)

    print("Converted custom shape scale drivers to xyz")


def get_custom_shape_scale_prop_name():
    if blender_version._float >= 300:
        return 'custom_shape_scale_xyz'
    else:
        return 'custom_shape_scale'
