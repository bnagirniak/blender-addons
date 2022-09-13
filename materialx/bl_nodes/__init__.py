# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from nodeitems_utils import (
    NodeCategory,
    NodeItem,
    register_node_categories,
    unregister_node_categories,
)
from nodeitems_builtins import (
    ShaderNodeCategory,
)
from .. import utils


class CompatibleShaderNodeCategory(NodeCategory):
    """ Appear with an active USD plugin in Material shader editor only """
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'


# add nodes here once they are supported
node_categories = [
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_INPUT", '_', True), "Input", items=[
        NodeItem('ShaderNodeRGB'),
        NodeItem('ShaderNodeValue'),
    ], ),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_OUTPUT", '_', True), "Output", items=[
        NodeItem('ShaderNodeOutputMaterial'),
    ], ),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_SHADERS", '_', True), "Shader", items=[
        NodeItem('ShaderNodeBsdfDiffuse'),
        NodeItem('ShaderNodeBsdfGlass'),
        NodeItem('ShaderNodeEmission'),
        NodeItem('ShaderNodeBsdfPrincipled'),
    ]),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_TEXTURE", '_', True), "Texture", items=[
        NodeItem('ShaderNodeTexImage'),
    ], ),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_COLOR", '_', True), "Color", items=[
        NodeItem('ShaderNodeInvert'),
        NodeItem('ShaderNodeMixRGB'),
    ], ),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_CONVERTER", '_', True), "Converter", items=[
        NodeItem('ShaderNodeMath'),
    ], ),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_VECTOR", '_', True), "Vector", items=[
        NodeItem('ShaderNodeNormalMap'),
    ], ),
    CompatibleShaderNodeCategory(utils.with_prefix("SHADER_NODE_CATEGORY_LAYOUT", '_', True), "Layout", items=[
        NodeItem('NodeFrame'),
        NodeItem('NodeReroute'),
    ], ),
]


# some nodes are hidden from plugins by Cycles itself(like Material Output), some we could not support.
# thus we'll hide 'em all to show only selected set of supported Blender nodes
# custom HdUSD_CompatibleShaderNodeCategory will be used instead
# def hide_cycles_and_eevee_poll(method):
#     @classmethod
#     def func(cls, context):
#         return not context.scene.render.engine == 'HdUSD' and method(context)
#     return func


old_shader_node_category_poll = None


def register():
    # hide Cycles/Eevee menu
    # global old_shader_node_category_poll
    # old_shader_node_category_poll = ShaderNodeCategory.poll
    # ShaderNodeCategory.poll = hide_cycles_and_eevee_poll(ShaderNodeCategory.poll)

    # use custom menu
    register_node_categories(utils.with_prefix("NODES", '_', True), node_categories)


def unregister():
    # restore Cycles/Eevee menu
    # if old_shader_node_category_poll and ShaderNodeCategory.poll is not old_shader_node_category_poll:
    #     ShaderNodeCategory.poll = old_shader_node_category_poll

    # remove custom menu
    unregister_node_categories(utils.with_prefix("NODES", '_', True))
