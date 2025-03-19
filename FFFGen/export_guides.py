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

def export_mesh_stl(context, object, full_file_path):
    # keep track of previously selected and active objects.
    active_old = bpy.context.active_object
    selected_old = bpy.context.selected_objects
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select_set(False)
    # set object to export as active and selected
    object.select_set(True)
    bpy.context.view_layer.objects.active = object

    # export object
    bpy.ops.wm.stl_export(
        filepath=full_file_path, 
        check_existing=True,
        export_selected_objects=True, 
        global_scale=context.scene.FFFGenPropertyGroup.export_scale_factor, 
        use_scene_unit=False, 
        forward_axis="Y", 
        up_axis="Z"
    )

    # deselect object to export
    object.select_set(False)
    # revert selection and active object to initial state.
    bpy.context.view_layer.objects.active = active_old
    for obj in selected_old:
        obj.select_set(True)

    return

def export_fibula_guide(context, full_file_path):
    if "fibula_guide" in bpy.data.objects.keys():
        obj = bpy.data.objects["fibula_guide"]
        export_mesh_stl(context, obj, full_file_path)
    return

def export_mandible_guide(context, full_file_path):
    if "joined_mandible_guide" in bpy.data.objects.keys():
        obj = bpy.data.objects["joined_mandible_guide"]
        export_mesh_stl(context, obj, full_file_path)
    return

def export_mandible_positioning_aid(context, full_file_path):
    if "positioning_aid_mesh" in bpy.data.objects.keys():
        obj = bpy.data.objects["positioning_aid_mesh"]
        export_mesh_stl(context, obj, full_file_path)
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

def export_reconstructed_mandible(context, full_file_path):
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
    export_mesh_stl(context, mandible_clone, full_file_path)

    # delete all cloned objects as they are no longer required.
    mandible_clone.select_set(True)
    for graft_clone in graft_clones:
        graft_clone.select_set(True)
    bpy.ops.object.delete()
    return

class ExportGuides(bpy.types.Operator):
    bl_idname = "fff_gen.export_guides"
    bl_label = "Export FFF Gen objects"
    bl_description = "Exports the enabled fff gen objects (guides and positioning aids)"
    bl_options = {'REGISTER', 'UNDO'}

    def get_stl_abspath(self, context, filename):
        properties = context.scene.FFFGenPropertyGroup
        dir_path = properties.export_dir_path
        if (dir_path.startswith("//")):
            dir_path = bpy.path.abspath(dir_path)
        path = os.path.join(dir_path, filename + ".stl")
        return path

    def find_path_check_exists(self, context, file):
        full_file_path = self.get_stl_abspath(context, file)
        exists = os.path.exists(full_file_path)
        return (full_file_path, exists)

    def draw(self, context):
        layout = self.layout
        warn_paths = []
        properties = context.scene.FFFGenPropertyGroup
        
        if properties.export_toggle_fibula_guide:
            fibula_path_exists = self.find_path_check_exists(context, "fibula_guide")
            if fibula_path_exists[1]:
                warn_paths.append(fibula_path_exists[0])
        
        if properties.export_toggle_mandible_guide:
            mandible_path_exists = self.find_path_check_exists(context, "mandible_guide")
            if mandible_path_exists[1]:
                warn_paths.append(mandible_path_exists[0])
        
        if properties.export_toggle_mandible_aid:
            positioning_path_exists = self.find_path_check_exists(context, "positioning_aid")
            if positioning_path_exists[1]:
                warn_paths.append(positioning_path_exists[0])

        if properties.export_toggle_reconstructed_mandible:
            reconstructed_path_exists = self.find_path_check_exists(context, "reconstructed_mandible")
            if reconstructed_path_exists[1]:
                warn_paths.append(reconstructed_path_exists[0])
        
        if len(warn_paths) > 0:
            layout.label(text="The following files exist.", icon="ERROR")
            for path in warn_paths:
                layout.label(text=path)
            layout.label(text="They will be overwritten.", icon="ERROR")
        
        return

    def execute(self, context):
        properties = context.scene.FFFGenPropertyGroup
        if properties.export_toggle_fibula_guide:
            export_path = self.get_stl_abspath(context, "fibula_guide")
            export_fibula_guide(context, export_path)
        if properties.export_toggle_mandible_guide:
            export_path = self.get_stl_abspath(context, "mandible_guide")
            export_mandible_guide(context, export_path)
        if properties.export_toggle_mandible_aid:
            export_path = self.get_stl_abspath(context, "positioning_aid")
            export_mandible_positioning_aid(context, export_path)
        if properties.export_toggle_reconstructed_mandible:
            export_path = self.get_stl_abspath(context, "reconstructed_mandible")
            export_reconstructed_mandible(context, export_path)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
