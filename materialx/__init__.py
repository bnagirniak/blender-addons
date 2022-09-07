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

ADDON_PREFIX = "materialx"

if "bpy" in locals():
    import importlib
    if "node_tree" in locals():
        importlib.reload(node_tree)
    if "utils" in locals():
        importlib.reload(utils)
    if "operators" in locals():
        importlib.reload(operators)
    if "menues" in locals():
        importlib.reload(menus)
    if "preferences" in locals():
        importlib.reload(preferences)
else:
    from .enum_values import *
    from .functions import *
    from .operators import *
    from .menus import *
    from .preferences import *

