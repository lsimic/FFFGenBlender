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


def load_guide_cube():
    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(directory, "guide_cube.blend")
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name == "guide_cube"]
    obj_guide_cube = data_to.objects[0]
    bpy.context.scene.collection.objects.link(obj_guide_cube)
    return obj_guide_cube


def load_cutting_planes():
    cutting_plane_start = None
    cutting_plane_end = None
    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(directory, "cutting_plane.blend")
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith("cutting_plane")]
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.scene.collection.objects.link(obj)
            if obj.name == "cutting_plane_start":
                cutting_plane_start = obj
            if obj.name == "cutting_plane_end":
                cutting_plane_end = obj
    return [cutting_plane_start, cutting_plane_end]


def load_armature_bone_shape():
    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(directory, "armature_bone_shape.blend")
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name == "armature_bone_shape"]
    obj_bone_shape = data_to.objects[0]
    bpy.context.scene.collection.objects.link(obj_bone_shape)
    return obj_bone_shape


def load_boolean_cube():
    # load cube with predefined vertex groups for use with boolean operation and armature parenting
    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(directory, "boolean_cube.blend")
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name == "boolean_cube"]
    obj_boolean_cube = data_to.objects[0]
    bpy.context.scene.collection.objects.link(obj_boolean_cube)
    return obj_boolean_cube
