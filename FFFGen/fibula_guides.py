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
from .external_loading import load_guide_cube
from .bevel_worldspace import create_bevel_modifier
from . import constants
from . import materials
import os
import math


class CreateFibulaGuide(bpy.types.Operator):
    bl_idname = "fff_gen.create_fibula_guide"
    bl_label = "Create Fibula Guide"
    bl_description = "Creates the fibula guide, adds all necessary objects, modifiers and constraints"

    def invoke(self, context, event):
        obj_fibula = bpy.context.scene.FFFGenPropertyGroup.fibula_object
        objects_cutting_planes = bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_FIBULA].objects

        obj_fibula_guide = create_obj_fibula_guide()
        obj_boolean_union = create_obj_boolean_union(objects_cutting_planes.values())
        obj_boolean_difference = create_obj_boolean_difference(objects_cutting_planes.values())
        obj_boolean_union_limit = create_obj_boolean_union_limit(obj_fibula_guide)
        obj_boolean_difference_limit = create_boj_boolean_difference_limit(obj_fibula_guide)

        setup_fibula_guide_modifiers(obj_fibula_guide, obj_boolean_union, obj_boolean_difference, obj_boolean_union_limit, obj_boolean_difference_limit, obj_fibula)
        obj_boolean_union.hide_set(True)
        obj_boolean_difference.hide_set(True)
        #set material
        if len(obj_fibula_guide.data.materials):
            obj_fibula_guide.data.materials[0] = materials.get_guide()
        else:
            obj_fibula_guide.data.materials.append(materials.get_guide())
        
        bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_FIBULA].hide_viewport = True

        return {"FINISHED"}


def create_obj_fibula_guide():
    obj_fibula_guide = load_guide_cube()
    obj_fibula_guide.name = "fibula_guide"
    move_object_to_collection(
        obj_to_move=obj_fibula_guide,
        collection_name="guide_fibula",
        remove_from_current=True
    )

    return obj_fibula_guide


def create_obj_boolean_union(objects_cutting_planes):
    geom_width = bpy.context.scene.FFFGenPropertyGroup.guide_around_width
    cutting_plane_width = bpy.context.scene.FFFGenPropertyGroup.cutting_plane_thickness
    scale_factor_y = geom_width/cutting_plane_width

    # using list here for easier referencing during iteration
    # create objects that are used for generating fibula gude geometry from exsiting cutting planes
    objects_planes_geometry = list()

    for index, obj_cutting_plane in enumerate(objects_cutting_planes):
        print("insade enumerate cutting planes")
        # duplicate the cutting plane and set origin to geometry so it scales properly
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        obj_cutting_plane.select_set(True)
        bpy.ops.object.duplicate()
        obj_plane_geom = bpy.context.selected_objects[0]
        obj_cutting_plane.select_set(False)
        bpy.ops.object.origin_set(
            type="ORIGIN_GEOMETRY"
        )
        # TODO: this 4.0 is a value that I found appropriate during testing. People might want to change this...
        # HACK - add 0.01 each time it is scaled to avoid boolean issues if the objects are rotated only on Z axis
        # scale the guides using the given scale factors, push to list...
        obj_plane_geom.scale = (4.0+(0.01*index), scale_factor_y, 4.0+(0.01*index))
        objects_planes_geometry.append(obj_plane_geom)

    # join all planes for fibula guide geometry
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    obj_boolean_union = objects_planes_geometry[0]
    obj_boolean_union.select_set(True)
    bpy.context.view_layer.objects.active = obj_boolean_union
    for i in range(1, len(objects_planes_geometry)):
        print("inside joining modifiers")
        modifier_boolean = obj_boolean_union.modifiers.new(
            name="boolean",
            type="BOOLEAN"
        )
        modifier_boolean.operation = "UNION"
        modifier_boolean.object = objects_planes_geometry[i]
        bpy.ops.object.modifier_apply(
            modifier=modifier_boolean.name
        )

    # delete unused objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for i in range(1, len(objects_planes_geometry)):
        print("deleting unused")
        objects_planes_geometry[i].select_set(True)
        bpy.ops.object.delete()
    
    # set sensible name and move to proper collection
    obj_boolean_union.name = "fibula_guide_union"
    move_object_to_collection(
        obj_to_move=obj_boolean_union,
        collection_name=constants.COLLECTION_GUIDE_FIBULA,
        remove_from_current=True
    )

    return obj_boolean_union


def create_obj_boolean_difference(objects_cutting_planes):
    objects_planes_difference = list()

    for index, obj_cutting_plane in enumerate(objects_cutting_planes):
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        obj_cutting_plane.select_set(True)
        bpy.ops.object.duplicate()
        plane_diff = bpy.context.selected_objects[0]
        obj_cutting_plane.select_set(False)
        # TODO: 4.0, same as above
        # HACK - add 0.01 each time it is scaled to avoid boolean issues if the objects are rotated only on Z axis
        plane_diff.scale = (4.0+(0.01*index), 1.0, 4.0+(0.01*index))
        objects_planes_difference.append(plane_diff)

    # join all planes for difference modifier
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    obj_boolean_difference = objects_planes_difference[0]
    obj_boolean_difference.select_set(True)
    bpy.context.view_layer.objects.active = obj_boolean_difference
    for i in range(1, len(objects_planes_difference)):
        modifier_union = obj_boolean_difference.modifiers.new(
            name="boolean_union",
            type="BOOLEAN"
        )
        modifier_union.operation = "UNION"
        modifier_union.object = objects_planes_difference[i]
        bpy.ops.object.modifier_apply(
            modifier=modifier_union.name
        )
    
    # delete unused objects
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for i in range(1, len(objects_planes_difference)):
        objects_planes_difference[i].select_set(True)
    bpy.ops.object.delete()
    # give proper name and move to proper collection
    obj_boolean_difference.name = "fibula_guide_difference"
    move_object_to_collection(
        obj_to_move=obj_boolean_difference,
        collection_name=constants.COLLECTION_GUIDE_FIBULA,
        remove_from_current=True
    )

    return obj_boolean_difference


def create_obj_boolean_union_limit(obj_fibula_guide):
    # create object for intersecting geometry
    # this limits the size of the geometry created by duplicating the cutting planes
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    obj_fibula_guide.select_set(True)
    bpy.ops.object.duplicate()
    obj_boolean_union_limit = bpy.context.selected_objects[0]

    # initial move and scale...
    obj_boolean_union_limit.scale = (1.0, 1.0, 3.0)
    obj_boolean_union_limit.location = (0.9, 0.0, 0.0)

    # parent obj_intersect to main fibula guide object
    obj_boolean_union_limit.select_set(True)
    bpy.context.view_layer.objects.active = obj_fibula_guide
    bpy.ops.object.parent_set(
        type="OBJECT",
        keep_transform=True
    )

    # display wireframe...
    obj_boolean_union_limit.display_type = "WIRE"
    obj_boolean_union_limit.name = "fibula_guide_union_limit"

    move_object_to_collection(
        obj_to_move=obj_boolean_union_limit,
        collection_name=constants.COLLECTION_GUIDE_FIBULA,
        remove_from_current=True
    )

    return obj_boolean_union_limit


def create_boj_boolean_difference_limit(obj_fibula_guide):
    # create object for intersecting with obj_diff
    # this controlls the "depth" of the blade and such
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    obj_fibula_guide.select_set(True)
    bpy.ops.object.duplicate()
    obj_boolean_difference_limit = bpy.context.selected_objects[0]

    # initial move and scale...
    obj_boolean_difference_limit.scale = (3.0, 1.0, 2.0)
    obj_boolean_difference_limit.location = (-0.1, 0.0, 0.0)

    # parent obj_intersect to main fibula guide object
    obj_boolean_difference_limit.select_set(True)
    bpy.context.view_layer.objects.active = obj_fibula_guide
    bpy.ops.object.parent_set(
        type="OBJECT",
        keep_transform=True
    )

    # display wireframe...
    obj_boolean_difference_limit.display_type = "WIRE"
    obj_boolean_difference_limit.name = "fibula_guide_difference_limit"
    move_object_to_collection(
        obj_to_move=obj_boolean_difference_limit,
        collection_name=constants.COLLECTION_GUIDE_FIBULA,
        remove_from_current=True
    )

    return obj_boolean_difference_limit


def setup_fibula_guide_modifiers(obj_fibula_guide, obj_boolean_union, obj_boolean_difference, obj_boolean_union_limit, obj_boolean_difference_limit, obj_fibula):
    bevel_seg = bpy.context.scene.FFFGenPropertyGroup.bevel_segmentcount
    bevel_width = bpy.context.scene.FFFGenPropertyGroup.bevel_width

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    obj_boolean_union.select_set(True)
    bpy.context.view_layer.objects.active = obj_boolean_union
    modifier_boolean_intersect = obj_boolean_union.modifiers.new(
        name="boolean_intersect",
        type="BOOLEAN"
    )
    modifier_boolean_intersect.operation = "INTERSECT"
    modifier_boolean_intersect.object = obj_boolean_union_limit
    obj_boolean_union.select_set(False)

    create_bevel_modifier(obj_boolean_union, "fffgen_bevel_fibula_guide_union", bevel_seg, bevel_width)

    obj_boolean_difference.select_set(True)
    bpy.context.view_layer.objects.active = obj_boolean_difference
    modifier_boolean_intersect = obj_boolean_difference.modifiers.new(
        name="boolean_intersect",
        type="BOOLEAN"
    )
    modifier_boolean_intersect.operation = "INTERSECT"
    modifier_boolean_intersect.object = obj_boolean_difference_limit
    obj_boolean_difference.select_set(False)

    create_bevel_modifier(obj_fibula_guide, "fffgen_bevel_fibula_guide", bevel_seg, bevel_width)

    obj_fibula_guide.select_set(True)
    obj_fibula_guide.scale = (1.0, 8.0, 1.0)
    bpy.context.view_layer.objects.active = obj_fibula_guide

    modifier_boolean_union = obj_fibula_guide.modifiers.new(
        name="boolean_union",
        type="BOOLEAN"
    )
    modifier_boolean_union.operation = "UNION"
    modifier_boolean_union.object = obj_boolean_union
    modifier_boolean_intersect = obj_fibula_guide.modifiers.new(
        name="boolean_intersect",
        type="BOOLEAN"
    )
    modifier_boolean_intersect.operation = "DIFFERENCE"
    modifier_boolean_intersect.object = obj_boolean_difference

    modifier_difference = obj_fibula_guide.modifiers.new(
        name="boolean_difference_fibula",
        type="BOOLEAN"
    )
    modifier_difference.operation = "DIFFERENCE"
    modifier_difference.object = obj_fibula


class CreateFibulaScrew(bpy.types.Operator):
    bl_idname = "fff_gen.create_fibula_screw"
    bl_label = "Create Fibula screw"
    bl_description = "Creates a screw for the fibula guide, and adds all neccesary objects, modifiers and constraints"

    def invoke(self, context, event):
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        obj_fibula_guide = bpy.data.objects["fibula_guide"]

        obj_screw_hole = create_fibula_screw_cylinder()
        # apply initial rotation on y axis 
        bpy.context.view_layer.objects.active = obj_screw_hole
        bpy.ops.object.transform_apply(
            location=False,
            rotation=True,
            scale=False
        )

        setup_screw_hole_constraint(obj_screw_hole, obj_fibula_guide)
        setup_screw_hole_modifiers(obj_screw_hole, obj_fibula_guide)

        # move to proper collection
        obj_fibula_guide.select_set(False)
        move_object_to_collection(
            obj_to_move=obj_screw_hole,
            collection_name=constants.COLLECTION_GUIDE_FIBULA,
            remove_from_current=True
        )

        # select screw hole, make it active
        obj_screw_hole.select_set(True)
        bpy.context.view_layer.objects.active = obj_screw_hole
        return {"FINISHED"}


def create_fibula_screw_cylinder():
    # create a cylinder object with correct scale
    # correct name and correct display type-
    diameter = bpy.context.scene.FFFGenPropertyGroup.screw_hole_diameter
    radius = (diameter*0.1)*0.5
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=4.0,
        location=(0.0, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0)
    )
    obj_screw_hole = bpy.context.active_object
    obj_screw_hole.name = "fibula_guide_screw_hole"
    obj_screw_hole.display_type = "WIRE"
    return obj_screw_hole


def setup_screw_hole_constraint(obj_screw_hole, obj_fibula_guide):
    # add copy rotation constraint so the screw is aligned and perpendicular
    constraint_copy_rotation = obj_screw_hole.constraints.new(
        type="COPY_ROTATION"
    )
    constraint_copy_rotation.target = obj_fibula_guide
    obj_screw_hole.select_set(False)


def setup_screw_hole_modifiers(obj_screw_hole, obj_fibula_guide):
    # add boolean modifier (difference) to fibula guide, using the cylinder as the target
    obj_fibula_guide.select_set(True)
    bpy.context.view_layer.objects.active = obj_fibula_guide
    modifier_boolean = obj_fibula_guide.modifiers.new(
        name="boolean_difference_screw",
        type="BOOLEAN"
    )
    modifier_boolean.operation = "DIFFERENCE"
    modifier_boolean.object = obj_screw_hole
