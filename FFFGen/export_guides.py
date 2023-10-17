# ##### BEGIN GPL LICENSE BLOCK #####
#
#  FFF Gen Add-on
#  Copyright (C) 2020 Luka Simic
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
from bpy import context

def export_mesh_stl(context, object, dir_path, object_name):
    # TODO: (Luka) add confirmation for overrirde of existing files...
    # set override context with the given object.
    path = os.path.join(bpy.path.abspath(dir_path), object_name + ".stl")
    override = context.copy()
    objList = []
    objList.append(object)
    override["selected_objects"] = objList
    with context.temp_override(**override):
        bpy.ops.export_mesh.stl(
            filepath=path, 
            check_existing=True,
            use_selection=True, 
            global_scale=1.0, 
            use_scene_unit=False, 
            axis_forward="Y", 
            axis_up="Z"
        )

    return

def export_fibula_guide(context, dir_path):
    if "fibula_guide" in bpy.data.objects.keys():
        obj = bpy.data.objects["fibula_guide"]
        export_mesh_stl(context, obj, dir_path, "fibula_guide")
    return

def export_mandible_guide(context, dir_path):
    if "joined_mandible_guide" in bpy.data.objects.keys():
        obj = bpy.data.objects["joined_mandible_guide"]
        export_mesh_stl(context, obj, dir_path, "mandible_guide")
    return

def export_mandible_positioning_aid(context, dir_path):
    if "positioning_aid_mesh" in bpy.data.objects.keys():
        obj = bpy.data.objects["positioning_aid_mesh"]
        export_mesh_stl(context, obj, dir_path, "mandible_positioning_aid")
    return

class ExportGuides(bpy.types.Operator):
    bl_idname = "fff_gen.export_guides"
    bl_label = "Export FFF Gen objects"
    bl_description = "Exports the enabled fff gen objects (guides and positioning aids)"

    def execute(self, context):
        properties = context.scene.FFFGenPropertyGroup
        if properties.export_toggle_fibula_guide:
            export_fibula_guide(context, properties.export_dir_path)
        if properties.export_toggle_mandible_guide:
            export_mandible_guide(context, properties.export_dir_path)
        if properties.export_toggle_mandible_aid:
            export_mandible_positioning_aid(context, properties.export_dir_path)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
