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
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty, StringProperty, EnumProperty


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
        if (obj):
            # values between 19 and 35 represent a reasonable size(in cm) for a human fibula + some extra
            # if the size falls out of this range, a warning will be raised.
            # this means that likely, an error occured during the imperial to metric conversion
            # or that an incorrect scale factor (factor of 10) is used.
            # this is simply a warning, and indicates that user should check the scale/size and verify that it is correct
            if (sum(obj.dimensions.xyz) < 19 or sum(obj.dimensions.xyz) > 35):
                message += "Possible incorrect scale!"
        bpy.context.scene.FFFGenPropertyGroup.mandible_message = message

    def positioning_aid_toggle_update(self, context):
        # when the toggle between guide/positioning aid is selected
        # toggle the visibility of objects.
        # an attempt was made with collections, but it does not work well
        # as the order of local collection changes if file from previous version is opened
        # and the API does not provide a nice way to access the local collection data...
        is_guide = self.positioning_aid_toggle == "GUIDE"

        guide_object_names = [
            "joined_mandible_guide",
            "mandible_guide_end",
            "mandible_guide_end_union",
            "mandible_guide_start",
            "mandible_guide_start_union"
        ]
        positioning_aid_object_names = [
            "positioning_aid_curve",
            "positioning_aid_curve_handle_start",
            "positioning_aid_curve_handle_end",
            "positioning_aid_start",
            "positioning_aid_end",
            "positioning_aid_mesh"
        ]

        # common objects (eg screws, plane, etc... remain visible all the time and are not toggled)
        for obj_name in guide_object_names:
            if obj_name in bpy.data.objects.keys():
                bpy.data.objects[obj_name].hide_set(not is_guide)
        for obj_name in positioning_aid_object_names:
            if obj_name in bpy.data.objects.keys():
                bpy.data.objects[obj_name].hide_set(is_guide)
        return

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

    positioning_aid_toggle: EnumProperty(
        items=[
            ("GUIDE", "Guide", "Editing the mandible guide", 1),
            ("POSITIONING_AID", "Positioning Aid", "Editing the mandible positioning aid", 2)
        ],
        name="Mandible Edit",
        description="Select whether to edit the mandible guide or positioning aid",
        default="GUIDE",
        update=positioning_aid_toggle_update
    )

    def positioning_aid_size_x_set_val(self, value):
        if "positioning_aid_mesh" in bpy.data.objects.keys():
            obj = bpy.data.objects["positioning_aid_mesh"]
            obj.scale[0] = value

    def positioning_aid_size_z_set_val(self, value):
        if "positioning_aid_mesh" in bpy.data.objects.keys():
            obj = bpy.data.objects["positioning_aid_mesh"]
            obj.scale[2] = value

    def positioning_aid_size_x_get_val(self):
        if "positioning_aid_mesh" in bpy.data.objects.keys():
            obj = bpy.data.objects["positioning_aid_mesh"]
            return obj.scale[0]
        return 0.0
    
    def positioning_aid_size_z_get_val(self):
        if "positioning_aid_mesh" in bpy.data.objects.keys():
            obj = bpy.data.objects["positioning_aid_mesh"]
            return obj.scale[2]
        return 0.0

    # NOTE: z and x (height and width) are swapped here due to how the mesh is deformed by the spline.

    positioning_aid_size_z: FloatProperty(
        name="Positioning aid width",
        default=0.2,
        description="Thickness of the positioning aid (in Z direction)",
        get = positioning_aid_size_z_get_val,
        set = positioning_aid_size_z_set_val
    )

    positioning_aid_size_x: FloatProperty(
        name="Positioning aid height",
        default=0.2,
        description="Thickness of the positioning aid (in X direction)",
        get = positioning_aid_size_x_get_val,
        set = positioning_aid_size_x_set_val
    )

    export_dir_path: StringProperty(
        name="Export directory",
        description="Export directory where guide 3D models will be exported",
        default="",
        maxlen=1023,
        subtype="DIR_PATH"
    )

    export_toggle_fibula_guide: BoolProperty(
        name="Export Fibula Guide",
        description="Whether to export the fibula guide",
        default=True
    )

    export_toggle_mandible_guide: BoolProperty(
        name="Export Mandible Guide",
        description="Whether to export the mandible guide",
        default=True
    )

    export_toggle_mandible_aid: BoolProperty(
        name="Export Positioning Aid",
        description="Whether to export the mandible positioning aid",
        default=True
    )

    export_toggle_reconstructed_mandible: BoolProperty(
        name="Export Reconstructed Mandible",
        description="Whether to export the reconstructed mandible object",
        default=True
    )
    
    screenshot_dir_path: StringProperty(
        name="Screenshot directory",
        description="Screenshot directory, where all screenshots will be saved",
        default="",
        maxlen=1023,
        subtype="DIR_PATH"
    )

    def bevel_segmentcount_update(self, context):
        val = bpy.context.scene.FFFGenPropertyGroup.bevel_segmentcount
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                if mod.name.startswith("fffgen_bevel"):
                    mod.segments = val
        return
    
    def bevel_width_update(self, context):
        val = bpy.context.scene.FFFGenPropertyGroup.bevel_width
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                if mod.name.startswith("fffgen_bevel"):
                    mod.width = val
        return

    bevel_segmentcount: IntProperty(
        name="Bevel segment count",
        description="Number of bevel segments.",
        default=3,
        min=0,
        update = bevel_segmentcount_update
    )

    bevel_width: FloatProperty(
        name="Bevel width",
        min=0.0,
        default=0.1,
        description="Bevel width",
        update=bevel_width_update
    )

    export_scale_factor: FloatProperty(
        name="Scale Factor",
        min=0.0,
        default=1.0,
        description="Scale Factor for .stl export"
    )
