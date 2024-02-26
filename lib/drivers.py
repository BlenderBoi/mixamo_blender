import bpy

def add_driver_to_prop(obj, dr_dp, tar_dp, array_idx=-1, exp="var"):
    if obj.animation_data == None:
        obj.animation_data_create()
        
    drivers_list = obj.animation_data.drivers
    dr = drivers_list.find(dr_dp, index=array_idx)

    if dr == None:
        dr = obj.driver_add(dr_dp, array_idx)

    dr.driver.expression = exp

    var = dr.driver.variables.get('var')

    if var == None:
        var = dr.driver.variables.new()

    var.type = 'SINGLE_PROP'
    var.name = 'var'
    var.targets[0].id = obj
    var.targets[0].data_path = tar_dp