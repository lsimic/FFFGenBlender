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
import os


class SaveScreenshot(bpy.types.Operator):
    bl_idname = "fff_gen.save_screenshot"
    bl_label = "Save Screenshot"
    bl_description = "Saves a screenshot of the currently active view."
    bl_options = {'REGISTER', 'UNDO'}

    def find_file_name(self, context):
        properties = context.scene.FFFGenPropertyGroup
        dir_path = properties.screenshot_dir_path # path should be absolute...
        if dir_path.startswith("//"):
            dir_path = bpy.path.abspath(dir_path)
        file_name_base = bpy.context.window.workspace.name # this is the name we use for incrementing...
        index = 1
        file_exists = True
        # find the first file in that dir with the inceremnt that does not exist.
        complete_img_path = ""
        while file_exists: 
            complete_img_path = os.path.join(dir_path, file_name_base + "_" + str(index) + ".png")
            file_exists = os.path.exists(complete_img_path)
            index = index + 1
        
        return complete_img_path

    def execute(self, context):
        complete_img_path = self.find_file_name(context)
        context.scene.render.resolution_x = context.area.width * 2
        context.scene.render.resolution_y = context.area.height * 2

        with context.temp_override():
            bpy.ops.render.opengl(write_still=False)
            bpy.data.images["Render Result"].save_render(complete_img_path)

        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        
        complete_img_path = self.find_file_name(context)
        layout.label(text="Screenshot will be saved to:", icon="INFO")
        layout.label(text=complete_img_path)
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class FFFGenScreenshotPanel(Panel):
    bl_idname = "FFF_GEN_PT_screenshot"
    bl_label = "Screenshot"
    bl_category = "FFF Gen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.FFFGenPropertyGroup
        
        layout.prop(properties, "screenshot_dir_path")

        enable_export = len(properties.screenshot_dir_path) > 0
        if not enable_export:
            layout.label(text="Please set a valid screenshot directory", icon="ERROR")
        sub = layout.row() # export button sub layout
        sub.enabled = enable_export
        sub.operator("fff_gen.save_screenshot", text="Take and save Screenshot") # screenshot button...
