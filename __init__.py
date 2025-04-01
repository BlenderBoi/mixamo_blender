# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Mixamo Rig for Blender",
    "author": "Mixamo, Xin, TinkerBoi",
    "version": (1, 1, 1),
    "blender": (4, 0, 0),
    "location": "3D View > Mixamo> Control Rig",
    "description": "Generate a control rig from the selected Mixamo Fbx skeleton",
    "category": "Animation",
    "doc_url": "https://github.com/BlenderBoi/mixamo_blender",
    "tracker_url": "https://github.com/BlenderBoi/mixamo_blender"
}


if "bpy" in locals():
    import importlib
    if "mixamo_rig_prefs" in locals():
        importlib.reload(mixamo_rig_prefs)
    if "mixamo_rig" in locals():
        importlib.reload(mixamo_rig)
    if "mixamo_rig_functions" in locals():
        importlib.reload(mixamo_rig_functions)
    if "utils" in locals():
        importlib.reload(utils)
    if "animation" in locals():
        importlib.reload(animation)


import bpy
from . import mixamo_rig_prefs
from . import mixamo_rig
from . import mixamo_rig_functions
from . import utils

def register():
    mixamo_rig_prefs.register()
    mixamo_rig.register()
    mixamo_rig_functions.register()

def unregister():
    mixamo_rig_prefs.unregister()
    mixamo_rig.unregister()
    mixamo_rig_functions.unregister()

if __name__ == "__main__":
    register()
