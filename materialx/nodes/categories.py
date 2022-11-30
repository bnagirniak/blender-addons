# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from collections import defaultdict

from nodeitems_utils import NodeCategory, NodeItem

from ..utils import title_str, code_str, with_prefix


class MxNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'


def get_node_categories():
    from . import mx_node_classes

    d = defaultdict(list)
    for MxNode_cls in mx_node_classes:
        d[MxNode_cls.category].append(MxNode_cls)

    categories = []
    for category, category_classes in d.items():
        categories.append(
            MxNodeCategory(with_prefix(code_str(category), '_MX_NG_'), title_str(category),
                           items=[NodeItem(MxNode_cls.bl_idname)
                                  for MxNode_cls in category_classes]))

    categories.append(
        MxNodeCategory(with_prefix('LAYOUT', '_MX_NG_'), 'Layout',
                       items=[NodeItem("NodeFrame"),
                              NodeItem("NodeReroute")]))

    return categories
