# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from .utils import with_prefix


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = with_prefix('AddonPreferences')

    def draw(self, context):
        layout = self.layout
        layout.label(text="MaterialX addon preferences")
