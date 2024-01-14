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
import mathutils
from .move_object_to_collection import move_object_to_collection
from .external_loading import load_guide_cube, load_positioning_aid_objects
from .bevel_worldspace import create_bevel_modifier
from . import constants
from . import materials
import os
import math


class CreateMandibleGuides(bpy.types.Operator):
    bl_idname = "fff_gen.create_mandible_guides"
    bl_label = "Create mandible Guides"
    bl_description = "Creates mandible guides and all necessary objects, modifiers and constraints"

    def invoke(self, context, event):
        create_mandible_visualisation_copy()

        # get mandible planes
        cutting_plane_mandible_end = bpy.data.objects["cutting_plane_mandible_end"]
        cutting_plane_mandible_start = bpy.data.objects["cutting_plane_mandible_start"]

        # call the function
        create_mandible_guide(cutting_plane_mandible_start)
        create_mandible_guide(cutting_plane_mandible_end)

        # hide cutting plane collection
        bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_MANDIBLE].hide_viewport = True
        return {"FINISHED"}


def create_mandible_guide_diff_obj(obj_cutting_plane, name):
    # duplicate the cutting plane, hide the original
    obj_cutting_plane.select_set(True)
    bpy.context.view_layer.objects.active = obj_cutting_plane
    bpy.ops.object.duplicate()
    obj_boolean_diff = bpy.context.selected_objects[0]
    obj_cutting_plane.select_set(False)

    # rename the obj_diff, set display to wire, apply some initial scale
    obj_boolean_diff.name = "mandible_guide_" + name + "_difference"
    obj_boolean_diff.display_type = "WIRE"
    obj_boolean_diff.scale = (1.5, 1.0, 1.2)
    obj_boolean_diff.select_set(False)

    return obj_boolean_diff


def setup_main_mandible_guide(obj_mandible_guide):
    move_object_to_collection(
        obj_to_move=obj_mandible_guide,
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )

    # rotate the mandible_guide, local Z, 180 degrees, scale on z 2x, apply rotation and scale
    obj_mandible_guide.rotation_euler[2] = math.radians(180)
    obj_mandible_guide.scale[2] = 2.0
    obj_mandible_guide.select_set(True)
    bpy.context.view_layer.objects.active = obj_mandible_guide
    bpy.ops.object.transform_apply(
        location=False,
        rotation=True,
        scale=True
    )


def setup_union_mandible_guide(obj_boolean_union, obj_mandible_guide):
    obj_boolean_union.display_type = "WIRE"

    # give some initial scale and location
    obj_boolean_union.location[0] = -0.8
    obj_boolean_union.scale = (1.0, 0.5, 1.1)

    # apply parent relationship
    obj_boolean_union.select_set(True)
    bpy.context.view_layer.objects.active = obj_mandible_guide
    bpy.ops.object.parent_set(
        type="OBJECT",
        keep_transform=True
    )
    # move to collection
    move_object_to_collection(
        obj_to_move=obj_boolean_union,
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )


def setup_mandible_guide_modifiers(obj_mandible, obj_mandible_guide, obj_boolean_diff, obj_boolean_union):
    # add bevel to mandible guide.
    bevel_seg = bpy.context.scene.FFFGenPropertyGroup.bevel_segmentcount
    bevel_width = bpy.context.scene.FFFGenPropertyGroup.bevel_width
    create_bevel_modifier(obj_mandible_guide, "fffgen_bevel_" + obj_mandible_guide.name, bevel_seg, bevel_width)

    create_bevel_modifier(obj_boolean_union, "fffgen_bevel_" + obj_mandible_guide.name, bevel_seg, bevel_width)

    # add modifier (boolean, union) to the mandible_guide
    modifier_union = obj_mandible_guide.modifiers.new(
        name="boolean_union_cutting_guides",
        type="BOOLEAN"
    )
    modifier_union.operation = "UNION"
    modifier_union.object = obj_boolean_union

    # apply modifier (boolean, difference)
    modifier_difference = obj_mandible_guide.modifiers.new(
        name="boolean_difference_cutting_planes",
        type="BOOLEAN"
    )
    modifier_difference.operation = "DIFFERENCE"
    modifier_difference.object = obj_boolean_diff

    # add modifier, difference with mandible object
    modifier_difference = obj_mandible_guide.modifiers.new(
        name="boolean_difference_mandible",
        type="BOOLEAN"
    )
    modifier_difference.operation = "DIFFERENCE"
    modifier_difference.object = obj_mandible


def create_mandible_guide(obj_cutting_plane):
    obj_mandible = bpy.context.scene.FFFGenPropertyGroup.mandible_object
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    
    # name is cutting_plane_mandible_end, or cutting_plane_mandible_start
    # len(cutting_plane_mandible_) = 23
    name = obj_cutting_plane.name[23:]

    # set up obj for boolean diff operation
    obj_boolean_diff = create_mandible_guide_diff_obj(obj_cutting_plane, name)
    move_object_to_collection(
        obj_to_move=obj_boolean_diff,
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )

    # load the cube, set correct name and move to proper collection
    obj_mandible_guide = load_guide_cube()
    obj_mandible_guide.name = "mandible_guide_" + name
    setup_main_mandible_guide(obj_mandible_guide)

    # set uo obj for boolean union operation
    obj_mandible_guide.select_set(True)
    bpy.context.view_layer.objects.active = obj_mandible_guide
    bpy.ops.object.duplicate()
    obj_boolean_union = bpy.context.selected_objects[0]
    obj_boolean_union.name = "mandible_guide_" + name + "_union"
    setup_union_mandible_guide(obj_boolean_union, obj_mandible_guide)
    obj_boolean_union.select_set(False)

    setup_mandible_guide_modifiers(obj_mandible, obj_mandible_guide, obj_boolean_diff, obj_boolean_union)

    # set the rotation and location to same values as the cutting plane
    obj_mandible_guide.location = obj_cutting_plane.location.copy()
    obj_mandible_guide.rotation_euler = obj_cutting_plane.rotation_euler.copy()

    #set material
    if len(obj_mandible_guide.data.materials):
        obj_mandible_guide.data.materials[0] = materials.get_guide()
    else:
        obj_mandible_guide.data.materials.append(materials.get_guide())


def create_mandible_visualisation_copy():
    # create mandible copies used for better visualisation in the guide creation process
    obj_mandible = bpy.data.objects["mandible_copy"]
    obj_mandible_copy = bpy.data.objects["mandible_copy.001"]
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    override_context = {
        "selected_objects":[obj_mandible, obj_mandible_copy]
    }

    # HACK: should make this better, not to reference objects using names(or at least better names...)
    bpy.ops.object.duplicate(override_context)
    move_object_to_collection(
        obj_to_move=bpy.data.objects["mandible_copy.002"],
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )
    move_object_to_collection(
        obj_to_move=bpy.data.objects["mandible_copy.003"],
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )
    for selected in bpy.context.selected_objects:
        selected.select_set(False)


class CreateMandibleStartScrew(bpy.types.Operator):
    bl_idname = "fff_gen.create_mandible_start_screw"
    bl_label = "Create Mandible Start Screw"
    bl_description = "Creates a screw on the start side, and adds all neccesary objects, modifiers and constraints"

    def invoke(self, context, event):
        mandible_guide_start = bpy.data.objects["mandible_guide_start"]
        if "positioning_aid_start" in bpy.data.objects.keys():
            mandible_positioning_aid = bpy.data.objects["positioning_aid_start"]
        else:
            mandible_positioning_aid = None
        create_mandible_screw(mandible_guide_start, mandible_positioning_aid, "start")
        return {"FINISHED"}


class CreateMandibleEndScrew(bpy.types.Operator):
    bl_idname = "fff_gen.create_mandible_end_screw"
    bl_label = "Create Mandible End Screw"
    bl_description = "Creates a screw on the end side, and adds all neccesary objects, modifiers and constraints"

    def invoke(self, context, event):
        mandible_guide_end = bpy.data.objects["mandible_guide_end"]
        if "positioning_aid_end" in bpy.data.objects.keys():
            mandible_positioning_aid = bpy.data.objects["positioning_aid_end"]
        else:
            mandible_positioning_aid = None
        create_mandible_screw(mandible_guide_end, mandible_positioning_aid, "end")
        return {"FINISHED"}


class JoinMandibleGuides(bpy.types.Operator):
    bl_idname = "fff_gen.join_mandible_guides"
    bl_label = "Join mandible guides"
    bl_description = "Connects start and end mandible guides with a simple objects and merges them together"

    def invoke(self, context, event):
        obj_guide_start = bpy.data.objects["mandible_guide_start"]
        obj_guide_end = bpy.data.objects["mandible_guide_end"]
        obj_mandible = bpy.context.scene.FFFGenPropertyGroup.mandible_object

        obj_guide = create_mandible_guide_join_cube(obj_guide_start, obj_guide_end)
        setup_mandible_joined_modifiers(obj_guide_start, obj_guide_end, obj_mandible, obj_guide)

        # set material
        if len(obj_guide.data.materials):
            obj_guide.data.materials[0] = materials.get_guide()
        else:
            obj_guide.data.materials.append(materials.get_guide())
        
        return {"FINISHED"}


def compute_positioning_aid_matrix(cutting_plane_obj, mandible_guide_obj):
    cutting_plane_mat_norm = cutting_plane_obj.matrix_world.normalized()
    guide_obj_pos = mandible_guide_obj.matrix_world.translation
    guide_obj_dim = mandible_guide_obj.dimensions

    # compute the size of the positioning aid...
    # x, z dimension can be split.
    # y dimension is computed by checking the distance from origin to plane and split y dim
    y_dist = (guide_obj_pos - cutting_plane_mat_norm.translation).dot(cutting_plane_mat_norm.col[1])
    positioning_aid_size = mathutils.Vector((guide_obj_dim.x, 0.5 * guide_obj_dim.y + y_dist, 0.5 * guide_obj_dim.z))

    # compute the location of the positioning aid...
    # by projecting the origin of guide_obj onto the cutting plane
    # and then offseting it by the width in local X direction. and the height in local z direction.
    # then, the rotation part of the matrix is same as the plane matrix. 
    projected_origin = guide_obj_pos - y_dist * cutting_plane_mat_norm.col[1].to_3d()
    projected_origin = projected_origin - cutting_plane_mat_norm.col[0].to_3d() * 0.5 * guide_obj_dim.x
    projected_origin = projected_origin + cutting_plane_mat_norm.col[2].to_3d() * 0.25 * guide_obj_dim.y

    # build the matrix.
    # use size as scale, because the loaded objects are stored normalized
    positioning_aid_matrix = mathutils.Matrix.LocRotScale(projected_origin, cutting_plane_mat_norm.to_quaternion(), positioning_aid_size)
    return positioning_aid_matrix


class CreateMandiblePositioningAid(bpy.types.Operator):
    bl_idname = "fff_gen.create_mandible_positioning_aid"
    bl_label = "Create mandible positioning aid"
    bl_description = "Creates the mandible positioning aid using the existing mandible guide objects"

    def invoke(self, context, event):
        # get the needed collections
        collection_mandible_guide = bpy.data.collections[constants.COLLECTION_GUIDE_MANDIBLE]

        # load the required objects from the scene
        load_positioning_aid_objects()
        obj_positioning_aid_curve = bpy.data.objects["positioning_aid_curve"]
        obj_positioning_aid_curve_handle_start = bpy.data.objects["positioning_aid_curve_handle_start"]
        obj_positioning_aid_curve_handle_end = bpy.data.objects["positioning_aid_curve_handle_end"]
        obj_positioning_aid_start = bpy.data.objects["positioning_aid_start"]
        obj_positioning_aid_end = bpy.data.objects["positioning_aid_end"]
        obj_positioning_aid = bpy.data.objects["positioning_aid_mesh"]

        # move loaded objects to collections...
        move_object_to_collection(
            obj_to_move=obj_positioning_aid_curve,
            collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
            remove_from_current=True
        )
        move_object_to_collection(
            obj_to_move=obj_positioning_aid_start,
            collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
            remove_from_current=True
        )
        move_object_to_collection(
            obj_to_move=obj_positioning_aid_end,
            collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
            remove_from_current=True
        )
        move_object_to_collection(
            obj_to_move=obj_positioning_aid_curve_handle_start,
            collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
            remove_from_current=True
        )
        move_object_to_collection(
            obj_to_move=obj_positioning_aid_curve_handle_end,
            collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
            remove_from_current=True
        )
        move_object_to_collection(
            obj_to_move=obj_positioning_aid,
            collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
            remove_from_current=True
        )

        # compute the matrix for positioning aid start/end parts
        # it will have the scale/translation/rotation components set in such a way that it aligns well with existing objects.
        pos_aid_matrix_start = compute_positioning_aid_matrix(bpy.data.objects["mandible_guide_start_difference"], bpy.data.objects["mandible_guide_start"])
        pos_aid_matrix_end = compute_positioning_aid_matrix(bpy.data.objects["mandible_guide_end_difference"], bpy.data.objects["mandible_guide_end"])

        # set the matrix for start/end
        obj_positioning_aid_start.matrix_world = pos_aid_matrix_start
        obj_positioning_aid_end.matrix_world = pos_aid_matrix_end

        # set the matrix for curve handles...
        obj_positioning_aid_curve_handle_start.matrix_world = pos_aid_matrix_start
        obj_positioning_aid_curve_handle_end.matrix_world = pos_aid_matrix_end

        # add boolean modifiers with the mandible objects where necessary (for start and end of positioning aid)
        # the rest of the booleans to merge the positioning aid together already exist on the curve object.
        modifier_difference_start = obj_positioning_aid_start.modifiers.new(
            name="boolean_difference_mandible",
            type="BOOLEAN"
        )
        modifier_difference_start.operation = "DIFFERENCE"
        modifier_difference_start.object = bpy.context.scene.FFFGenPropertyGroup.mandible_object
        
        modifier_difference_end = obj_positioning_aid_end.modifiers.new(
            name="boolean_difference_mandible",
            type="BOOLEAN"
        )
        modifier_difference_end.operation = "DIFFERENCE"
        modifier_difference_end.object = bpy.context.scene.FFFGenPropertyGroup.mandible_object


        # TODO: (Luka) add constraint, copy location, y axis, both target and owner in local_space. 
        # this makes sure that the positioning aid will remain aligned with the guide when translated.
        # scaling will not misalign it, as the origin is on the cutting plane.

        # find existing screws for start, end 
        objects_screw_start = []
        objects_screw_end = []
        for obj in collection_mandible_guide.objects:
            if obj.name_full.startswith("mandible_guide_start_screw_hole"):
                objects_screw_start.append(obj)
            elif obj.name_full.startswith("mandible_guide_end_screw_hole"):
                objects_screw_end.append(obj)

        # init the boolean modifiers for start using the existing screws
        for screw_start_obj in objects_screw_start:
            obj_positioning_aid_start.select_set(True)
            bpy.context.view_layer.objects.active = obj_positioning_aid_start
            modifier_mandible_aid_screw = obj_positioning_aid_start.modifiers.new(
                name="boolean_difference_screw",
                type="BOOLEAN"
            )
            modifier_mandible_aid_screw.operation = "DIFFERENCE"
            modifier_mandible_aid_screw.object = screw_start_obj
            obj_positioning_aid_start.select_set(False)
        
        # init the boolean modifiers for end using the existing screws
        for screw_end_obj in objects_screw_end:
            obj_positioning_aid_end.select_set(True)
            bpy.context.view_layer.objects.active = obj_positioning_aid_end
            modifier_mandible_aid_screw = obj_positioning_aid_end.modifiers.new(
                name="boolean_difference_screw",
                type="BOOLEAN"
            )
            modifier_mandible_aid_screw.operation = "DIFFERENCE"
            modifier_mandible_aid_screw.object = screw_end_obj
            obj_positioning_aid_end.select_set(False)

        return {"FINISHED"}


def create_mandible_screw_cylinder(obj_mandible_guide, name):
    diameter = bpy.context.scene.FFFGenPropertyGroup.screw_hole_diameter
    radius = (diameter * 0.1) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=4.0,
        location=obj_mandible_guide.location,
        rotation=(0.0, math.radians(90.0), 0.0)
    )

    # set the correct name, wire display
    obj_screw_hole = bpy.context.active_object
    obj_screw_hole.name = "mandible_guide_" + name + "_screw_hole"
    obj_screw_hole.display_type = "WIRE"

    return obj_screw_hole


def setup_mandible_screw_constraints(obj_mandible_guide, obj_screw_hole):
    constraint_copy_rotation = obj_screw_hole.constraints.new(
        type="COPY_ROTATION"
    )
    constraint_copy_rotation.target = obj_mandible_guide
    obj_screw_hole.select_set(False)


def setup_mandible_screw_modifiers(obj_mandible_guide, obj_positioning_aid, obj_screw_hole):
    # add boolean modifier to mandible guide
    obj_mandible_guide.select_set(True)
    bpy.context.view_layer.objects.active = obj_mandible_guide
    modifier_mandible_screw = obj_mandible_guide.modifiers.new(
        name="boolean_difference_screw",
        type="BOOLEAN"
    )
    modifier_mandible_screw.operation = "DIFFERENCE"
    modifier_mandible_screw.object = obj_screw_hole
    obj_mandible_guide.select_set(False)

    # add boolean modifier to mandible positioning aid
    if obj_positioning_aid is not None:
        obj_positioning_aid.select_set(True)
        bpy.context.view_layer.objects.active = obj_positioning_aid
        modifier_mandible_screw = obj_positioning_aid.modifiers.new(
            name="boolean_difference_screw",
            type="BOOLEAN"
        )
        modifier_mandible_screw.operation = "DIFFERENCE"
        modifier_mandible_screw.object = obj_screw_hole
        obj_positioning_aid.select_set(False)


def create_mandible_screw(obj_mandible_guide, obj_positioning_aid, name):
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    # add a cylinder, with the correct dimensions
    obj_screw_hole = create_mandible_screw_cylinder(obj_mandible_guide, name)

    # add copy rotation constraint to cylinder, apply initial rotation on y axis
    bpy.context.view_layer.objects.active = obj_screw_hole
    bpy.ops.object.transform_apply(
        location=False,
        rotation=True,
        scale=False
    )

    setup_mandible_screw_constraints(obj_mandible_guide, obj_screw_hole)

    # add boolean modifier (difference) to mandible guide, using the cylinder as the target
    setup_mandible_screw_modifiers(obj_mandible_guide, obj_positioning_aid, obj_screw_hole)

    # select screw hole, make it active when the function finishes
    # so it can be moved easily by the user without the need to select.
    obj_mandible_guide.select_set(False)
    move_object_to_collection(
        obj_to_move=obj_screw_hole,
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )
    obj_screw_hole.select_set(True)
    bpy.context.view_layer.objects.active = obj_screw_hole


def create_mandible_guide_join_cube(obj_guide_start, obj_guide_end):
    # create a cube, at center point between objects
    co = (obj_guide_end.location + obj_guide_start.location) / 2
    bpy.ops.mesh.primitive_cube_add(size=1.0, enter_editmode=False, location=co)
    obj_guide = bpy.context.active_object
    obj_guide.name = "joined_mandible_guide"
    # offset it on z axis lower
    z_dist = (obj_guide_start.dimensions[2] + obj_guide_end.dimensions[2]) / 4
    obj_guide.location[2] -= z_dist

    # move to proper collection
    move_object_to_collection(
        obj_to_move=obj_guide,
        collection_name=constants.COLLECTION_GUIDE_MANDIBLE,
        remove_from_current=True
    )

    # calculate distance between start and end guides
    dist = (obj_guide_start.location - obj_guide_end.location).length
    obj_guide.scale[0] = 1.1 * dist
    obj_guide.scale[1] = 0.2 * dist
    obj_guide.scale[2] = 0.1 * dist

    # set initial rotation to follow the line between two guides
    vec_1 = obj_guide_start.location - obj_guide_end.location
    vec_1.normalize()
    obj_guide.rotation_euler = vec_1.to_track_quat('X', 'Z').to_euler()

    return obj_guide


def setup_mandible_joined_modifiers(obj_guide_start, obj_guide_end, obj_mandible, obj_guide):
    # mandible guide bevel...
    bevel_seg = bpy.context.scene.FFFGenPropertyGroup.bevel_segmentcount
    bevel_width = bpy.context.scene.FFFGenPropertyGroup.bevel_width
    create_bevel_modifier(obj_guide, "fffgen_bevel_" + obj_guide.name, bevel_seg, bevel_width)

    # add bolean modifier difference(with mandible)
    mod_difference = obj_guide.modifiers.new(
        name="boolean_difference",
        type="BOOLEAN"
    )
    mod_difference.operation = "DIFFERENCE"
    mod_difference.object = obj_mandible

    # add boolean modifier unions with guide objects
    mod_union_start = obj_guide.modifiers.new(
        name="boolean_union_start",
        type="BOOLEAN"
    )
    mod_union_start.operation = "UNION"
    mod_union_start.object = obj_guide_start
    mod_union_end = obj_guide.modifiers.new(
        name="boolean_union_end",
        type="BOOLEAN"
    )
    mod_union_end.operation = "UNION"
    mod_union_end.object = obj_guide_end
