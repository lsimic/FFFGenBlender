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
from .external_loading import load_cutting_planes
import os


class InitializeCuttingPlanes(bpy.types.Operator):
    bl_idname = "fff_gen.initialize_cutting_planes"
    bl_label = "Initialize Cutting Planes"
    bl_description = "Creates cutting planes, and displays them in appropriate workspaces"

    def invoke(self, context, event):
        # get the armature
        armature = bpy.data.objects["Armature"]

        # load cutting planes from the external file...
        loaded_planes = load_cutting_planes()
        cutting_plane_start_orig = loaded_planes[0]
        cutting_plane_end_orig = loaded_planes[1]

        # crate duplicates of loaded cutting planes at correct, apply their transforms
        # and move them to proper location in relation to the fibula.
        objects_cutting_planes = setup_cutting_planes(
            cutting_plane_start_orig, 
            cutting_plane_end_orig, 
            armature
        )
        apply_cutting_plane_transforms(objects_cutting_planes.values())
        set_cutting_plane_positions(objects_cutting_planes)

        # remove original cutting planes, and move the duplicates to proper layers.
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        cutting_plane_start_orig.select_set(True)
        cutting_plane_end_orig.select_set(True)
        bpy.ops.object.delete()
        move_cutting_planes_to_layers(objects_cutting_planes.values())
        return {"FINISHED"}


def apply_cutting_plane_transforms(cutting_planes):
    # apply visual transform for all cutting planes, and remove the constraints one applied
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for cutting_plane_dupli in cutting_planes:
        cutting_plane_dupli.select_set(True)
        bpy.context.view_layer.objects.active = cutting_plane_dupli
        bpy.ops.object.visual_transform_apply()
        bpy.ops.object.constraints_clear()
        cutting_plane_dupli.select_set(False)


def move_cutting_planes_to_layers(cutting_planes):
    for obj in cutting_planes:
        if obj.name.startswith("cutting_plane_fibula_"):
            move_object_to_collection(
                obj_to_move=obj,
                collection_name=constants.COLLECTION_CUTTING_PLANES_FIBULA,
                remove_from_current=True
            )
        else:
            move_object_to_collection(
                obj_to_move=obj,
                collection_name=constants.COLLECTION_CUTTING_PLANES_MANDIBLE,
                remove_from_current=True
            )


def set_cutting_plane_positions(objects_cutting_planes):
    # TODO: find a better way to do this
    # perhaps using matrix world to copy transformations
    # duplicates the fibula dupli object, applies its constraints and visual transforms
    # parents the cutting plane to the fibula object
    # then resets the location and rotation of the fibula object...

    # get fibula graft objects
    objects_fibula = dict()
    for obj in bpy.data.objects:
        if obj.name.startswith("fibula_object"):
            objects_fibula[obj.name] = obj

    for obj_fibula in objects_fibula.values():
        # duplicate the fibula object
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        obj_fibula.select_set(True)
        bpy.ops.object.duplicate()
        obj_fibula_dupli = bpy.context.selected_objects[0]
        obj_fibula.select_set(False)

        # assign ob_dupli as parent (use keep transform)
        index = obj_fibula.name[14:]
        obj_plane_start = objects_cutting_planes["cutting_plane_fibula_start." + index]
        obj_plane_end = objects_cutting_planes["cutting_plane_fibula_end." + index]
        obj_plane_start.select_set(True)
        obj_plane_end.select_set(True)
        bpy.context.view_layer.objects.active = obj_fibula_dupli
        bpy.ops.object.parent_set(
            type="OBJECT",
            keep_transform=True
        )

        # reset the location of fibula dupli by clearing the constraints and setting the location and rotation to 0
        obj_plane_start.select_set(False)
        obj_plane_end.select_set(False)
        bpy.context.view_layer.objects.active = obj_fibula_dupli
        bpy.ops.object.constraints_clear()
        obj_fibula_dupli.location = (0.0, 0.0, 0.0)
        obj_fibula_dupli.rotation_euler = (0.0, 0.0, 0.0)

        # clear the parent relationship, but keep the transformations to keep planes in place
        obj_fibula_dupli.select_set(False)
        obj_plane_start.select_set(True)
        obj_plane_end.select_set(True)
        bpy.ops.object.parent_clear(
            type='CLEAR_KEEP_TRANSFORM'
        )

        # delete duplicated fibula object...
        obj_plane_start.select_set(False)
        obj_plane_end.select_set(False)
        obj_fibula_dupli.select_set(True)
        bpy.ops.object.delete()


def setup_cutting_planes(cutting_plane_start_orig, cutting_plane_end_orig, armature):
    # iterate over armature bones, duplicate cutting planes and move them to bone positions...

    objects_cutting_planes = dict()
    thickness_sf = bpy.context.scene.FFFGenPropertyGroup.cutting_plane_thickness

    for index, bone in enumerate(armature.pose.bones):
        # duplicate start and end cutting planes
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        cutting_plane_start_orig.select_set(True)
        bpy.ops.object.duplicate()
        cutting_plane_start_dupli = bpy.context.selected_objects[0]
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        cutting_plane_end_orig.select_set(True)
        bpy.ops.object.duplicate()
        cutting_plane_end_dupli = bpy.context.selected_objects[0]
        for obj in bpy.context.selected_objects:
            obj.select_set(False)

        # for both cutting planes apply scale factor and add constraints
        for cutting_plane_dupli in [cutting_plane_start_dupli, cutting_plane_end_dupli]:
            # set scale for correct plane thickness and apply visuzal transform for scale
            cutting_plane_dupli.scale[1] = thickness_sf
            cutting_plane_dupli.select_set(True)
            bpy.context.view_layer.objects.active = cutting_plane_dupli
            bpy.ops.object.transform_apply(
                location=False,
                rotation=False,
                scale=True
            )
            # add constraints
            constraint_child_of = cutting_plane_dupli.constraints.new(
                type="CHILD_OF"
            )
            constraint_child_of.target = armature
            constraint_child_of.subtarget = bone.name
            bpy.ops.constraint.childof_clear_inverse(constraint=constraint_child_of.name, owner="OBJECT")
            cutting_plane_dupli.select_set(False)
            bpy.context.view_layer.objects.active = None

        # rename duplicated cutting planes
        cutting_plane_start_dupli.name = "cutting_plane_fibula_start." + str(index)
        cutting_plane_end_dupli.name = "cutting_plane_fibula_end." + str(index - 1)
        if index == 0:
            cutting_plane_end_dupli.name = "cutting_plane_mandible_end"
        if index == (len(armature.pose.bones)-1):
            cutting_plane_start_dupli.name = "cutting_plane_mandible_start"

        # append to duplicated cutting planes to a dictionary
        objects_cutting_planes[cutting_plane_start_dupli.name] = cutting_plane_start_dupli
        objects_cutting_planes[cutting_plane_end_dupli.name] = cutting_plane_end_dupli

    # return the correctly positioned duplicated cutting planes
    return objects_cutting_planes
