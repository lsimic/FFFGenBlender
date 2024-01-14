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
from bpy.types import Panel


# a helper function to create a world-space bevel setup 
# uses goemetry modifiers to bring geo to world space, adds the bevel and then another geometry node modifier to bring it back into local
# a bit hacky, but works well enough. 
# modifier_name should be passed as the hooks on the property will search for modifiers with the name that follow a specific pattern.
def create_bevel_modifier(obj, modifier_name, segments, width):
    nodegroup_objtoworld = None
    nodegroup_worldtoobj = None

    # no need to load/append from file if the node group is already in the current document...
    if "geonode_object_to_world" in bpy.data.node_groups.keys():
        nodegroup_objtoworld = bpy.data.node_groups["geonode_object_to_world"]
    if "geonode_world_to_object" in bpy.data.node_groups.keys():
        nodegroup_worldtoobj = bpy.data.node_groups["geonode_world_to_object"]

    # load node groups if not already loaded...
    if nodegroup_objtoworld is None:
        directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(directory, "geonodes_world_space_bevel.blend")
        with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
            data_to.node_groups = [name for name in data_from.node_groups if name == "geonode_object_to_world"]
        nodegroup_objtoworld = data_to.node_groups[0]
    # load node groups if not already loaded...
    if nodegroup_worldtoobj is None:
        directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(directory, "geonodes_world_space_bevel.blend")
        with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
            data_to.node_groups = [name for name in data_from.node_groups if name == "geonode_world_to_object"]
        nodegroup_worldtoobj = data_to.node_groups[0]

    # create the geo node modifier. first we add object to world.
    mod_objtoworld = obj.modifiers.new(
        name="geo_object_to_world",
        type="NODES"
    )
    mod_objtoworld.node_group = nodegroup_objtoworld
    # create bevel modifier (now bevel will be done in world space)
    mod_bevel = obj.modifiers.new(
        name=modifier_name,
        type="BEVEL"
    )
    mod_bevel.segments = segments
    mod_bevel.width = width
    # create the other geo node modifier to bring back geo into object space.
    mod_worldtoobj = obj.modifiers.new(
        name="geo_world_to_object",
        type="NODES"
    )
    mod_worldtoobj.node_group = nodegroup_worldtoobj

    return mod_bevel


class FFFGenBevelPanel(Panel):
    bl_idname = "FFF_GEN_PT_bevel"
    bl_label = "Bevel"
    bl_category = "FFF Gen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.FFFGenPropertyGroup
        
        layout.prop(properties, "bevel_segmentcount")
        layout.prop(properties, "bevel_width")
