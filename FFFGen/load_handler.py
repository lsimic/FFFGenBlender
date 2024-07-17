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
from bpy.app.handlers import persistent

@persistent
def on_load_post_handler(dummy):
    properties = bpy.context.scene.FFFGenPropertyGroup
    if properties.is_initialized:
        # file is being loaded that had the property group set.
        # likely an existing fffgen file.
        # set the orientation to local by default on load (also will happen for old files)
        for idx in range(0, 4):
            bpy.context.scene.transform_orientation_slots[idx].type = "LOCAL"
