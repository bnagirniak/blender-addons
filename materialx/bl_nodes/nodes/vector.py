# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from ..node_parser import NodeParser

from ... import logging
log = logging.Log("bl_nodes.nodes.vector")

DEFAULT_SPACE = 'OBJECT'


class ShaderNodeNormalMap(NodeParser):
    def export(self):
        color = self.get_input_value('Color')
        strength = self.get_input_value('Strength')
        space = self.node.space

        if space not in ('TANGENT', 'OBJECT'):
            log.warn("Ignoring unsupported Space", space, self.node, self.material,
                     f"{DEFAULT_SPACE} will be used")
            space = DEFAULT_SPACE

        if space == 'TANGENT':
            log.warn("Ignoring unsupported UV Map", space, self.node, self.material,
                     "No UV Map will be used")

        result = self.create_node('normalmap', 'vector3', {
            'in': color ,
            'scale': strength,
            'space': space.lower(),
        })

        return result
