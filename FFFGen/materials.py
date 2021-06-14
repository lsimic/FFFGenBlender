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


def get_transparent():
    mat = bpy.data.materials.get("Transparent")
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Transparent")
        mat.diffuse_color = (1, 1, 1, 0.5)
    return mat


def get_fibula(index):
    mat = bpy.data.materials.get("Fibula" + str(index))
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Fibula" + str(index))
        col = mathutils.Color((0.0, 0.0, 1.0))
        col.h = 0.1*index
        col.s = 0.75
        col.v = 1
        mat.diffuse_color = (col.r, col.g, col.b, 1)
    return mat


def get_guide():
    mat = bpy.data.materials.get("Guide")
    if mat is None:
        mat = bpy.data.materials.new(name="Guide")
        col = mathutils.Color((0.0, 0.0, 1.0))
        col.h = 0.8
        col.s = 0.75
        col.v = 1
        mat.diffuse_color = (col.r, col.g, col.b, 1)
    return mat