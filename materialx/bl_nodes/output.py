# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD
import MaterialX

from .node_parser import NodeParser, Id, log


class ShaderNodeOutputMaterial(NodeParser):
    nodegraph_path = ""

    def __init__(self, doc, material, node, obj, **kwargs):
        super().__init__(Id(), doc, material, node, obj, None, None, {}, **kwargs)

    def export(self):
        surface = self.get_input_link('Surface')
        if surface is None:
            return None

        linked_input_type = surface.getType() if isinstance(surface, MaterialX.Node) else surface.type

        if linked_input_type != 'surfaceshader':
            log.warn("Incorrect node tree to export: output node doesn't have correct input")

            return None

        result = self.create_node('surfacematerial', 'material', {
            'surfaceshader': surface,
        })

        return result
