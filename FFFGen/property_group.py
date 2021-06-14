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
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty, StringProperty


class FFFGenPropertyGroup(PropertyGroup):
    def fibula_update(self, context):
        obj = bpy.context.scene.FFFGenPropertyGroup.fibula_object
        message = ""
        # Y axis should be the longest if oriented properly
        if(obj):
            if(obj.dimensions.y < obj.dimensions.z or obj.dimensions.y < obj.dimensions.x):
                message += "Possible incorrect orientation!  "
            # values between 25 and 70 represent a reasonable size(in cm) for a human fibula + some extra
            # if the size falls out of this range, a warning will be raised.
            # this means that likely, an error occured during the imperial to metric conversion
            # or that an incorrect scale factor (factor of 10) is used.
            # this is simply a warning, and indicates that user should check the scale/size and verify that it is correct
            if(max(obj.dimensions.xyz) > 70 or max(obj.dimensions.xyz) < 25):
                message += "Possible incorrect scale!"
        bpy.context.scene.FFFGenPropertyGroup.fibula_message = message
    
    def mandible_update(self, context):
        obj = bpy.context.scene.FFFGenPropertyGroup.mandible_object
        message = ""
        if(obj):
            # values between 19 and 35 represent a reasonable size(in cm) for a human fibula + some extra
            # if the size falls out of this range, a warning will be raised.
            # this means that likely, an error occured during the imperial to metric conversion
            # or that an incorrect scale factor (factor of 10) is used.
            # this is simply a warning, and indicates that user should check the scale/size and verify that it is correct
            if(sum(obj.dimensions.xyz) < 19 or sum(obj.dimensions.xyz) > 35):
                message += "Possible incorrect scale!"
        bpy.context.scene.FFFGenPropertyGroup.mandible_message = message

    def on_auto_update_toggle(self, context):
        if self.auto_update_toggle == True:
            bpy.ops.fff_gen.auto_update_modal("INVOKE_DEFAULT")
        return

    auto_decimate: BoolProperty(
        default=False,
        description="Decimate objects on initialization",
        name="Auto Decimate"
    )

    auto_update_toggle: BoolProperty(
        default=False,
        update=on_auto_update_toggle,
        description="Toggle auto update function on or off"
    )

    cutting_plane_thickness: FloatProperty(
        name="Cutting plane thickness(in mm)",
        default=0.9,
        description="Thickness of the cutting plane.\nSet this to the thickness of bone saw blade."
    )

    fibula_message: StringProperty(
        name="Fibula message",
        description="Fibula warning/info message",
        default=""
    )

    fibula_object: PointerProperty(
        type=bpy.types.Object,
        name="Fibula object",
        description="Fibula object to use for operator.",
        update=fibula_update
    )

    guide_around_width: FloatProperty(
        name="Width of guide area around the blade(in mm)",
        default=10.0
    )

    is_initialized: BoolProperty(
        name="Is Add-On initialized",
        default=False
    )

    mandible_message: StringProperty(
        name="Mandible message",
        description="Mandible warning/info message",
        default=""
    )

    mandible_object: PointerProperty(
        type=bpy.types.Object,
        name="Mandible object",
        description="Mandible object to use for operator.",
        update=mandible_update
    )

    screw_hole_diameter: FloatProperty(
        name="Diameter of the screw hole(in mm)",
        default=3.0
    )

    segment_count: IntProperty(
        name="Fibula segment count",
        description="Number of individual fibula segments.",
        default=3,
        min=1
    )

    update_rate: FloatProperty(
        name="Update rate(seconds)",
        default=0.2,
        description="How often to update fibula objects when auto update is running.\nChange this based on your system performance"
    )
