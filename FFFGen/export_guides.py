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
from . import constants

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

# small helper function for object duplication
# links everything to the scene collection so the new objects should be available to operators etc.
# using bpy.ops.object.duplicate() has some issues here, i guess due to visibility, even with override context...
def duplicate_object(object_to_duplicate, duplicated_object_name):
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    new_object = object_to_duplicate.copy()
    new_object.data= object_to_duplicate.data.copy()
    new_object.name = duplicated_object_name
    bpy.context.collection.objects.link(new_object)
    return new_object

def export_reconstructed_mandible(context, dir_path):
    # TODO: (Luka) implement
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    # clone mandible object(cut one)
    mandible_clone = duplicate_object(bpy.data.objects["mandible_copy.001"], "clone_mandible")
    
    # on cloned mandible apply all modifiers. the mandible has no constraints set...
    for mandible_modifier in mandible_clone.modifiers:
        bpy.context.view_layer.objects.active = mandible_clone
        bpy.ops.object.modifier_apply(modifier=mandible_modifier.name, single_user=True)

    # clone grafts after accumulating all present...
    graft_originals = []
    for obj in bpy.data.collections[constants.COLLECTION_FFF_GEN_MANDIBLE].objects:
        if obj.name.startswith("fibula_object."):
            graft_originals.append(obj)
    graft_clones = []
    for index, obj in enumerate(graft_originals):
        graft_clone = duplicate_object(obj, "graft_clone." + str(index))
        graft_clones.append(graft_clone)
    
    # on cloned grafts apply all modifiers and constraints,
    # move origin to geometry,
    # and scale each cloned graft on local y axis by a factor of 1.001 to avoid issues with co-planar faces in boolean.
    for graft_clone in graft_clones:
        # apply modifiers and constraints
        for graft_clone_modifier in graft_clone.modifiers:
            bpy.context.view_layer.objects.active = graft_clone
            bpy.ops.object.modifier_apply(modifier=graft_clone_modifier.name, single_user=True)
        for graft_clone_constraint in graft_clone.constraints:
            bpy.context.view_layer.objects.active = graft_clone
            bpy.ops.constraint.apply(constraint=graft_clone_constraint.name)
        # origin to geometry.
        graft_clone.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
        graft_clone.select_set(False)
        # scale cloned graft on local y by a factor of 1.001
        graft_clone.scale.y = graft_clone.scale.y * 1.001

    # add a boole union on the cloned mandible object for each graft
    for graft_clone in graft_clones:
        modifier_boolean = mandible_clone.modifiers.new(
            name="boolean",
            type="BOOLEAN"
        )
        modifier_boolean.operation = "UNION"
        modifier_boolean.object = graft_clone
        modifier_boolean.solver = "EXACT"

    # export the cloned mandible object with modifiers applied
    export_mesh_stl(context, mandible_clone, dir_path, "reconstructed_mandible")

    # delete all cloned objects as they are no longer required.
    mandible_clone.select_set(True)
    for graft_clone in graft_clones:
        graft_clone.select_set(True)
    bpy.ops.object.delete()
    return

# TODO: (Luka) switch this to use invoke_props_dialog and provide a warning message if a file would be overwritten...
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
        if properties.export_toggle_reconstructed_mandible:
            export_reconstructed_mandible(context, properties.export_dir_path)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
