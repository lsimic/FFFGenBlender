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
from .external_loading import load_armature_bone_shape, load_boolean_cube
from . import constants
from . import materials
import os


class InitializeRig(bpy.types.Operator):
    bl_idname = "fff_gen.initialize_rig"
    bl_label = "Initialize FFF Gen Rig"
    bl_description = "Initializes the rigging(armature) and adds all necessary objects, modifiers and constraints"

    # this one is a bit longer, but it does a lot of stuff which to me does not have much sense to separate
    # and i won't do it just for the sake of separating stuff
    def invoke(self, context, event):
        # decimate objects if option is checked
        if(bpy.context.scene.FFFGenPropertyGroup.auto_decimate):
            decimate_objects()
        
        # get original fibula and mandible object, store them in a separate collection...
        obj_mandible = bpy.context.scene.FFFGenPropertyGroup.mandible_object
        obj_fibula = bpy.context.scene.FFFGenPropertyGroup.fibula_object
        move_object_to_collection(
            obj_to_move=obj_mandible,
            collection_name=constants.COLLECTION_ORIGINAL,
            remove_from_current=True
        )
        move_object_to_collection(
            obj_to_move=obj_fibula,
            collection_name=constants.COLLECTION_ORIGINAL,
            remove_from_current=True
        )
        
        # duplicate fibula and mandible
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        override_context = {
            "selected_objects":[obj_mandible]
        }
        bpy.ops.object.duplicate(override_context)
        obj_mandible_copy = bpy.context.selected_objects[0]
        obj_mandible_copy.name = "mandible_copy"
        move_object_to_collection(
            obj_to_move=obj_mandible_copy,
            collection_name=constants.COLLECTION_FFF_GEN_MANDIBLE,
            remove_from_current=True
        )
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        override_context = {
            "selected_objects":[obj_fibula]
        }
        bpy.ops.object.duplicate(override_context)
        obj_fibula_copy = bpy.context.selected_objects[0]
        obj_fibula_copy.name = "fibula_copy"
        move_object_to_collection(
            obj_to_move=obj_fibula_copy,
            collection_name=constants.COLLECTION_FFF_GEN_FIBULA,
            remove_from_current=True
        )

        # deselect all
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        
        # initialize armature and the rig...
        armature = initialize_armature()
        boolean_objects = initialize_boolean_objects(armature)
        
        initialize_mandible_objects(
            armature=armature,
            obj_mandible=obj_mandible_copy,
            objects_boolean_cubes=boolean_objects
        )
        initialize_fibula_objects(
            armature=armature,
            obj_fibula=obj_fibula,
            objects_boolean_cubes=boolean_objects
        )

        # hide original collection
        bpy.data.collections[constants.COLLECTION_ORIGINAL].hide_viewport = True

        # set armature to pose mode...
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(
            mode="POSE"
        )
        bpy.context.view_layer.objects.active = None

        #set materials
        if len(obj_mandible_copy.data.materials):
            obj_mandible_copy.data.materials[0] = materials.get_transparent()
        else:
            obj_mandible_copy.data.materials.append(materials.get_transparent())
        if len(obj_fibula_copy.data.materials):
            obj_fibula_copy.data.materials[0] = materials.get_transparent()
        else:
            obj_fibula_copy.data.materials.append(materials.get_transparent())
        
        # return
        return {"FINISHED"}


def decimate_objects():
    obj_mandible = bpy.context.scene.FFFGenPropertyGroup.mandible_object
    obj_fibula = bpy.context.scene.FFFGenPropertyGroup.fibula_object

    for obj in [obj_mandible, obj_fibula]:
        modifier_decimate = obj.modifiers.new(
            name="decimate",
            type="DECIMATE"
        )
        modifier_decimate.decimate_type = "COLLAPSE"
        ratio = 10000/len(obj.data.polygons)
        if (ratio > 1):
            ratio = 1
        modifier_decimate.ratio = ratio
        override_context = bpy.context.copy()
        override_context["active_object"] = obj
        override_context["selected_objects"] = [obj]
        override_context["object"] = obj
        bpy.ops.object.modifier_apply(override_context, modifier=modifier_decimate.name)


def initialize_armature():
    # add armature object, enter edit mode
    bpy.ops.object.armature_add()
    armature = bpy.context.active_object
    bpy.ops.object.mode_set(
        mode="EDIT"
    )

    # delete default bone
    bpy.ops.armature.select_all(
        action="SELECT"
    )
    bpy.ops.armature.delete()

    # add armature bones
    segment_count = bpy.context.scene.FFFGenPropertyGroup.segment_count
    for i in range(0, segment_count + 1):
        # TODO: the value 3.0(distance between bones) is hard coded here.
        bpy.context.scene.cursor.location = (0.0, i*3.0, 0.0)
        bpy.context.scene.tool_settings.transform_pivot_point = "CURSOR"
        bone_name = "bone." + str(i)
        bpy.ops.armature.bone_primitive_add(
            name=bone_name
        )
        bone = bpy.context.object.data.edit_bones[bone_name]
        bone.tail = (0.0, i*3.0 + 1.0, 0.0)
        bpy.ops.armature.select_all(
            action="DESELECT"
        )
    
    # back to object mode, deselect all objects
    bpy.ops.object.mode_set(
        mode="OBJECT"
    )
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    # reset 3D cursor
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    # reset transform pivot point to back to median
    bpy.context.scene.tool_settings.transform_pivot_point = "MEDIAN_POINT"


    # reset transform pivot point back to median
    bpy.context.scene.tool_settings.transform_pivot_point = "MEDIAN_POINT"

    # add custom bone shape to armature
    obj_bone_shape = load_armature_bone_shape()
    obj_bone_shape.hide_set(True)
    for bone in armature.pose.bones:
        bone.custom_shape = obj_bone_shape
    
    # move to collection
    move_object_to_collection(
        obj_to_move = armature,
        collection_name=constants.COLLECTION_FFF_GEN_MANDIBLE,
        remove_from_current=True
    )

    return armature


def initialize_boolean_objects(armature):
    obj_boolean_cube = load_boolean_cube()
    # duplicate the loaded cubes, assign correct vertex group names and push them to a dictionary
    objects_boolean_cubes = dict()
    segment_count = bpy.context.scene.FFFGenPropertyGroup.segment_count
    for i in range(0, segment_count):
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        obj_boolean_cube_dupli = obj_boolean_cube.copy()
        obj_boolean_cube_dupli.location.y = i*3.0
        obj_boolean_cube_dupli.vertex_groups[0].name = "bone." + str(i)
        obj_boolean_cube_dupli.vertex_groups[1].name = "bone." + str(i + 1)
        obj_boolean_cube_dupli.name = "boolean_cube." + str(i)
        bpy.context.scene.collection.objects.link(obj_boolean_cube_dupli)
        # move to collection
        move_object_to_collection(
            obj_to_move=obj_boolean_cube_dupli,
            collection_name=constants.COLLECTION_FFF_GEN_MANDIBLE,
            remove_from_current=True
        )
        # set armature as parent
        obj_boolean_cube_dupli.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(
            type="ARMATURE"
        )
        # hide it
        obj_boolean_cube_dupli.hide_set(True)
        objects_boolean_cubes[obj_boolean_cube_dupli.name] = obj_boolean_cube_dupli
    
    # unlink the initial cube object
    bpy.context.scene.collection.objects.unlink(obj_boolean_cube)
        
    return objects_boolean_cubes


def initialize_mandible_objects(armature, obj_mandible, objects_boolean_cubes):
    objects_mandible_boolean_cubes = dict()
    last_cube_name = "boolean_cube." + str(len(objects_boolean_cubes)-1)
    for obj_boolean_cube in objects_boolean_cubes.values():
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        override_context = {
            "selected_objects":[obj_boolean_cube]
        }
        bpy.ops.object.duplicate(override_context)
        obj_boolean_cube_dupli = bpy.context.selected_objects[0]
        # scale up to avoid artifacts with boolean modifiers
        if obj_boolean_cube.name != last_cube_name:
            obj_boolean_cube_dupli.scale = (1.2, 1.2, 1.2)
        else:
            obj_boolean_cube_dupli.scale = (1.2, 1.0, 1.2)
        obj_boolean_cube_dupli.name = "mandible_" + obj_boolean_cube.name
        objects_mandible_boolean_cubes[obj_boolean_cube_dupli.name] = obj_boolean_cube_dupli

    # duplicate a mandible object for visualisation
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    override_context = {
        "selected_objects":[obj_mandible]
    }
    bpy.ops.object.duplicate(override_context)
    obj_mandible_dupli = bpy.context.selected_objects[0]
    obj_mandible_dupli.select_set(False)

    # add boolean modifiers...
    for obj in objects_mandible_boolean_cubes.values():
        modifier_boolean = obj_mandible_dupli.modifiers.new(
            name="boolean_difference",
            type="BOOLEAN"
        )
        modifier_boolean.operation = "DIFFERENCE"
        modifier_boolean.object = obj
        # move to proper collection, hide
        move_object_to_collection(
            obj_to_move=obj,
            collection_name=constants.COLLECTION_FFF_GEN_MANDIBLE,
            remove_from_current=True
        )
        obj.hide_set(True)


def initialize_fibula_vectors(segment_count, armature):
    objects_vectors = dict()
    for i in range(0, segment_count):
        # get start and end points for this vector(empty objects)
        bone_start_name = "bone." + str(i)
        bone_end_name = "bone." + str(i+1)

        # create the empty which represents the vector
        bpy.ops.object.empty_add(
            type="ARROWS"
        )
        obj_vector = bpy.context.active_object
        obj_vector.name = "vector." + str(i)

        # assign proper constraints
        constraint_child_of = obj_vector.constraints.new(
            type="CHILD_OF"
        )
        constraint_child_of.target = armature
        constraint_child_of.subtarget = bone_start_name
        constraint_track_to = obj_vector.constraints.new(
            type="TRACK_TO"
        )
        constraint_track_to.target = armature
        constraint_track_to.subtarget = bone_end_name

        move_object_to_collection(
            obj_to_move=obj_vector,
            collection_name=constants.COLLECTION_FFF_GEN_MANDIBLE,
            remove_from_current=True
        )
        obj_vector.hide_set(True)
        objects_vectors[obj_vector.name] = obj_vector
    
    return objects_vectors


def initialize_fibula_duplis(obj_fibula, objects_vectors, objects_boolean_cubes):
    objects_fibula_duplis = dict()

    for counter in range(0, len(objects_vectors.values())):
        # duplicate the fibula object
        obj_vector_empty = objects_vectors["vector." + str(counter)]
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        override_context = {
            "selected_objects":[obj_fibula]
        }
        bpy.ops.object.duplicate(override_context)
        obj_fibula_dupli = bpy.context.selected_objects[0]

        # initial offset on y
        bpy.context.view_layer.objects.active = obj_fibula_dupli
        bpy.ops.transform.translate(
            value=(0.0, counter * (-3.0), 0.0),
            constraint_axis=(False, True, False),
            orient_type='LOCAL'
        )

        obj_fibula_dupli.name = "fibula_object." + str(counter)

        # init constraints
        bpy.context.view_layer.objects.active = obj_fibula_dupli
        constraint_child_of = obj_fibula_dupli.constraints.new(
            type="CHILD_OF"
        )
        constraint_child_of.target = obj_vector_empty

        # init boolean modifier
        obj_boolean_cube = objects_boolean_cubes["boolean_cube." + str(counter)]
        modifier_intersect = obj_fibula_dupli.modifiers.new(
            name="boolean_intersect",
            type="BOOLEAN"
        )
        modifier_intersect.operation = "INTERSECT"
        modifier_intersect.object = obj_boolean_cube

        # move to collection
        move_object_to_collection(
            obj_to_move=obj_fibula_dupli,
            collection_name=constants.COLLECTION_FFF_GEN_MANDIBLE,
            remove_from_current=True
        )

        #set material
        if len(obj_fibula_dupli.data.materials):
            obj_fibula_dupli.data.materials[0] = materials.get_fibula(counter)
        else:
            obj_fibula_dupli.data.materials.append(materials.get_fibula(counter))

        objects_fibula_duplis[obj_fibula_dupli.name] = obj_fibula_dupli
    
    return objects_fibula_duplis


def initialize_fibula_objects(armature, obj_fibula, objects_boolean_cubes):
    # initialize empties/vectors
    # they are used so the fibula fragments can be moved on local axes
    # without affecting orientation.
    segment_count = bpy.context.scene.FFFGenPropertyGroup.segment_count

    objects_vectors = initialize_fibula_vectors(segment_count, armature)

    # initialize fibula duplicate objects(the ones affected by moving the armature bones)
    objects_fibula_duplis = initialize_fibula_duplis(obj_fibula, objects_vectors, objects_boolean_cubes)

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
