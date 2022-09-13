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


def register():
    log("register")
    bpy.utils.register_class(preferences.AddonPreferences)
    bpy.utils.register_class(node_tree.MxNodeTree)
    nodes.register()
    matlib.register()


def unregister():
    log("unregister")
    matlib.unregister()
    nodes.unregister()
    bpy.utils.unregister_class(node_tree.MxNodeTree)
    bpy.utils.unregister_class(preferences.AddonPreferences)
