# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy


class MATERIALX_Panel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'


class MATERIALX_ChildPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = ''


from . import (
    material,
    # matlib,
    # world,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory([
    material.MATERIAL_PT_context,
    material.MATERIAL_PT_preview,
    material.MATERIAL_OP_new_mx_node_tree,
    material.MATERIAL_OP_duplicate_mx_node_tree,
    material.MATERIAL_OP_convert_shader_to_mx,
    material.MATERIAL_OP_duplicate_mat_mx_node_tree,
    material.MATERIAL_OP_link_mx_node_tree,
    material.MATERIAL_OP_unlink_mx_node_tree,
    material.MATERIAL_MT_mx_node_tree,
    material.MATERIAL_PT_material,
    material.MATERIAL_PT_material_settings_surface,
    material.MATERIAL_OP_link_mx_node,
    material.MATERIAL_OP_invoke_popup_input_nodes,
    material.MATERIAL_OP_invoke_popup_shader_nodes,
    material.MATERIAL_OP_remove_node,
    material.MATERIAL_OP_disconnect_node,
    material.MATERIAL_PT_material_settings_displacement,
    material.MATERIAL_PT_output_surface,
    material.MATERIAL_PT_output_displacement,
    material.MATERIAL_PT_output_volume,
    material.MATERIAL_OP_export_mx_file,
    material.MATERIAL_OP_export_mx_console,
    material.MATERIAL_PT_tools,
    # material.MATERIAL_PT_dev,

    # matlib.MATERIAL_OP_matlib_clear_search,
    # matlib.MATLIB_OP_load_materials,
    # matlib.MATLIB_OP_import_material,
    # matlib.MATLIB_OP_load_package,
    # matlib.MATLIB_PT_matlib,
    # matlib.MATLIB_PT_matlib_tools,

    # world.WORLD_PT_surface,
])


def register():
    material.register()
    register_classes()


def unregister():
    material.unregister()
    unregister_classes()
