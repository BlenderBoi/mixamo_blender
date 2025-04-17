import bpy
from .maths_geo import *
from .bones_pose import *
from .version import *

def bake_anim(frame_start=0, frame_end=10, only_selected=False, bake_bones=True, bake_object=False, ik_data=None):
    scn = bpy.context.scene
    obj_data = []
    bones_data = []
    armature = bpy.data.objects.get(bpy.context.active_object.name)
    
    def get_bones_matrix():
        matrix = {}        
        for pbone in armature.pose.bones:            
            if only_selected and not pbone.bone.select:                
                continue
            
            bmat = pbone.matrix           
            
            # IK poles
            if pbone.name.startswith("Ctrl_ArmPole") or pbone.name.startswith("Ctrl_LegPole"):
                b1 = b2 = None
                src_arm = ik_data["src_arm"]
                type = ""
                if "Leg" in pbone.name:
                    type = "Leg"                    
                elif "Arm" in pbone.name:
                    type = "Arm"
                    
                name_split = pbone.name.split('_')
                side = name_split[len(name_split)-1]
                b1_name = ik_data[type+side][0]
                b2_name = ik_data[type+side][1]
                b1 = src_arm.pose.bones.get(b1_name)
                b2 = src_arm.pose.bones.get(b2_name)
                
                _axis = None
                if type == "Leg":
                    _axis = (b1.z_axis*0.5) + (b2.z_axis*0.5)#b1.z_axis#
                elif type == "Arm":
                    if side == "Left":
                        _axis = b2.x_axis
                    elif side == "Right":
                        _axis = -b2.x_axis
                
                pole_pos = get_ik_pole_pos(b1, b2, method=2, axis=_axis)
                #pole_pos = b2.head + (b2.z_axis.normalized() * (b2.tail-b2.head).magnitude)
                bmat = Matrix.Translation(pole_pos)
                
                # Child Of constraints are preserved after baking
                # need to compensate the matrix with the Child Of transformation
                child_of_cns = pbone.constraints.get("Child Of")
                if child_of_cns:     
                    if child_of_cns.influence == 1.0 and child_of_cns.mute == False:
                        bmat = get_pose_bone(child_of_cns.subtarget).matrix_channel.inverted() @ bmat
                    
            matrix[pbone.name] = armature.convert_space(pose_bone=pbone, matrix=bmat, from_space="POSE", to_space="LOCAL") 
            
        return matrix

    def get_obj_matrix():
        parent = armature.parent
        matrix = armature.matrix_world
        if parent:
            return parent.matrix_world.inverted_safe() @ matrix
        else:
            return matrix.copy()

    # store matrices
    current_frame = scn.frame_current

    for f in range(int(frame_start), int(frame_end+1)):
        scn.frame_set(f)
        bpy.context.view_layer.update()

        if bake_bones:
            bones_data.append((f, get_bones_matrix()))
        if bake_object:
            obj_data.append((f, get_obj_matrix()))

    # set new action
    action = bpy.data.actions.new("Action")
    anim_data = armature.animation_data_create()
    anim_data.action = action

    def store_keyframe(bn, prop_type, fc_array_index, fra, val):
        fc_data_path = 'pose.bones["' + bn + '"].' + prop_type
        fc_key = (fc_data_path, fc_array_index)
        if not keyframes.get(fc_key):
            keyframes[fc_key] = []
        keyframes[fc_key].extend((fra, val))


    # set transforms and store keyframes
    if bake_bones:
        for pb in armature.pose.bones:
            if only_selected and not pb.bone.select:
                continue

            euler_prev = None
            quat_prev = None
            keyframes = {}

            for (f, matrix) in bones_data:
                pb.matrix_basis = matrix[pb.name].copy()

                for arr_idx, value in enumerate(pb.location):
                    store_keyframe(pb.name, "location", arr_idx, f, value)

                rotation_mode = pb.rotation_mode

                if rotation_mode == 'QUATERNION':
                    if quat_prev is not None:
                        quat = pb.rotation_quaternion.copy()
                        quat.make_compatible(quat_prev)
                        pb.rotation_quaternion = quat
                        quat_prev = quat
                        del quat
                    else:
                        quat_prev = pb.rotation_quaternion.copy()

                    for arr_idx, value in enumerate(pb.rotation_quaternion):
                        store_keyframe(pb.name, "rotation_quaternion", arr_idx, f, value)

                elif rotation_mode == 'AXIS_ANGLE':
                    for arr_idx, value in enumerate(pb.rotation_axis_angle):
                        store_keyframe(pb.name, "rotation_axis_angle", arr_idx, f, value)

                else:  # euler, XYZ, ZXY etc
                    if euler_prev is not None:
                        euler = pb.rotation_euler.copy()
                        euler.make_compatible(euler_prev)
                        pb.rotation_euler = euler
                        euler_prev = euler
                        del euler
                    else:
                        euler_prev = pb.rotation_euler.copy()

                    for arr_idx, value in enumerate(pb.rotation_euler):
                        store_keyframe(pb.name, "rotation_euler", arr_idx, f, value)

                for arr_idx, value in enumerate(pb.scale):
                    store_keyframe(pb.name, "scale", arr_idx, f, value)


            # Add keyframes
            for fc_key, key_values in keyframes.items():
                data_path, index = fc_key
                if blender_version._float <= 403:
                    fcurve = action.fcurves.find(data_path=data_path, index=index)
                else:
                    fcurve = action.fcurve_ensure_for_datablock(
                        armature,  # Target data-block
                        data_path,
                        index=index
                    )
                if fcurve == None:
                    fcurve = action.fcurves.new(data_path, index=index, action_group=pb.name)

                num_keys = len(key_values) // 2
                fcurve.keyframe_points.add(num_keys)
                fcurve.keyframe_points.foreach_set('co', key_values)

                if blender_version._float >= 290:# internal error when doing so with Blender 2.83, only for Blender 2.90 and higher
                    linear_enum_value = bpy.types.Keyframe.bl_rna.properties['interpolation'].enum_items['LINEAR'].value
                    fcurve.keyframe_points.foreach_set('interpolation', (linear_enum_value,) * num_keys)
                else:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'


    if bake_object:
        euler_prev = None
        quat_prev = None

        for (f, matrix) in obj_data:
            name = "Action Bake"
            armature.matrix_basis = matrix

            armature.keyframe_insert("location", index=-1, frame=f, group=name)

            rotation_mode = armature.rotation_mode
            if rotation_mode == 'QUATERNION':
                if quat_prev is not None:
                    quat = armature.rotation_quaternion.copy()
                    quat.make_compatible(quat_prev)
                    armature.rotation_quaternion = quat
                    quat_prev = quat
                    del quat
                else:
                    quat_prev = armature.rotation_quaternion.copy()
                armature.keyframe_insert("rotation_quaternion", index=-1, frame=f, group=name)
            elif rotation_mode == 'AXIS_ANGLE':
                armature.keyframe_insert("rotation_axis_angle", index=-1, frame=f, group=name)
            else:  # euler, XYZ, ZXY etc
                if euler_prev is not None:
                    euler = armature.rotation_euler.copy()
                    euler.make_compatible(euler_prev)
                    armature.rotation_euler = euler
                    euler_prev = euler
                    del euler
                else:
                    euler_prev = armature.rotation_euler.copy()
                armature.keyframe_insert("rotation_euler", index=-1, frame=f, group=name)

            armature.keyframe_insert("scale", index=-1, frame=f, group=name)


    # restore current frame
    scn.frame_set(current_frame)
