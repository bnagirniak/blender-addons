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
    ui,
    properties
)

register_classes, unregister_classes = bpy.utils.register_classes_factory([
    ui.MATERIAL_PT_context,
    ui.MATERIAL_PT_preview,
    ui.MATERIAL_OP_new_mx_node_tree,
    ui.MATERIAL_OP_duplicate_mx_node_tree,
    ui.MATERIAL_OP_convert_shader_to_mx,
    ui.MATERIAL_OP_duplicate_mat_mx_node_tree,
    ui.MATERIAL_OP_link_mx_node_tree,
    ui.MATERIAL_OP_unlink_mx_node_tree,
    ui.MATERIAL_MT_mx_node_tree,
    ui.MATERIAL_PT_material,
    ui.MATERIAL_PT_material_settings_surface,
    ui.MATERIAL_OP_link_mx_node,
    ui.MATERIAL_OP_invoke_popup_input_nodes,
    ui.MATERIAL_OP_invoke_popup_shader_nodes,
    ui.MATERIAL_OP_remove_node,
    ui.MATERIAL_OP_disconnect_node,
    ui.MATERIAL_PT_material_settings_displacement,
    ui.MATERIAL_PT_output_surface,
    ui.MATERIAL_PT_output_displacement,
    ui.MATERIAL_PT_output_volume,
    ui.MATERIAL_OP_export_mx_file,
    ui.MATERIAL_OP_export_mx_console,
    ui.MATERIAL_PT_tools,
    ui.MATERIAL_PT_dev,
])


def register():
    properties.register()
    register_classes()


def unregister():
    properties.unregister()
    unregister_classes()
