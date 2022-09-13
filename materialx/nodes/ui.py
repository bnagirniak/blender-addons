# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from pathlib import Path
import traceback

import MaterialX as mx

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper

from ..node_tree import MxNodeTree
from .. import utils
from ..preferences import addon_preferences

from ..utils import logging
log = logging.Log('nodes.ui')


class NODES_OP_import_file(bpy.types.Operator, ImportHelper):
    bl_idname = utils.with_prefix('nodes_import_file')
    bl_label = "Import from File"
    bl_description = "Import MaterialX node tree from .mtlx file"

    filename_ext = ".mtlx"
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="File path used for importing MaterialX node tree from .mtlx file",
        maxlen=1024, subtype="FILE_PATH"
    )
    filter_glob: bpy.props.StringProperty(default="*.mtlx", options={'HIDDEN'}, )

    def execute(self, context):
        mx_node_tree = context.space_data.edit_tree
        mtlx_file = Path(self.filepath)

        doc = mx.createDocument()
        search_path = mx.FileSearchPath(str(mtlx_file.parent))
        search_path.append(str(utils.MX_LIBS_DIR))
        try:
            mx.readFromXmlFile(doc, str(mtlx_file))
            mx_node_tree.import_(doc, mtlx_file)

        except Exception as e:
            log.error(traceback.format_exc(), mtlx_file)
            return {'CANCELLED'}

        return {'FINISHED'}


class NODES_OP_export_file(bpy.types.Operator, ExportHelper):
    bl_idname = utils.with_prefix('nodes_export_file')
    bl_label = "Export MaterialX"
    bl_description = "Export MaterialX node tree to .mtlx file"

    # region properties
    filename_ext = ".mtlx"

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="File path used for exporting MaterialX node tree to .mtlx file",
        maxlen=1024,
        subtype="FILE_PATH"
    )
    filter_glob: bpy.props.StringProperty(
        default="*.mtlx",
        options={'HIDDEN'},
    )
    is_export_deps: bpy.props.BoolProperty(
        name="Include dependencies",
        description="Export used MaterialX dependencies",
        default=False
    )
    is_export_textures: bpy.props.BoolProperty(
        name="Export bound textures",
        description="Export bound textures to corresponded folder",
        default=True
    )
    is_clean_texture_folder: bpy.props.BoolProperty(
        name="Сlean texture folder",
        description="Сlean texture folder before export",
        default=False
    )
    is_clean_deps_folders: bpy.props.BoolProperty(
        name="Сlean MaterialX dependencies folders",
        description="Сlean MaterialX dependencies folders before export",
        default=False
    )
    texture_dir_name: bpy.props.StringProperty(
        name="Texture folder name",
        description="Texture folder name used for exporting files",
        default='textures',
        maxlen=1024
    )
    is_create_new_folder: bpy.props.BoolProperty(
        name="Create new folder",
        description="Create new folder for material",
        default=True
    )
    # endregion

    def execute(self, context):
        mx_node_tree = context.space_data.edit_tree
        doc = mx_node_tree.export()
        if not doc:
            log.warn("Incorrect node tree to export", mx_node_tree)
            return {'CANCELLED'}

        if self.is_create_new_folder:
            self.filepath = str(Path(self.filepath).parent / mx_node_tree.name_full / Path(self.filepath).name)

        utils.export_mx_to_file(doc, self.filepath,
                                mx_node_tree=mx_node_tree,
                                is_export_deps=self.is_export_deps,
                                is_export_textures=self.is_export_textures,
                                texture_dir_name=self.texture_dir_name,
                                is_clean_texture_folder=self.is_clean_texture_folder,
                                is_clean_deps_folders=self.is_clean_deps_folders)

        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, 'is_create_new_folder')
        self.layout.prop(self, 'is_export_deps')

        col = self.layout.column(align=False)
        col.prop(self, 'is_export_textures')

        row = col.row()
        row.enabled = self.is_export_textures
        row.prop(self, 'texture_dir_name', text='')

    @staticmethod
    def enabled(context):
        return bool(context.space_data.edit_tree.output_node)


class NODES_OP_export_console(bpy.types.Operator):
    bl_idname = utils.with_prefix('nodes_export_console')
    bl_label = "Export MaterialX to Console"
    bl_description = "Export MaterialX node tree to console"

    def execute(self, context):
        mx_node_tree = context.space_data.edit_tree
        doc = mx_node_tree.export()
        if not doc:
            log.warn("Incorrect node tree to export", mx_node_tree)
            return {'CANCELLED'}

        print(mx.writeToXmlString(doc))
        return {'FINISHED'}

    @staticmethod
    def enabled(context):
        return bool(context.space_data.edit_tree.output_node)


class NODES_OP_create_basic_nodes(bpy.types.Operator):
    bl_idname = utils.with_prefix("nodes_create_basic_nodes")
    bl_label = "Create Basic Nodes"
    bl_description = "Create basic MaterialX nodes"

    def execute(self, context):
        mx_node_tree = context.space_data.edit_tree
        mx_node_tree.create_basic_nodes()
        return {'FINISHED'}


class NODES_PT_tools(bpy.types.Panel):
    bl_idname = utils.with_prefix('NODES_PT_tools', '_', True)
    bl_label = "MaterialX Tools"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        return tree and tree.bl_idname == MxNodeTree.bl_idname

    def draw(self, context):
        layout = self.layout

        layout.operator(NODES_OP_create_basic_nodes.bl_idname, icon='ADD')
        layout.operator(NODES_OP_import_file.bl_idname, icon='IMPORT')
        layout.operator(NODES_OP_export_file.bl_idname, icon='EXPORT', text='Export MaterialX to file')


class NODES_PT_dev(bpy.types.Panel):
    bl_idname = utils.with_prefix('NODES_PT_dev', '_', True)
    bl_parent_id = NODES_PT_tools.bl_idname
    bl_label = "Dev"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return addon_preferences().dev_tools

    def draw(self, context):
        layout = self.layout

        layout.operator(NODES_OP_export_console.bl_idname)