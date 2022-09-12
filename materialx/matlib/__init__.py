# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from . import ui, properties


register_properties, unregister_properties = bpy.utils.register_classes_factory(
    [
        properties.MatlibProperties,
        properties.WindowManagerProperties,
    ]
)
register_ui, unregister_ui = bpy.utils.register_classes_factory(
    [
        ui.MATLIB_PT_matlib,
        ui.MATLIB_PT_matlib_tools,
        ui.MATLIB_OP_load_materials,
        ui.MATLIB_OP_load_package,
        ui.MATLIB_OP_import_material,
        ui.MATERIAL_OP_matlib_clear_search,
    ]
)


def register():
    register_properties()
    register_ui()


def unregister():
    unregister_ui()
    unregister_properties()
