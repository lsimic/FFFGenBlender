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


def move_object_to_collection(obj_to_move, collection_name, remove_from_current):
    if remove_from_current:
        for collection in obj_to_move.users_collection:
            collection.objects.unlink(obj_to_move)
    bpy.data.collections[collection_name].objects.link(obj_to_move)
    # TODO: toggle local visibility off/on to force viewport update...
    # do this by deducting the viewport from the collection name, and fetching the viewport space...