# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from . import ui

register_classes, unregister_classes = bpy.utils.register_classes_factory([
    ui.MATERIAL_OP_import_file,
    ui.MATERIAL_OP_export_file,
    ui.MATERIAL_OP_export_console,
    ui.MATERIAL_PT_tools,
    ui.MATERIAL_PT_dev,
])


def register():
    register_classes()


def unregister():
    unregister_classes()
