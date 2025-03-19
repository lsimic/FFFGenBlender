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
from . import initialize_addon
from . import initialize_rig
from . import property_group
from . import UI
from . import update
from . import cutting_planes
from . import fibula_guides
from . import mandible_guides
from . import clear
from . import load_handler
from . import export_guides
from . import screenshot
from . import bevel_worldspace


bl_info = {
    "name": "FFFGen",
    "description": "Fibula free flap guide generation",
    "author": "Luka Šimić, Vjekoslav Kopačin",
    "version": (1, 2, 1),
    "blender": (4, 3, 2),
    "location": "View3D > Toolbox > FFF Gen",
    "wiki_url": "https://lsimic.github.io/FFFGen/",
    "tracker_url": "https://github.com/lsimic/FFFGen/issues",
    "support": "COMMUNITY",
    "category": "Add Mesh"
}


def register():
    bpy.utils.register_class(property_group.FFFGenPropertyGroup)
    bpy.types.Scene.FFFGenPropertyGroup = bpy.props.PointerProperty(type=property_group.FFFGenPropertyGroup)
    bpy.utils.register_class(initialize_addon.InitializeAddon)
    bpy.utils.register_class(initialize_rig.InitializeRig)
    bpy.utils.register_class(update.Update)
    bpy.utils.register_class(update.AutoUpdateOperator)
    bpy.utils.register_class(cutting_planes.InitializeCuttingPlanes)
    bpy.utils.register_class(fibula_guides.CreateFibulaGuide)
    bpy.utils.register_class(fibula_guides.CreateFibulaScrew)
    bpy.utils.register_class(mandible_guides.CreateMandibleGuides)
    bpy.utils.register_class(mandible_guides.CreateMandibleStartScrew)
    bpy.utils.register_class(mandible_guides.CreateMandibleEndScrew)
    bpy.utils.register_class(mandible_guides.JoinMandibleGuides)
    bpy.utils.register_class(mandible_guides.CreateMandiblePositioningAid)
    bpy.utils.register_class(export_guides.ExportGuides)
    bpy.utils.register_class(clear.ClearMandibleGuides)
    bpy.utils.register_class(clear.ClearFibulaGuides)
    bpy.utils.register_class(clear.ClearCuttingPlanes)
    bpy.utils.register_class(clear.ClearMandiblePositioningAid)
    bpy.utils.register_class(clear.ClearAll)
    bpy.utils.register_class(UI.FFFGenGeneralPanel)
    bpy.utils.register_class(UI.FFFGenGuidesPanel)
    bpy.utils.register_class(UI.FFFGenDangerPanel)
    bpy.utils.register_class(UI.FFFGenColorPanel)
    bpy.utils.register_class(UI.FFFGenExportPanel)
    bpy.utils.register_class(screenshot.SaveScreenshot)
    bpy.utils.register_class(screenshot.FFFGenScreenshotPanel)
    bpy.utils.register_class(bevel_worldspace.FFFGenBevelPanel)
    bpy.app.handlers.load_post.append(load_handler.on_load_post_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler.on_load_post_handler)
    del bpy.types.Scene.FFFGenPropertyGroup
    bpy.utils.unregister_class(property_group.FFFGenPropertyGroup)
    bpy.utils.unregister_class(initialize_addon.InitializeAddon)
    bpy.utils.unregister_class(initialize_rig.InitializeRig)
    bpy.utils.unregister_class(update.Update)
    bpy.utils.unregister_class(update.AutoUpdateOperator)
    bpy.utils.unregister_class(cutting_planes.InitializeCuttingPlanes)
    bpy.utils.unregister_class(fibula_guides.CreateFibulaGuide)
    bpy.utils.unregister_class(fibula_guides.CreateFibulaScrew)
    bpy.utils.unregister_class(mandible_guides.CreateMandibleGuides)
    bpy.utils.unregister_class(mandible_guides.CreateMandibleStartScrew)
    bpy.utils.unregister_class(mandible_guides.CreateMandibleEndScrew)
    bpy.utils.unregister_class(mandible_guides.JoinMandibleGuides)
    bpy.utils.unregister_class(mandible_guides.CreateMandiblePositioningAid)
    bpy.utils.unregister_class(export_guides.ExportGuides)
    bpy.utils.unregister_class(clear.ClearMandibleGuides)
    bpy.utils.unregister_class(clear.ClearFibulaGuides)
    bpy.utils.unregister_class(clear.ClearCuttingPlanes)
    bpy.utils.unregister_class(clear.ClearMandiblePositioningAid)
    bpy.utils.unregister_class(clear.ClearAll)
    bpy.utils.unregister_class(UI.FFFGenGeneralPanel)
    bpy.utils.unregister_class(UI.FFFGenGuidesPanel)
    bpy.utils.unregister_class(UI.FFFGenDangerPanel)
    bpy.utils.unregister_class(UI.FFFGenColorPanel)
    bpy.utils.unregister_class(UI.FFFGenExportPanel)
    bpy.utils.unregister_class(screenshot.SaveScreenshot)
    bpy.utils.unregister_class(screenshot.FFFGenScreenshotPanel)
    bpy.utils.unregister_class(bevel_worldspace.FFFGenBevelPanel)

