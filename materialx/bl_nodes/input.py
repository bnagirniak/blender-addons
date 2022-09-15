# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from .node_parser import NodeParser


class ShaderNodeValue(NodeParser):
    """ Returns float value """

    def export(self):
        return self.get_output_default()


class ShaderNodeRGB(NodeParser):
    """ Returns color value """

    def export(self):
        return self.get_output_default()
