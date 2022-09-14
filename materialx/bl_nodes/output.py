# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from .node_parser import NodeParser, Id


class ShaderNodeOutputMaterial(NodeParser):
    nodegraph_path = ""

    def __init__(self, doc, material, node, obj, **kwargs):
        super().__init__(Id(), doc, material, node, obj, None, None, {}, **kwargs)

    def export(self):
        surface = self.get_input_link('Surface')
        if surface is None:
            return None

        if surface.type == 'BSDF':
            surface = self.create_node('surface', 'surfaceshader', {
                'bsdf': surface,
            })
        elif surface.type == 'EDF':
            surface = self.create_node('surface', 'surfaceshader', {
                'edf': surface,
            })

        result = self.create_node('surfacematerial', 'material', {
            'surfaceshader': surface,
        })

        return result
