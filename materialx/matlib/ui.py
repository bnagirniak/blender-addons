# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import traceback
import textwrap

import MaterialX as mx

import bpy

from .. import utils
from ..node_tree import MxNodeTree
from .manager import manager

from ..utils import logging
log = logging.Log('matlib.ui')


class MATERIAL_OP_matlib_clear_search(bpy.types.Operator):
    """Create new MaterialX node tree for selected material"""
    bl_idname = utils.with_prefix("matlib_clear_search")
    bl_label = ""

    def execute(self, context):
        utils.mx_properties(context.window_manager).matlib.search = ''
        return {"FINISHED"}


class MATLIB_OP_load_materials(bpy.types.Operator):
    """Load materials"""
    bl_idname = utils.with_prefix("matlib_load")
    bl_label = "Reload Library"

    def execute(self, context):
        manager.check_load_materials(reset=True)
        return {"FINISHED"}


class MATLIB_OP_import_material(bpy.types.Operator):
    """Import Material Package to material"""
    bl_idname = utils.with_prefix("matlib_import_material")
    bl_label = "Import Material Package"

    def execute(self, context):
        matlib_prop = utils.mx_properties(context.window_manager).matlib
        package = matlib_prop.package

        mtlx_file = package.unzip()

        # getting/creating MxNodeTree
        bl_material = context.material
        mx_node_tree = utils.mx_properties(bl_material).mx_node_tree
        if not mx_node_tree:
            mx_node_tree = bpy.data.node_groups.new(f"MX_{bl_material.name}",
                                                    type=MxNodeTree.bl_idname)
            utils.mx_properties(bl_material).mx_node_tree = mx_node_tree

        log(f"Reading: {mtlx_file}")
        doc = mx.createDocument()
        search_path = mx.FileSearchPath(str(mtlx_file.parent))
        search_path.append(str(utils.MX_LIBS_DIR))
        try:
            mx.readFromXmlFile(doc, str(mtlx_file), searchPath=search_path)
            mx_node_tree.import_(doc, mtlx_file)

        except Exception as e:
            log.error(traceback.format_exc(), mtlx_file)
            return {'CANCELLED'}

        return {"FINISHED"}


class MATLIB_OP_load_package(bpy.types.Operator):
    """Download material package"""
    bl_idname = utils.with_prefix("matlib_load_package")
    bl_label = "Download Package"

    def execute(self, context):
        matlib_prop = utils.mx_properties(context.window_manager).matlib
        manager.load_package(matlib_prop.package)

        return {"FINISHED"}


class MATLIB_PT_matlib(bpy.types.Panel):
    bl_idname = utils.with_prefix("MATLIB_PT_matlib", '_', True)
    bl_label = "Material Library"
    bl_context = "material"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        matlib_prop = utils.mx_properties(context.window_manager).matlib

        manager.check_load_materials()

        # category
        layout.prop(matlib_prop, 'category_id')

        # search
        row = layout.row(align=True)
        row.prop(matlib_prop, 'search', text="", icon='VIEWZOOM')
        if matlib_prop.search:
            row.operator(MATERIAL_OP_matlib_clear_search.bl_idname, icon='X')

        # materials
        col = layout.column(align=True)
        materials = matlib_prop.get_materials()
        if not materials:
            col.label(text="Start syncing..." if not manager.materials else "No materials found")
            return

        row = col.row()
        row.alignment = 'RIGHT'
        row.label(text=f"{len(materials)} materials")

        col.template_icon_view(matlib_prop, 'material_id', show_labels=True)

        mat = matlib_prop.material
        if not mat:
            return

        # other material renders
        if len(mat.renders) > 1:
            grid = col.grid_flow(align=True)
            for i, render in enumerate(mat.renders):
                if i % 6 == 0:
                    row = grid.row()
                    row.alignment = 'CENTER'

                row.template_icon(render.thumbnail_icon_id, scale=5)

        # material title
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text=mat.title)

        # material description
        col = layout.column(align=True)
        if mat.description:
            for line in textwrap.wrap(mat.description, 60):
                col.label(text=line)

        col = layout.column(align=True)
        col.label(text=f"Category: {mat.category.title}")
        col.label(text=f"Author: {mat.author}")

        # packages
        package = matlib_prop.package
        if not package:
            return

        layout.prop(matlib_prop, 'package_id', icon='DOCUMENTS')

        row = layout.row()
        if package.has_file:
            row.operator(MATLIB_OP_import_material.bl_idname, icon='IMPORT')
        else:
            if package.size_load is None:
                row.operator(MATLIB_OP_load_package.bl_idname, icon='IMPORT')
            else:
                percent = min(100, int(package.size_load * 100 / package.size))
                row.operator(MATLIB_OP_load_package.bl_idname, icon='IMPORT',
                             text=f"Downloading Package...{percent}%")
                row.enabled = False


class MATLIB_PT_matlib_tools(bpy.types.Panel):
    bl_label = "Tools"
    bl_context = "material"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_parent_id = utils.with_prefix('MATLIB_PT_matlib', '_', True)
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=manager.status)

        row = col.row()
        row.enabled = bool(manager.is_synced)
        row.operator(MATLIB_OP_load_materials.bl_idname, icon='FILE_REFRESH')
