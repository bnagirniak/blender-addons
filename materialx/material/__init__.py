# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from . import (
    ui,
    properties
)

register_classes, unregister_classes = bpy.utils.register_classes_factory([
    ui.MATERIAL_OP_new_mx_node_tree,
    ui.MATERIAL_OP_duplicate_mx_node_tree,
    ui.MATERIAL_OP_convert_shader_to_mx,
    ui.MATERIAL_OP_duplicate_mat_mx_node_tree,
    ui.MATERIAL_OP_link_mx_node_tree,
    ui.MATERIAL_OP_unlink_mx_node_tree,
    ui.MATERIAL_MT_mx_node_tree,
    ui.MATERIAL_PT_materialx,
    ui.MATERIAL_PT_materialx_surfaceshader,
    ui.MATERIAL_PT_materialx_displacementshader,
    ui.MATERIAL_OP_link_mx_node,
    ui.MATERIAL_OP_invoke_popup_input_nodes,
    ui.MATERIAL_OP_invoke_popup_shader_nodes,
    ui.MATERIAL_OP_remove_node,
    ui.MATERIAL_OP_disconnect_node,
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
