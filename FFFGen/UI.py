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
from bpy.types import PropertyGroup, Panel
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from . import constants


class FFFGenGeneralPanel(Panel):
    bl_idname = "FFF_GEN_PT_general"
    bl_label = "General"
    bl_category = "FFF Gen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.FFFGenPropertyGroup

        if properties.is_initialized:
            if not len(bpy.data.collections[constants.COLLECTION_ORIGINAL].objects):
                box = layout.box()
                box.label(text="General Settings")
                box.prop_search(
                    data=properties,
                    property="fibula_object",
                    search_data=context.scene,
                    search_property="objects",
                    icon="OBJECT_DATA",
                    text="Fibula object"
                )
                if(properties.fibula_message):
                    box.label(text=properties.fibula_message, icon="ERROR")
                box.prop_search(
                    data=properties,
                    property="mandible_object",
                    search_data=context.scene,
                    search_property="objects",
                    icon="OBJECT_DATA",
                    text="Mandible object"
                )
                if(properties.mandible_message):
                    box.label(text=properties.mandible_message, icon="ERROR")
                box.prop(properties, "segment_count")
                box.prop(properties, "auto_decimate")
                box = layout.box()
                box.label(text="Initialize objects:")
                box.operator("fff_gen.initialize_rig", text="Initialize objects")
            else:
                if bpy.context.window.workspace.name == constants.WORKSPACE_POSITIONING and not len(bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_MANDIBLE].objects):
                    box = layout.box()
                    box.label(text="Update settings")
                    box.prop(properties, "update_rate")
                    label = "Auto update is ON" if properties.auto_update_toggle else "Auto update is OFF"
                    box.prop(properties, "auto_update_toggle", text=label, toggle=True)
                    box.operator("fff_gen.update", text="update bone fragments")
        else:
            box = layout.box()
            box.operator("fff_gen.initialize_addon", text="Initialize Add-On")


class FFFGenGuidesPanel(Panel):
    bl_idname = "FFF_GEN_PT_guides"
    bl_label = "Guides"
    bl_category = "FFF Gen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.FFFGenPropertyGroup

        if properties.is_initialized and bpy.context.window.workspace.name == constants.WORKSPACE_POSITIONING:
            if not len(bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_MANDIBLE].objects) and len(bpy.data.collections[constants.COLLECTION_FFF_GEN_FIBULA].objects):
                box = layout.box()
                box.label(text="cutting planes:")
                box.prop(properties, "cutting_plane_thickness")
                box.operator("fff_gen.initialize_cutting_planes", text="Generate cutting planes")

        if properties.is_initialized and (bpy.context.window.workspace.name == constants.WORKSPACE_MANDIBLE_GUIDES or bpy.context.window.workspace.name == constants.WORKSPACE_FIBULA_GUIDES):
            if ((len(bpy.data.collections[constants.COLLECTION_GUIDE_FIBULA].objects) and bpy.context.window.workspace.name == constants.WORKSPACE_FIBULA_GUIDES)
            or (len(bpy.data.collections[constants.COLLECTION_GUIDE_MANDIBLE].objects) and bpy.context.window.workspace.name == constants.WORKSPACE_MANDIBLE_GUIDES)):
                box = layout.box()
                box.label(text="settings:")
                box.prop(properties, "screw_hole_diameter")

        if properties.is_initialized and (bpy.context.window.workspace.name == constants.WORKSPACE_FIBULA_GUIDES):
            box = layout.box()
            box.label(text="Fibula Guides:")
            if not len(bpy.data.collections[constants.COLLECTION_GUIDE_FIBULA].objects):
                if len(bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_FIBULA].objects):
                    box.operator("fff_gen.create_fibula_guide", text="Generate Fibula guide")
            else:
                box.operator("fff_gen.create_fibula_screw", text="Create Fibula guide screw")

        if properties.is_initialized and (bpy.context.window.workspace.name == constants.WORKSPACE_MANDIBLE_GUIDES):
            layout.prop(properties, "positioning_aid_toggle")
            box = layout.box()
            box.label(text="Mandible Guides:")
            if not len(bpy.data.collections[constants.COLLECTION_GUIDE_MANDIBLE].objects):
                if len(bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_MANDIBLE].objects):
                    box.operator("fff_gen.create_mandible_guides", text="Create Mandible Guides")
            else:
                box.operator("fff_gen.create_mandible_start_screw", text="Create Mandible Start Screw")
                box.operator("fff_gen.create_mandible_end_screw", text="Create Mandible End Screw")
                if properties.positioning_aid_toggle == "GUIDE":
                    if not "joined_mandible_guide" in bpy.data.objects.keys():
                        box.operator("fff_gen.join_mandible_guides", text="Join mandible guides")
                else:
                    # try to find the positioning aid object
                    # if found - it is initialized
                    # otherwise - it is not initialized and show the button to do so.
                    if not "positioning_aid_mesh" in bpy.data.objects.keys():
                        box.operator("fff_gen.create_mandible_positioning_aid", text="Create positioning aid")
                    else:
                        # Property to adjust scale/thickness
                        box.prop(properties, "positioning_aid_size_x")
                        box.prop(properties, "positioning_aid_size_z")


class FFFGenDangerPanel(Panel):
    bl_idname = "FFF_GEN_PT_danger"
    bl_label = "Danger Zone"
    bl_category = "FFF Gen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.FFFGenPropertyGroup
        col = layout.column()

        if properties.is_initialized and (bpy.context.window.workspace.name == constants.WORKSPACE_FIBULA_GUIDES):
            if len(bpy.data.collections[constants.COLLECTION_GUIDE_FIBULA].objects):
                col.operator("fff_gen.clear_fibula_guides", text="Clear Fibula Guides")
        
        if properties.is_initialized and (bpy.context.window.workspace.name == constants.WORKSPACE_MANDIBLE_GUIDES):
            if properties.positioning_aid_toggle == "GUIDE":
                if len(bpy.data.collections[constants.COLLECTION_GUIDE_MANDIBLE].objects):
                    col.operator("fff_gen.clear_mandible_guides", text="Clear Mandible Guides")
            else:
                if "positioning_aid_mesh" in bpy.data.objects.keys():
                    col.operator("fff_gen.clear_mandible_positioning_aid", text="Clear positioning aid")
        
        if properties.is_initialized and (bpy.context.window.workspace.name == constants.WORKSPACE_POSITIONING):
            if len(bpy.data.collections[constants.COLLECTION_CUTTING_PLANES_FIBULA].objects):
                col.operator("fff_gen.clear_cutting_planes", text="Clear Cutting Planes")
            if len(bpy.data.collections[constants.COLLECTION_ORIGINAL].objects):
                col.operator("fff_gen.clear_all", text="Clear all")


class FFFGenColorPanel(Panel):
    bl_idname = "FFF_GEN_PT_color"
    bl_label = "Color"
    bl_category = "FFF Gen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.active_object
        if obj is not None:
            if hasattr(obj.data, "materials"):
                if len(obj.data.materials):
                    row = layout.row()
                    row.prop(obj.data.materials[0], "diffuse_color")

