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
from . import constants


# initializes the addon, creates collections, appends workspaces...
class InitializeAddon(bpy.types.Operator):
    bl_idname = "fff_gen.initialize_addon"
    bl_label = "Initialize FFF Gen Add-On"
    bl_description = "Initializes the add-on, loads all neccesary files and sets up the user interface"

    def invoke(self, context, event):
        # check if addon has aleady been initialized...
        if(bpy.context.scene.FFFGenPropertyGroup.is_initialized):
            return {"CANCELLED"}
        
        # set the property to indicate that the addon has been initialized
        bpy.context.scene.FFFGenPropertyGroup.is_initialized = True

        remove_objects_and_collections()
        create_collections()
        initialize_workspaces()

        # set active workspace to positioning
        bpy.context.window.workspace = bpy.data.workspaces[constants.WORKSPACE_POSITIONING]

        # set up units and scale
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.context.scene.unit_settings.length_unit = "CENTIMETERS"

        # enable selection in both pose and object mode
        bpy.context.scene.tool_settings.lock_object_mode = False

        return {"FINISHED"}


def remove_objects_and_collections():
    # remove all collections and objects, effectivly clears the current scene
    scene = bpy.context.scene
    for col in scene.collection.children:
        for obj in col.objects:
            bpy.data.objects.remove(obj)
        scene.collection.children.unlink(col)
        for obj in scene.collection.objects:
            bpy.data.objects.remove(obj)
    for col in bpy.data.collections:
        if not col.users:
            bpy.data.collections.remove(col)


def create_collections():
    # initialize/create collections, order matters here, because local hidden collections are accesed using an index
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_ORIGINAL))
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_FFF_GEN_FIBULA))
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_FFF_GEN_MANDIBLE))
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_GUIDE_MANDIBLE))
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_CUTTING_PLANES_MANDIBLE))
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_GUIDE_FIBULA))
    bpy.context.scene.collection.children.link(bpy.data.collections.new(constants.COLLECTION_CUTTING_PLANES_FIBULA))


def initialize_workspaces():
    # initialize workspaces by appending them from a file
    # for each workspace, find the appropriate space(spaceView3D)
    # set the "use_local_collections" flag
    # select collections to be visible
    # set grid scale
    # TODO: set ortho view
    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(directory, "workspaces.blend")

    bpy.ops.workspace.append_activate(
        idname=constants.WORKSPACE_FIBULA_GUIDES,
        filepath=file_path
    )

    for screen in bpy.data.workspaces[constants.WORKSPACE_FIBULA_GUIDES].screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.overlay.grid_scale = 0.01
                    space.use_local_collections = True
                    override_context = {'window': bpy.context.window, 'screen': screen, 'area': area, 'workspace': bpy.data.workspaces[constants.WORKSPACE_FIBULA_GUIDES]}
                    hidden_collections = [1, 3, 4, 5]
                    for collection_index in hidden_collections:
                        bpy.ops.object.hide_collection(override_context, collection_index=collection_index, toggle=True)
    
    bpy.ops.workspace.append_activate(
        idname=constants.WORKSPACE_MANDIBLE_GUIDES,
        filepath=file_path
    )
    
    for screen in bpy.data.workspaces[constants.WORKSPACE_MANDIBLE_GUIDES].screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.overlay.grid_scale = 0.01
                    space.use_local_collections = True
                    override_context = {'window': bpy.context.window, 'screen': screen, 'area': area, 'workspace': bpy.data.workspaces[constants.WORKSPACE_MANDIBLE_GUIDES]}
                    hidden_collections = [1, 2, 3, 6, 7]
                    for collection_index in hidden_collections:
                        bpy.ops.object.hide_collection(override_context, collection_index=collection_index, toggle=True)
    
    bpy.ops.workspace.append_activate(
        idname=constants.WORKSPACE_POSITIONING,
        filepath=file_path
    )

    for screen in bpy.data.workspaces[constants.WORKSPACE_POSITIONING].screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.overlay.grid_scale = 0.01
                    space.use_local_collections = True
                    override_context = {'window': bpy.context.window, 'screen': screen, 'area': area, 'workspace': bpy.data.workspaces[constants.WORKSPACE_POSITIONING]}
                    # check left/right area, change collection visibility as appropriate
                    if area.x > 0: # right area
                        hidden_collections = [3, 4, 5, 6, 7]
                    else:
                        hidden_collections = [2, 4, 5, 6, 7]
                    for collection_index in hidden_collections:
                        bpy.ops.object.hide_collection(override_context, collection_index=collection_index, toggle=True)
