# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

"""
MaterialX NodeTree addon + MaterialX online library
"""

bl_info = {
    "name": "MaterialX NodeTree",
    "description": "MaterialX NodeTree addon + MaterialX online library",
    "author": "AMD",
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "location": "Editor Type -> MaterialX",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/materials/materialx.html",
    "warning": "Alpha",
    "support": "TESTING",
    "category": "Material",
}

ADDON_ALIAS = "materialx"


import bpy

from . import preferences
from . import node_tree
from . import nodes
from . import matlib

from . import logging
log = logging.Log("")


register_classes, unregister_classes = bpy.utils.register_classes_factory([
    node_tree.MxNodeTree,
    preferences.AddonPreferences,
])


def register():
    log("register")

    register_classes()
    nodes.register()
    matlib.register()


def unregister():
    log("unregister")

    matlib.unregister()
    nodes.unregister()
    unregister_classes()
