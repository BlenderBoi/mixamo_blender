import bpy

def update_all_tab_names(self, context):
    try:
        from . import mixamo_rig
        mixamo_rig.update_mixamo_tab()
    except:
        pass


class MR_MT_addon_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    mixamo_tab_name : bpy.props.StringProperty(name="Interface Tab", description="Name of the tab to display the interface in", default="Mixamo", update=update_all_tab_names)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, "mixamo_tab_name", text="Interface Tab")


def register():
    from bpy.utils import register_class

    try:
        register_class(MR_MT_addon_preferences)
    except:
        pass


def unregister():
    from bpy.utils import unregister_class
    unregister_class(MR_MT_addon_preferences)
