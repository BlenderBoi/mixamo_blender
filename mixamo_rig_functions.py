import bpy, os
from mathutils import *
from math import *
from bpy.app.handlers import persistent
from operator import itemgetter
from .utils import *
from .define import *

fk_leg = [c_prefix+leg_rig_names["thigh_fk"], c_prefix+leg_rig_names["calf_fk"], c_prefix+leg_rig_names["foot_fk"], c_prefix+leg_rig_names["toes_fk"]]
ik_leg = [leg_rig_names["thigh_ik"], leg_rig_names["calf_ik"], c_prefix+leg_rig_names["foot_ik"], c_prefix+leg_rig_names["pole_ik"], c_prefix+leg_rig_names["toes_ik"], c_prefix+leg_rig_names["foot_01"], c_prefix+leg_rig_names["foot_roll_cursor"], leg_rig_names["foot_snap"]]
fk_arm = [c_prefix+arm_rig_names["arm_fk"], c_prefix+arm_rig_names["forearm_fk"], c_prefix+arm_rig_names["hand_fk"]]
ik_arm = [arm_rig_names["arm_ik"], arm_rig_names["forearm_ik"], c_prefix+arm_rig_names["hand_ik"], c_prefix+arm_rig_names["pole_ik"]]

################## OPERATOR CLASSES ###################

class MR_OT_arm_bake_fk_to_ik(bpy.types.Operator):
    """Snaps and bake an FK to an IK arm over a specified frame range"""

    bl_idname = "pose.mr_bake_arm_fk_to_ik"
    bl_label = "Snap an FK to IK arm over a specified frame range"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")
    frame_start : bpy.props.IntProperty(name="Frame start", default=0)
    frame_end : bpy.props.IntProperty(name="Frame end", default=10)

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'frame_start', text='Frame Start')
        layout.prop(self, 'frame_end', text='Frame End')

    def invoke(self, context, event):
        action = context.active_object.animation_data.action
        self.frame_start, self.frame_end = int(action.frame_range[0]), int(action.frame_range[1])
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        # save current autokey state
        auto_key_state = bpy.context.scene.tool_settings.use_keyframe_insert_auto
        # set auto key to True
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        try:
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            bake_fk_to_ik_arm(self)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            # restore autokey state
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = auto_key_state

        return {'FINISHED'}


class MR_OT_arm_fk_to_ik(bpy.types.Operator):
    """Snaps an FK arm to an IK arm"""

    bl_idname = "pose.mr_arm_fk_to_ik_"
    bl_label = "Snap FK arm to IK"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)

            fk_to_ik_arm(self)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {'FINISHED'}


class MR_OT_arm_bake_ik_to_fk(bpy.types.Operator):
    """Snaps and bake an IK to an FK arm over a specified frame range"""

    bl_idname = "pose.mr_bake_arm_ik_to_fk"
    bl_label = "Snap an IK to FK arm over a specified frame range"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")
    frame_start : bpy.props.IntProperty(name="Frame start", default=0)
    frame_end : bpy.props.IntProperty(name="Frame end", default=10)

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'frame_start', text='Frame Start')
        layout.prop(self, 'frame_end', text='Frame End')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        # save current autokey state
        auto_key_state = bpy.context.scene.tool_settings.use_keyframe_insert_auto
        # set auto key to True
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        try:
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)

            bake_ik_to_fk_arm(self)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            # restore autokey state
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = auto_key_state

        return {'FINISHED'}


class MR_OT_arm_ik_to_fk(bpy.types.Operator):
    """Snaps an IK arm to an FK arm"""

    bl_idname = "pose.mr_arm_ik_to_fk_"
    bl_label = "Snap IK arm to FK"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)

            ik_to_fk_arm(self)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class MR_OT_switch_snap_anim(bpy.types.Operator):
    """Switch and snap IK-FK over multiple frames"""

    bl_idname = "pose.mr_switch_snap_anim"
    bl_label = "Switch and Snap IK FK anim"
    bl_options = {'UNDO'}

    rig = None
    side : bpy.props.StringProperty(name="bone side", default="")
    _side = ""
    prefix: bpy.props.StringProperty(name="", default="")
    type : bpy.props.StringProperty(name="type", default="")

    frame_start : bpy.props.IntProperty(name="Frame start", default=0)
    frame_end : bpy.props.IntProperty(name="Frame end", default=10)
    has_action = False


    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')


    def draw(self, context):
        layout = self.layout
        if self.has_action:
            layout.prop(self, 'frame_start', text='Frame Start')
            layout.prop(self, 'frame_end', text='Frame End')
        else:
            layout.label(text="This rig is not animated!")


    def invoke(self, context, event):
        try:
            action = context.active_object.animation_data.action
            if action:
                self.has_action = True
        except:
            pass

        if self.has_action:
            self.frame_start, self.frame_end = int(action.frame_range[0]), int(action.frame_range[1])

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


    def execute(self, context):
        if self.has_action == False:
            return {'FINISHED'}

        try:
            scn = context.scene
            # save current autokey state
            auto_key_state = scn.tool_settings.use_keyframe_insert_auto
            # set auto key to True
            scn.tool_settings.use_keyframe_insert_auto = True
            # save current frame
            cur_frame = scn.frame_current

            self.rig = context.active_object
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            self._side = '_'+self.side
            self.prefix = get_mixamo_prefix()


            if is_selected(fk_leg, bname) or is_selected(ik_leg, bname):
                self.type = "LEG"
            elif is_selected(fk_arm, bname) or is_selected(ik_arm, bname):
                self.type = "ARM"

            if self.type == "ARM":
                c_hand_ik = get_pose_bone(c_prefix+arm_rig_names["hand_ik"]+self._side)#self.prefix+self.side+'Hand')
                if c_hand_ik['ik_fk_switch'] < 0.5:
                    bake_fk_to_ik_arm(self)
                else:
                    bake_ik_to_fk_arm(self)

            elif self.type == "LEG":
                c_foot_ik = get_pose_bone(c_prefix+leg_rig_names["foot_ik"]+self._side)#get_pose_bone(self.prefix+self.side+'Foot')
                if c_foot_ik['ik_fk_switch'] < 0.5:
                    bake_fk_to_ik_leg(self)
                else:
                    print("Bake IK to FK leg")
                    bake_ik_to_fk_leg(self)


        finally:
            # restore autokey state
            scn.tool_settings.use_keyframe_insert_auto = auto_key_state
            # restore frame
            scn.frame_set(cur_frame)

        return {'FINISHED'}


class MR_OT_switch_snap(bpy.types.Operator):
    """Switch and snap IK-FK for the current frame"""

    bl_idname = "pose.mr_switch_snap"
    bl_label = "Switch and Snap IK FK"
    bl_options = {'UNDO'}

    rig = None
    side : bpy.props.StringProperty(name="bone side", default="")
    _side = ""
    prefix: bpy.props.StringProperty(name="", default="")
    type : bpy.props.StringProperty(name="type", default="")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            self.rig = context.active_object
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            self._side = '_'+self.side
            self.prefix = get_mixamo_prefix()

            if is_selected(fk_leg, bname) or is_selected(ik_leg, bname):
                self.type = "LEG"
            elif is_selected(fk_arm, bname) or is_selected(ik_arm, bname):
                self.type = "ARM"


            if self.type == "ARM":
                #base_hand = get_pose_bone(self.prefix+self.side+'Hand')
                c_hand_ik = get_pose_bone(c_prefix+arm_rig_names["hand_ik"]+self._side)#self.prefix+self.side+'Hand')
                if c_hand_ik['ik_fk_switch'] < 0.5:
                    fk_to_ik_arm(self)
                else:
                    ik_to_fk_arm(self)

            elif self.type == "LEG":
                #base_foot = get_pose_bone(self.prefix+self.side+'Foot')
                c_foot_ik = get_pose_bone(c_prefix+leg_rig_names["foot_ik"]+self._side)#get_pose_bone(self.prefix+self.side+'Foot')
                if c_foot_ik['ik_fk_switch'] < 0.5:
                    fk_to_ik_leg(self)
                else:
                    ik_to_fk_leg(self)


        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {'FINISHED'}


class MR_OT_leg_bake_fk_to_ik(bpy.types.Operator):
    """Snaps and bake an FK leg to an IK leg over a specified frame range"""

    bl_idname = "pose.mr_bake_leg_fk_to_ik"
    bl_label = "Snap an FK to IK leg over a specified frame range"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")
    _side = ""
    prefix = ""
    frame_start : bpy.props.IntProperty(name="Frame start", default=0)
    frame_end : bpy.props.IntProperty(name="Frame end", default=10)
    rig = None

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'frame_start', text='Frame Start')
        layout.prop(self, 'frame_end', text='Frame End')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        # save current autokey state
        auto_key_state = bpy.context.scene.tool_settings.use_keyframe_insert_auto
        # set auto key to True
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        try:
            self.rig = context.active_object
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            self._side = '_'+self.side
            self.prefix = get_mixamo_prefix()

            bake_fk_to_ik_leg(self)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            # restore autokey state
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = auto_key_state

        return {'FINISHED'}


class MR_OT_leg_fk_to_ik(bpy.types.Operator):
    """Snaps an FK leg to an IK leg"""

    bl_idname = "pose.mr_leg_fk_to_ik_"
    bl_label = "Snap FK leg to IK"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")
    rig = None
    _side = ""
    prefix = ""

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            self.rig = context.active_object
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            self._side = '_'+self.side
            self.prefix = get_mixamo_prefix()

            fk_to_ik_leg(self)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class MR_OT_leg_bake_ik_to_fk(bpy.types.Operator):
    """Snaps and bake an IK leg to an FK leg over a specified frame range"""

    bl_idname = "pose.mr_bake_leg_ik_to_fk"
    bl_label = "Snap an IK to FK leg over a specified frame range"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")
    frame_start : bpy.props.IntProperty(name="Frame start", default=0)
    frame_end : bpy.props.IntProperty(name="Frame end", default=10)
    rig = None
    _side = ""
    prefix = ""


    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'frame_start', text='Frame Start')
        layout.prop(self, 'frame_end', text='Frame End')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        # save current autokey state
        auto_key_state = bpy.context.scene.tool_settings.use_keyframe_insert_auto
        # set auto key to True
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        try:
            self.rig = context.active_object
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            self._side = '_'+self.side
            self.prefix = get_mixamo_prefix()

            bake_ik_to_fk_leg(self)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            # restore autokey state
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = auto_key_state

        return {'FINISHED'}


class MR_OT_leg_ik_to_fk(bpy.types.Operator):
    """Snaps an IK leg to an FK leg"""

    bl_idname = "pose.mr_leg_ik_to_fk_"
    bl_label = "Snap IK leg to FK"
    bl_options = {'UNDO'}

    side : bpy.props.StringProperty(name="bone side")
    rig = None
    _side = ""
    prefix = ""

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            self.rig = context.active_object
            bname = get_selected_pbone_name()
            self.side = get_bone_side(bname)
            self._side = '_'+self.side
            self.prefix = get_mixamo_prefix()

            ik_to_fk_leg(self)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {'FINISHED'}



################## FUNCTIONS ##################

def set_pose_rotation(pose_bone, mat):
    q = mat.to_quaternion()

    if pose_bone.rotation_mode == 'QUATERNION':
        pose_bone.rotation_quaternion = q
    elif pose_bone.rotation_mode == 'AXIS_ANGLE':
        pose_bone.rotation_axis_angle[0] = q.angle
        pose_bone.rotation_axis_angle[1] = q.axis[0]
        pose_bone.rotation_axis_angle[2] = q.axis[1]
        pose_bone.rotation_axis_angle[3] = q.axis[2]
    else:
        pose_bone.rotation_euler = q.to_euler(pose_bone.rotation_mode)


def snap_pos(pose_bone, target_bone):
    # Snap a bone to another bone. Supports child of constraints and parent.

    # if the pose_bone has direct parent
    if pose_bone.parent:
        # apply double time because of dependecy lag
        pose_bone.matrix = target_bone.matrix
        update_transform()
        # second apply
        pose_bone.matrix = target_bone.matrix
    else:
        # is there a child of constraint attached?
        child_of_cns = None
        if len(pose_bone.constraints) > 0:
            all_child_of_cns = [i for i in pose_bone.constraints if i.type == "CHILD_OF" and i.influence == 1.0 and i.mute == False and i.target]
            if len(all_child_of_cns) > 0:
                child_of_cns = all_child_of_cns[0]# in case of multiple child of constraints enabled, use only the first for now

        if child_of_cns != None:
            if child_of_cns.subtarget != "" and get_pose_bone(child_of_cns.subtarget):
                # apply double time because of dependecy lag
                pose_bone.matrix = get_pose_bone(child_of_cns.subtarget).matrix_channel.inverted() @ target_bone.matrix
                update_transform()
                pose_bone.matrix = get_pose_bone(child_of_cns.subtarget).matrix_channel.inverted() @ target_bone.matrix
            else:
                pose_bone.matrix = target_bone.matrix

        else:
            pose_bone.matrix = target_bone.matrix


def snap_pos_matrix(pose_bone, target_bone_matrix):
    # Snap a bone to another bone. Supports child of constraints and parent.

    # if the pose_bone has direct parent
    if pose_bone.parent:
        pose_bone.matrix = target_bone_matrix.copy()
        update_transform()
    else:
        # is there a child of constraint attached?
        child_of_cns = None
        if len(pose_bone.constraints) > 0:
            all_child_of_cns = [i for i in pose_bone.constraints if i.type == "CHILD_OF" and i.influence == 1.0 and i.mute == False and i.target]
            if len(all_child_of_cns) > 0:
                child_of_cns = all_child_of_cns[0]# in case of multiple child of constraints enabled, use only the first for now

        if child_of_cns != None:
            if child_of_cns.subtarget != "" and get_pose_bone(child_of_cns.subtarget):
                pose_bone.matrix = get_pose_bone(child_of_cns.subtarget).matrix_channel.inverted() @ target_bone_matrix
                update_transform()
            else:
                pose_bone.matrix = target_bone_matrix.copy()

        else:
            pose_bone.matrix = target_bone_matrix.copy()


def snap_rot(pose_bone, target_bone):
    method = 1

    if method == 1:
        mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
        set_pose_rotation(pose_bone, mat)
        #bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.ops.object.mode_set(mode='POSE')
        bpy.context.view_layer.update()
    elif method == 2:
        loc, scale = pose_bone.location.copy(), pose_bone.scale.copy()
        pose_bone.matrix = target_bone.matrix
        pose_bone.location, pose_bone.scale = loc, scale
        bpy.context.view_layer.update()


def bake_fk_to_ik_arm(self):
    for f in range(self.frame_start, self.frame_end +1):
        bpy.context.scene.frame_set(f)
        print("baking frame", f)
        fk_to_ik_arm(self)


def fk_to_ik_arm(self):
    rig = self.rig
    side = self.side
    _side = self._side
    prefix = self.prefix

    arm_fk  = rig.pose.bones[fk_arm[0] + _side]
    forearm_fk  = rig.pose.bones[fk_arm[1] + _side]
    hand_fk  = rig.pose.bones[fk_arm[2] + _side]

    arm_ik = rig.pose.bones[ik_arm[0] + _side]
    forearm_ik = rig.pose.bones[ik_arm[1] + _side]
    hand_ik = rig.pose.bones[ik_arm[2] + _side]
    pole = rig.pose.bones[ik_arm[3] + _side]

    #Snap rot
    snap_rot(arm_fk, arm_ik)
    snap_rot(forearm_fk, forearm_ik)
    snap_rot(hand_fk, hand_ik)

    #Snap scale
    hand_fk.scale =hand_ik.scale

    #rot debug
    forearm_fk.rotation_euler[0]=0
    forearm_fk.rotation_euler[1]=0

    #switch
    #base_hand = get_pose_bone(prefix+side+'Hand')
    c_hand_ik = get_pose_bone(c_prefix+arm_rig_names["hand_ik"]+_side)
    c_hand_ik['ik_fk_switch'] = 1.0

    #udpate view
    bpy.context.view_layer.update()

    #insert key if autokey enable
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        #fk chain
        c_hand_ik.keyframe_insert(data_path='["ik_fk_switch"]')
        hand_fk.keyframe_insert(data_path="scale")
        hand_fk.keyframe_insert(data_path="rotation_euler")
        arm_fk.keyframe_insert(data_path="rotation_euler")
        forearm_fk.keyframe_insert(data_path="rotation_euler")

        #ik chain
        hand_ik.keyframe_insert(data_path="location")
        hand_ik.keyframe_insert(data_path="rotation_euler")
        hand_ik.keyframe_insert(data_path="scale")
        pole.keyframe_insert(data_path="location")

    # change FK to IK hand selection, if selected
    if hand_ik.bone.select:
        hand_fk.bone.select = True
        hand_ik.bone.select = False


def bake_ik_to_fk_arm(self):
    for f in range(self.frame_start, self.frame_end +1):
        bpy.context.scene.frame_set(f)
        print("baking frame", f)

        ik_to_fk_arm(self)


def ik_to_fk_arm(self):
    rig = self.rig
    side = self.side
    _side = self._side
    prefix = self.prefix

    arm_fk  = rig.pose.bones[fk_arm[0] + _side]
    forearm_fk  = rig.pose.bones[fk_arm[1] + _side]
    hand_fk  = rig.pose.bones[fk_arm[2] + _side]

    arm_ik = rig.pose.bones[ik_arm[0] + _side]
    forearm_ik = rig.pose.bones[ik_arm[1] + _side]
    hand_ik = rig.pose.bones[ik_arm[2] + _side]
    pole_ik  = rig.pose.bones[ik_arm[3] + _side]

    # Snap
        # constraint support
    constraint = None
    bparent_name = ""
    parent_type = ""
    valid_constraint = True

    # Snap Hand
    if len(hand_ik.constraints) > 0:
        for c in hand_ik.constraints:
            if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
                if c.target:
                    #if bone
                    if c.target.type == 'ARMATURE':
                        bparent_name = c.subtarget
                        parent_type = "bone"
                        constraint = c
                    #if object
                    else:
                        bparent_name = c.target.name
                        parent_type = "object"
                        constraint = c


    if constraint != None:
        if parent_type == "bone":
            if bparent_name == "":
                valid_constraint = False

    if constraint and valid_constraint:
        if parent_type == "bone":
            bone_parent = get_pose_bone(bparent_name)
            hand_ik.matrix = bone_parent.matrix_channel.inverted() @ hand_fk.matrix
        if parent_type == "object":
            bone_parent = bpy.data.objects[bparent_name]
            obj_par = bpy.data.objects[bparent_name]
            hand_ik.matrix = constraint.inverse_matrix.inverted() @ obj_par.matrix_world.inverted() @ hand_fk.matrix
    else:
        hand_ik.matrix = hand_fk.matrix

    # Snap Pole
    _axis = forearm_fk.x_axis if side == "Left" else -forearm_fk.x_axis
    pole_pos = get_ik_pole_pos(arm_fk, forearm_fk, method=2, axis=_axis)
    pole_mat = Matrix.Translation(pole_pos)
    snap_pos_matrix(pole_ik, pole_mat)

    # Switch
    c_hand_ik = get_pose_bone(c_prefix+arm_rig_names["hand_ik"]+_side)
    #base_hand = get_pose_bone(prefix+side+'Hand')
    c_hand_ik['ik_fk_switch'] = 0.0

    # update
    update_transform()

     #insert key if autokey enable
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        #ik chain
        c_hand_ik.keyframe_insert(data_path='["ik_fk_switch"]')
        hand_ik.keyframe_insert(data_path="location")
        hand_ik.keyframe_insert(data_path="rotation_euler")
        hand_ik.keyframe_insert(data_path="scale")
        pole_ik.keyframe_insert(data_path="location")

        #fk chain
        hand_fk.keyframe_insert(data_path="location")
        hand_fk.keyframe_insert(data_path="rotation_euler")
        hand_fk.keyframe_insert(data_path="scale")
        arm_fk.keyframe_insert(data_path="rotation_euler")
        forearm_fk.keyframe_insert(data_path="rotation_euler")

    # change FK to IK hand selection, if selected
    if hand_fk.bone.select:
        hand_fk.bone.select = False
        hand_ik.bone.select = True


def bake_fk_to_ik_leg(self):
    for f in range(self.frame_start, self.frame_end +1):
        bpy.context.scene.frame_set(f)
        print("baking frame", f)

        fk_to_ik_leg(self)


def fk_to_ik_leg(self):
    rig = self.rig
    side = self.side
    _side = self._side
    prefix = self.prefix

    thigh_fk = rig.pose.bones[fk_leg[0] + _side]
    leg_fk = rig.pose.bones[fk_leg[1] + _side]
    foot_fk = rig.pose.bones[fk_leg[2] + _side]
    toes_fk = rig.pose.bones[fk_leg[3] + _side]

    thigh_ik = rig.pose.bones[ik_leg[0] + _side]
    leg_ik = rig.pose.bones[ik_leg[1] + _side]
    foot_ik = rig.pose.bones[ik_leg[2] + _side]
    pole_ik = rig.pose.bones[ik_leg[3] + _side]
    toes_ik = rig.pose.bones[ik_leg[4] + _side]
    foot_01_ik = rig.pose.bones[ik_leg[5] + _side]
    foot_roll_ik = rig.pose.bones[ik_leg[6] + _side]
    foot_snap_ik = rig.pose.bones[ik_leg[7] + _side]

    # Thigh snap
    snap_rot(thigh_fk, thigh_ik)
    #thigh_fk.matrix = thigh_ik.matrix.copy()

    # Leg snap
    snap_rot(leg_fk, leg_ik)

    # Foot snap
    snap_rot(foot_fk, foot_snap_ik)
    foot_fk.scale =foot_ik.scale

    # Toes snap
    snap_rot(toes_fk, toes_ik)
    toes_fk.scale = toes_ik.scale

    # rotation fix
    leg_fk.rotation_euler[1] = 0.0
    leg_fk.rotation_euler[2] = 0.0

    # switch prop value
    c_foot_ik = get_pose_bone(c_prefix+leg_rig_names["foot_ik"]+_side)
    #base_foot = get_pose_bone(prefix+side+'Foot')
    c_foot_ik['ik_fk_switch'] = 1.0

    # udpate hack
    bpy.context.view_layer.update()

    #if bpy.context.scene.frame_current == 2:
    #    print(br)

    #insert key if autokey enable
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        #fk chain
        c_foot_ik.keyframe_insert(data_path='["ik_fk_switch"]')
        thigh_fk.keyframe_insert(data_path="rotation_euler")
        leg_fk.keyframe_insert(data_path="rotation_euler")
        foot_fk.keyframe_insert(data_path="rotation_euler")
        foot_fk.keyframe_insert(data_path="scale")
        toes_fk.keyframe_insert(data_path="rotation_euler")
        toes_fk.keyframe_insert(data_path="scale")

        #ik chain
        foot_ik.keyframe_insert(data_path="location")
        foot_ik.keyframe_insert(data_path="rotation_euler")
        foot_ik.keyframe_insert(data_path="scale")
        foot_01_ik.keyframe_insert(data_path="rotation_euler")
        foot_roll_ik.keyframe_insert(data_path="location")
        toes_ik.keyframe_insert(data_path="rotation_euler")
        toes_ik.keyframe_insert(data_path="scale")
        pole_ik.keyframe_insert(data_path="location")

    # change IK to FK foot selection, if selected
    if foot_ik.bone.select:
        foot_fk.bone.select = True
        foot_ik.bone.select = False


def bake_ik_to_fk_leg(self):
    for f in range(self.frame_start, self.frame_end +1):
        bpy.context.scene.frame_set(f)
        print("baking frame", f)

        ik_to_fk_leg(self)


def ik_to_fk_leg(self):
    rig = self.rig
    side = self.side
    _side = self._side
    prefix = self.prefix

    thigh_fk = rig.pose.bones[fk_leg[0] + _side]
    leg_fk = rig.pose.bones[fk_leg[1] + _side]
    foot_fk = rig.pose.bones[fk_leg[2] + _side]
    toes_fk = rig.pose.bones[fk_leg[3] + _side]

    thigh_ik = rig.pose.bones[ik_leg[0] + _side]
    calf_ik = rig.pose.bones[ik_leg[1] + _side]
    foot_ik = rig.pose.bones[ik_leg[2] + _side]
    pole_ik = rig.pose.bones[ik_leg[3] + _side]
    toes_ik = rig.pose.bones[ik_leg[4] + _side]
    foot_01_ik = rig.pose.bones[ik_leg[5] + _side]
    foot_roll_ik = rig.pose.bones[ik_leg[6] + _side]


    # reset IK foot_01 and foot_roll
    foot_01_ik.rotation_euler = [0,0,0]
    foot_roll_ik.location[0] = 0.0
    foot_roll_ik.location[2] = 0.0

    # Snap toes
    toes_ik.rotation_euler = toes_fk.rotation_euler.copy()
    toes_ik.scale = toes_fk.scale.copy()

    # Child Of constraint or parent cases
    constraint = None
    bparent_name = ""
    parent_type = ""
    valid_constraint = True

    if len(foot_ik.constraints) > 0:
        for c in foot_ik.constraints:
            if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
                if c.target:
                    #if bone
                    if c.target.type == 'ARMATURE':
                        bparent_name = c.subtarget
                        parent_type = "bone"
                        constraint = c
                    #if object
                    else:
                        bparent_name = c.target.name
                        parent_type = "object"
                        constraint = c

    if constraint != None:
        if parent_type == "bone":
            if bparent_name == "":
                valid_constraint = False

    # Snap Foot
    if constraint and valid_constraint:
        if parent_type == "bone":
            bone_parent = rig.pose.bones[bparent_name]
            foot_ik.matrix = bone_parent.matrix_channel.inverted() @ foot_fk.matrix
        if parent_type == "object":
            ob = bpy.data.objects[bparent_name]
            foot_ik.matrix = constraint.inverse_matrix.inverted() @ ob.matrix_world.inverted() @ foot_fk.matrix

    else:
        foot_ik.matrix = foot_fk.matrix

    # update
    bpy.context.view_layer.update()

    # Snap Pole
    pole_pos = get_ik_pole_pos(thigh_fk, leg_fk, method=2, axis=leg_fk.z_axis)
    pole_mat = Matrix.Translation(pole_pos)
    snap_pos_matrix(pole_ik, pole_mat)

    update_transform()

    # switch
    c_foot_ik = get_pose_bone(c_prefix+leg_rig_names["foot_ik"]+_side)
    #base_foot = get_pose_bone(prefix+side+'Foot')
    c_foot_ik['ik_fk_switch'] = 0.0

    update_transform()

    #insert key if autokey enable
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        #ik chain
        c_foot_ik.keyframe_insert(data_path='["ik_fk_switch"]')
        foot_01_ik.keyframe_insert(data_path="rotation_euler")
        foot_roll_ik.keyframe_insert(data_path="location")
        foot_ik.keyframe_insert(data_path="location")
        foot_ik.keyframe_insert(data_path="rotation_euler")
        foot_ik.keyframe_insert(data_path="scale")
        toes_ik.keyframe_insert(data_path="rotation_euler")
        toes_ik.keyframe_insert(data_path="scale")
        pole_ik.keyframe_insert(data_path="location")

        #fk chain
        thigh_fk.keyframe_insert(data_path="rotation_euler")
        leg_fk.keyframe_insert(data_path="rotation_euler")
        foot_fk.keyframe_insert(data_path="rotation_euler")
        foot_fk.keyframe_insert(data_path="scale")
        toes_fk.keyframe_insert(data_path="rotation_euler")
        toes_fk.keyframe_insert(data_path="scale")

    # change IK to FK foot selection, if selected
    if foot_fk.bone.select:
        foot_fk.bone.select = False
        foot_ik.bone.select = True


def get_active_child_of_cns(bone):
    constraint = None
    bparent_name = ""
    parent_type = ""
    valid_constraint = True

    if len(bone.constraints) > 0:
        for c in bone.constraints:
            if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
                if c.target:
                    if c.target.type == 'ARMATURE':# bone
                        bparent_name = c.subtarget
                        parent_type = "bone"
                        constraint = c
                    else:# object
                        bparent_name = c.target.name
                        parent_type = "object"
                        constraint = c

    if constraint:
        if parent_type == "bone":
            if bparent_name == "":
                valid_constraint = False

    return constraint, bparent_name, parent_type, valid_constraint


def is_selected(names, selected_bone_name, startswith=False):
    side = ""
    if get_bone_side(selected_bone_name) != None:
       side = get_bone_side(selected_bone_name)

    _side = "_"+side

    if startswith == False:
        if type(names) == list:
            for name in names:
                if not "." in name[-2:]:
                    if name + _side == selected_bone_name:
                        return True
                else:
                    if name[-2:] == ".x":
                        if name[:-2] + _side == selected_bone_name:
                            return True
        elif names == selected_bone_name:
            return True
    else:#startswith
        if type(names) == list:
            for name in names:
                if selected_bone_name.startswith(name):
                    return True
        else:
            return selected_bone_name.startswith(names)
    return False


def is_selected_prop(pbone, prop_name):
    if pbone.bone.keys():
        if prop_name in pbone.bone.keys():
            return True


################## User Interface ##################
class MR_PT_rig_ui(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_label = "Mixamo Rig Settings"
    bl_idname = "MR_PT_rig_ui"

    @classmethod
    def poll(self, context):
        if context.mode != 'POSE':
            return False
        return True


    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene
        rig = context.active_object

        if rig == None:
            return
        if rig.type != "ARMATURE":
            return

        # check if a Mixamo ctrl rig is selected
        if len(rig.data.keys()):
            if not 'mr_control_rig' in rig.data.keys():
                return
        else:
            return


        pose_bones = rig.pose.bones

        try:
            active_bone = context.selected_pose_bones[0]#context.active_pose_bone
            selected_bone_name = active_bone.name
        except:
            return

        side = get_bone_side(selected_bone_name)
        prefix = get_mixamo_prefix()

       # Leg
        if (is_selected(fk_leg, selected_bone_name) or is_selected(ik_leg, selected_bone_name)):
            # IK-FK Switch
            col = layout.column(align=True)
            #foot_base = get_pose_bone(prefix+side.title()+'Foot')
            c_foot_ik = get_pose_bone(c_prefix+leg_rig_names["foot_ik"]+'_'+side.title())
            col.prop(c_foot_ik, '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
            col.operator(MR_OT_switch_snap.bl_idname, text="Snap Frame IK/FK")
            col.operator(MR_OT_switch_snap_anim.bl_idname, text="Snap Anim IK-FK")


        # Arm
        if is_selected(fk_arm, selected_bone_name) or is_selected(ik_arm, selected_bone_name):
            # IK-FK Switch
            col = layout.column(align=True)
            #hand_base = get_pose_bone(prefix+side.title()+'Hand')
            c_hand_ik = get_pose_bone(c_prefix+arm_rig_names["hand_ik"]+'_'+side.title())
            col.prop(c_hand_ik, '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
            col.operator(MR_OT_switch_snap.bl_idname, text="Snap Frame IK-FK")
            col.operator(MR_OT_switch_snap_anim.bl_idname, text="Snap Anim IK-FK")



##################  REGISTER  ##################
classes = (
    MR_OT_arm_bake_fk_to_ik,
    MR_OT_arm_fk_to_ik,
    MR_OT_arm_bake_ik_to_fk,
    MR_OT_arm_ik_to_fk,
    MR_OT_switch_snap,
    MR_OT_leg_fk_to_ik,
    MR_OT_leg_bake_fk_to_ik,
    MR_OT_leg_ik_to_fk,
    MR_OT_leg_bake_ik_to_fk,
    MR_PT_rig_ui,
    MR_OT_switch_snap_anim)


def update_mixamo_tab():
    try:
        bpy.utils.unregister_class(MR_PT_rig_ui)
    except:
        pass

    MR_PT_rig_ui.bl_category = bpy.context.preferences.addons[__package__].preferences.mixamo_tab_name
    bpy.utils.register_class(MR_PT_rig_ui)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    update_mixamo_tab()

    bpy.types.Scene.mix_show_ik_fk_advanced = bpy.props.BoolProperty(name="Show IK-FK operators", description="Show IK-FK manual operators", default=False)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.mix_show_ik_fk_advanced
