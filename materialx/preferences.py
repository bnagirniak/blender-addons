# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from .utils import with_prefix
from . import logging, ADDON_ALIAS


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = with_prefix('AddonPreferences', '_', True)

    def update_log_level(self, context):
        logging.logger.setLevel(self.log_level)

    dev_tools: bpy.props.BoolProperty(
        name="Developer Tools",
        description="Enable developer tools",
        default=False,
    )
    log_level: bpy.props.EnumProperty(
        name="Log Level",
        description="Select logging level",
        items=(('DEBUG', "Debug", "Log level DEBUG"),
               ('INFO', "Info", "Log level INFO"),
               ('WARNING', "Warning", "Log level WARN"),
               ('ERROR', "Error", "Log level ERROR"),
               ('CRITICAL', "Critical", "Log level CRITICAL")),
        default='INFO',
        update=update_log_level,
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "dev_tools")
        col.prop(self, "log_level")


def addon_preferences():
    return bpy.context.preferences.addons[ADDON_ALIAS].preferences
