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
from .move_object_to_collection import move_object_to_collection
from . import constants


class AutoUpdateOperator(bpy.types.Operator):
    bl_idname = "fff_gen.auto_update_modal"
    bl_label = "FFF Gen Auto Update"
    bl_description = "Updates fibula objects to fit the current positioning automatically"
    _timer = None
    old_data = None

    def modal(self, context, event):
        if event.type == "TIMER":
            if not context.scene.FFFGenPropertyGroup.auto_update_toggle:
                self.cancel(context)
                return {"FINISHED"}
            else:
                data = list()
                for obj in bpy.context.scene.objects:
                    if (obj.name.startswith("vector.") or
                            obj.name.startswith("fibula_object.")):
                        data.append(obj.matrix_world.copy())
                if self.old_data != data:
                    print("Change detected")
                    self.old_data = data.copy()
                    modal_invoke(context)
                else:
                    print("No change detected")
        return {"PASS_THROUGH"}

    def execute(self, context):
        print("Auto update modal execute")
        wm = context.window_manager
        update_rate = bpy.context.scene.FFFGenPropertyGroup.update_rate
        self._timer = wm.event_timer_add(update_rate, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        print("Auto update modal cancel")
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class Update(bpy.types.Operator):
    bl_idname = "fff_gen.update"
    bl_label = "Update FFF Gen objects"
    bl_description = "Updates fibula objects to fit the current positioning."

    def invoke(self, context, event):
        modal_invoke(context)
        return {"FINISHED"}


def modal_invoke(context):

    # delete old duplicate objects and add new ones to proper locations
    delete_old_duplis(context)
    update_duplis(context)


def delete_old_duplis(context):
    # delete old fibula duplicates used for visualisation
    objects_to_delete = []
    for obj in bpy.data.objects:
        if obj.name.startswith("fibula_dupli."):
            objects_to_delete.append(obj)

    for obj in objects_to_delete:
        bpy.data.objects.remove(obj, do_unlink=True)

def update_duplis(context):
    # update fibula duplicates for visualisation
    # get all fibula graft objects
    objects_fibula = list()
    for obj in bpy.data.objects:
        if obj.name.startswith("fibula_object."):
            objects_fibula.append(obj)

    if "fibula_copy" in bpy.data.objects.keys():
        fibula_orig = bpy.data.objects["fibula_copy"]
    else:
        fibula_orig = None

    for obj_fibula in objects_fibula:
        # copy fibula object
        obj_fibula_dupli = obj_fibula.copy()
        obj_fibula_dupli.data = obj_fibula.data.copy()
        obj_fibula_dupli.name = "fibula_dupli." + obj_fibula.name[14:]
        bpy.context.scene.collection.objects.link(obj_fibula_dupli)

        # apply modifiers to obj_fibula_dupli
        with context.temp_override(selected_objects=[obj_fibula_dupli], active_object=obj_fibula_dupli, object=obj_fibula_dupli):
            bpy.ops.object.modifier_apply(
                modifier=obj_fibula_dupli.modifiers[0].name
            )
        # remove constraints from dupli and reset location and rotation
        obj_fibula_dupli.constraints.clear()
        if fibula_orig is not None:
            obj_fibula_dupli.location = fibula_orig.location
            obj_fibula_dupli.rotation_euler = fibula_orig.rotation_euler
        else:
            obj_fibula_dupli.location = (0.0, 0.0, 0.0)
            obj_fibula_dupli.rotation_euler = (0.0, 0.0, 0.0)

        # move ob_dupli to proper layer
        move_object_to_collection(
            obj_to_move=obj_fibula_dupli,
            collection_name=constants.COLLECTION_FFF_GEN_FIBULA,
            remove_from_current=True
        )
