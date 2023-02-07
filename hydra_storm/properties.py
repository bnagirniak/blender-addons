# SPDX-License-Identifier: Apache-2.0
# Copyright 2011-2022 Blender Foundation

# <pep8 compliant>

import bpy


class Properties(bpy.types.PropertyGroup):
    bl_type = None

    @classmethod
    def register(cls):
        cls.bl_type.hydra_storm = bpy.props.PointerProperty(
            name="Hydra Storm",
            description="Hydra Storm properties",
            type=cls,
        )

    @classmethod
    def unregister(cls):
        del cls.bl_type.hydra_storm


class SceneProperties(Properties):
    bl_type = bpy.types.Scene

    enable_tiny_prim_culling: bpy.props.BoolProperty(
        name="Tiny Prim Culling",
        description="Enable Tiny Prim Culling",
        default=False,
    )
    volume_raymarching_step_size: bpy.props.FloatProperty(
        name="Volume Raymarching Step Size",
        description="Step size when raymarching volume",
        default=1.0,
    )
    volume_raymarching_step_size_lighting: bpy.props.FloatProperty(
        name="Volume Raymarching Step Size",
        description="Step size when raymarching volume for lighting computation",
        default=10.0,
    )
    volume_max_texture_memory_per_field: bpy.props.FloatProperty(
        name="Volume Max Texture Memory Per Field",
        description="Maximum memory for a volume field texture in Mb (unless overridden by field prim)",
        default=128.0,
    )
    max_lights: bpy.props.IntProperty(
        name="Max Lights",
        description="Maximum number of lights",
        default=16, min=0,
    )


register, unregister = bpy.utils.register_classes_factory((
    SceneProperties,
))
