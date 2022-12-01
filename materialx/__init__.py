# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

"""
MaterialX nodes addon
"""

bl_info = {
    "name": "MaterialX nodes",
    "description": "MaterialX nodes addon",
    "author": "AMD",
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "location": "Editor Type -> Shader Editor",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/materials/materialx.html",
    "warning": "Alpha",
    "support": "TESTING",
    "category": "Material",
}

ADDON_ALIAS = "materialx"


from . import (
    preferences,
    nodes,
    ui,
    utils,
)

from . import logging
log = logging.Log("__init__")


def register():
    log("register")

    preferences.register()
    nodes.register()
    ui.register()


def unregister():
    log("unregister")

    utils.clear_temp_dir()

    ui.unregister()
    nodes.unregister()
    preferences.unregister()
