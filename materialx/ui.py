# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from pathlib import Path

import traceback
import MaterialX as mx

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper

from . import utils
from .preferences import addon_preferences

from .utils import logging
log = logging.Log(tag='ui')


class MATERIALX_OP_import_file(bpy.types.Operator, ImportHelper):
    bl_idname = utils.with_prefix('materialx_import_file')
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
            utils.import_materialx_from_file(mx_node_tree, doc, mtlx_file)

        except Exception as e:
            log.error(traceback.format_exc(), mtlx_file)
            return {'CANCELLED'}

        return {'FINISHED'}


class MATERIALX_OP_export_file(bpy.types.Operator, ExportHelper):
    bl_idname = utils.with_prefix('materialx_export_file')
    bl_label = "Export to File"
    bl_description = "Export material as MaterialX node tree to .mtlx file"

    filename_ext = ".mtlx"

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="File path used for exporting material as MaterialX node tree to .mtlx file",
        maxlen=1024,
        subtype="FILE_PATH"
    )
    filter_glob: bpy.props.StringProperty(
        default="*.mtlx",
        options={'HIDDEN'},
    )
    export_textures: bpy.props.BoolProperty(
        name="Export textures",
        description="Export bound textures to corresponded folder",
        default=True
    )
    texture_dir_name: bpy.props.StringProperty(
        name="Folder name",
        description="Texture folder name used for exporting files",
        default='textures',
        maxlen=1024,
    )

    def execute(self, context):
        doc = utils.export(context.material, None)
        if not doc:
            return {'CANCELLED'}

        utils.export_to_file(doc, self.filepath, self.export_textures, self.texture_dir_name)

        return {'FINISHED'}

    def draw(self, context):
        col = self.layout.column(align=False)
        col.prop(self, 'export_textures')

        row = col.row()
        row.enabled = self.export_textures
        row.prop(self, 'texture_dir_name', text='')


class MATERIALX_OP_export_console(bpy.types.Operator):
    bl_idname = utils.with_prefix('materialx_export_console')
    bl_label = "Export to Console"
    bl_description = "Export material as MaterialX node tree to console"

    def execute(self, context):
        doc = utils.export(context.material, context.object)
        if not doc:
            return {'CANCELLED'}

        print(mx.writeToXmlString(doc))
        return {'FINISHED'}


class MATERIALX_PT_tools(bpy.types.Panel):
    bl_idname = utils.with_prefix('MATERIALX_PT_tools', '_', True)
    bl_label = "MaterialX Tools"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree

        return tree and tree.bl_idname == 'ShaderNodeTree'

    def draw(self, context):
        layout = self.layout

        layout.operator(MATERIALX_OP_import_file.bl_idname, icon='IMPORT')
        layout.operator(MATERIALX_OP_export_file.bl_idname, icon='EXPORT')


class MATERIALX_PT_dev(bpy.types.Panel):
    bl_idname = utils.with_prefix('MATERIALX_PT_dev', '_', True)
    bl_label = "Dev"
    bl_parent_id = MATERIALX_PT_tools.bl_idname
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        preferences = addon_preferences()
        return preferences.dev_tools if preferences else True

    def draw(self, context):
        layout = self.layout
        layout.operator(MATERIALX_OP_export_console.bl_idname)


register, unregister = bpy.utils.register_classes_factory([
    MATERIALX_OP_import_file,
    MATERIALX_OP_export_file,
    MATERIALX_OP_export_console,
    MATERIALX_PT_tools,
    MATERIALX_PT_dev,
])
