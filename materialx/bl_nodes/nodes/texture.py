# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

from ..node_parser import NodeParser
from ...utils import cache_image_file


TEXTURE_ERROR_COLOR = (1.0, 0.0, 1.0)  # following Cycles color for wrong Texture nodes


class ShaderNodeTexImage(NodeParser):
    def export(self):
        image_error_result = self.node_item(TEXTURE_ERROR_COLOR)
        image = self.node.image

        # TODO support UDIM Tilesets and SEQUENCE
        if not image or image.source in ('TILED', 'SEQUENCE'):
            return image_error_result

        img_path = cache_image_file(image)
        if not img_path:
            return image_error_result

        # TODO use Vector input for UV
        uv = self.create_node('texcoord', 'vector2', {})

        result = self.create_node('image', self.out_type, {
            'file': img_path,
            'texcoord': uv,
        })

        return result
