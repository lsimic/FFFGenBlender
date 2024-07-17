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
from . import constants
from .move_object_to_collection import move_object_to_collection


class ClearFibulaGuides(bpy.types.Operator):
    bl_idname = "fff_gen.clear_fibula_guides"
    bl_label = "Clear fibula guide objects"
    bl_description = "Removes all fibula guide objects"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        clear_fibula_guides()
        return {"FINISHED"}


class ClearMandibleGuides(bpy.types.Operator):
    bl_idname = "fff_gen.clear_mandible_guides"
    bl_label = "Clear mandible guide and positioning aid objects"
    bl_description = "Removes all mandible and positioning guide objects"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        clear_mandible_guides()
        return {"FINISHED"}


class ClearMandiblePositioningAid(bpy.types.Operator):
    bl_idname = "fff_gen.clear_mandible_positioning_aid"
    bl_label = "Clear mandible positioning aid objects"
    bl_description = "Removes all mandible positioning aid objects"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        clear_mandible_positioning_aid()
        return {"FINISHED"}


class ClearCuttingPlanes(bpy.types.Operator):
    bl_idname = "fff_gen.clear_cutting_planes"
    bl_label = "Clear cutting plane objects"
    bl_description = "Removes all cutting planes, and objects depending on them(fibula and mandible guides)"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        clear_fibula_guides()
        clear_mandible_guides()
        clear_cutting_planes()
        return {"FINISHED"}


class ClearAll(bpy.types.Operator):
    bl_idname = "fff_gen.clear_all"
    bl_label = "Clear All"
    bl_description = "Removes all created objects.\nEffectivly resets the state of the application"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        clear_fibula_guides()
        clear_mandible_guides()
        clear_cutting_planes()
        clear_fff_gen_objects()
        reset_collections()
        return {"FINISHED"}


def clear_mandible_guides():
    # deselect all selected objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # get the collections, craete override context using collection objects
    collection = bpy.data.collections[constants.COLLECTION_GUIDE_MANDIBLE]
    override_context = {
        "selected_objects":collection.objects
    }
    # delete using override context
    bpy.ops.object.delete(override_context)
    # set cutting plane visibility back
    bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_MANDIBLE].hide_viewport = False


def clear_mandible_positioning_aid():
    # deselect all selected objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    # select all positioning aid specific objects.
    objects = []
    positioning_aid_object_names = [
        "positioning_aid_curve",
        "positioning_aid_curve_handle_start",
        "positioning_aid_curve_handle_end",
        "positioning_aid_start",
        "positioning_aid_end",
        "positioning_aid_mesh"
    ]
    for obj_name in positioning_aid_object_names:
        if obj_name in bpy.data.objects.keys():
            objects.append(bpy.data.objects[obj_name])
    override_context = {
        "selected_objects":objects
    }

    # delete using override context
    bpy.ops.object.delete(override_context)


def clear_fibula_guides():
     # deselect all selected objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # get the collections, craete override context using collection objects
    collection = bpy.data.collections[constants.COLLECTION_GUIDE_FIBULA]
    override_context = {
        "selected_objects":collection.objects
    }
    # delete using override context
    bpy.ops.object.delete(override_context)
    # set cutting plane visibility back
    bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_FIBULA].hide_viewport = False


def clear_cutting_planes():
    # deselect all selected objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # get the collections, craete override context using collection objects
    collection_mandible = bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_MANDIBLE]
    collection_fibula = bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_FIBULA]
    objects = []
    for obj in collection_mandible.objects:
        objects.append(obj)
    for obj in collection_fibula.objects:
        objects.append(obj)
    override_context = {
        "selected_objects":objects
    }
    # delete using override context
    bpy.ops.object.delete(override_context)


def clear_fff_gen_objects():
    # deselect all selected objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # get the collections, craete override context using collection objects
    collection_fibula = bpy.data.collections[constants.COLLECTION_FFF_GEN_FIBULA]
    collection_mandible = bpy.data.collections[constants.COLLECTION_FFF_GEN_MANDIBLE]
    objects = []
    for obj in collection_mandible.objects:
        objects.append(obj)
    for obj in collection_fibula.objects:
        objects.append(obj)
    override_context = {
        "selected_objects":objects
    }
    # delete using override context
    bpy.ops.object.delete(override_context)


def reset_collections():
    # move objects from original collection to scene collection
    for obj in bpy.data.collections[constants.COLLECTION_ORIGINAL].objects:
        for collection in obj.users_collection:
            collection.objects.unlink(obj)
        bpy.context.scene.collection.objects.link(obj)
    # show original collection
    bpy.data.collections[constants.COLLECTION_ORIGINAL].hide_viewport = False
