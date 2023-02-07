# SPDX-License-Identifier: Apache-2.0
# Copyright 2011-2022 Blender Foundation

# <pep8 compliant>

import bpy
from hydra import HydraRenderEngine


class StormHydraRenderEngine(HydraRenderEngine):
    bl_idname = 'StormHydraRenderEngine'
    bl_label = "Hydra: Storm"
    bl_info = "Hydra Storm (OpenGL) render delegate"

    bl_use_preview = False
    bl_use_gpu_context = True

    delegate_id = 'HdStormRendererPlugin'

    def get_delegate_settings(self, engine_type):
        settings = bpy.context.scene.hydra_storm
        return {
            'enableTinyPrimCulling': settings.enable_tiny_prim_culling,
            'volumeRaymarchingStepSize': settings.volume_raymarching_step_size,
            'volumeRaymarchingStepSizeLighting': settings.volume_raymarching_step_size_lighting,
            'volumeMaxTextureMemoryPerField': settings.volume_max_texture_memory_per_field,
            'maxLights': settings.max_lights,
        }


register, unregister = bpy.utils.register_classes_factory((
    StormHydraRenderEngine,
))
