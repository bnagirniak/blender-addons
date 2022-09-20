# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import traceback

import bpy
import MaterialX as mx

from ..node_tree import MxNodeTree
from ..bl_nodes.output import ShaderNodeOutputMaterial
from ..utils import MX_LIBS_DIR

from ..utils import logging, get_temp_file, MaterialXProperties
log = logging.Log('material.properties')


class MaterialProperties(MaterialXProperties):
    bl_type = bpy.types.Material

    def update_mx_node_tree(self, context):
        pass
        #self.update()

    mx_node_tree: bpy.props.PointerProperty(type=MxNodeTree, update=update_mx_node_tree)

    @property
    def output_node(self):
        material = self.id_data

        if not material.node_tree:
            return None

        return next((node for node in material.node_tree.nodes if
                     node.bl_idname == ShaderNodeOutputMaterial.__name__ and
                     node.is_active_output), None)

    def export(self, obj: bpy.types.Object, check_mx_node_tree=True) -> [mx.Document, None]:
        if check_mx_node_tree and self.mx_node_tree:
            return self.mx_node_tree.export()

        material = self.id_data
        output_node = self.output_node

        if not output_node:
            return None

        doc = mx.createDocument()

        node_parser = ShaderNodeOutputMaterial(doc, material, output_node, obj)
        if not node_parser.export():
            return None

        return doc

    def convert_to_materialx(self, obj: bpy.types.Object = None):
        mat = self.id_data
        output_node = self.output_node
        if not output_node:
            log.warn("Incorrect node tree to export: output node doesn't exist")
            return False

        mx_node_tree = bpy.data.node_groups.new(f"MX_{mat.name}", type=MxNodeTree.bl_idname)

        if obj:
            doc = self.export(obj)
        else:
            doc = mx.createDocument()

            node_parser = ShaderNodeOutputMaterial(doc, mat, output_node, obj)
            if not node_parser.export():
                return False

        if not doc:
            log.warn("Incorrect node tree to export", mx_node_tree)
            return False

        mtlx_file = get_temp_file(".mtlx",
                                  f'{mat.name}_{self.mx_node_tree.name if self.mx_node_tree else ""}')
        mx.writeToXmlFile(doc, str(mtlx_file))
        search_path = mx.FileSearchPath(str(mtlx_file.parent))
        search_path.append(str(MX_LIBS_DIR))

        try:
            mx.readFromXmlFile(doc, str(mtlx_file), searchPath=search_path)
            mx_node_tree.import_(doc, mtlx_file)
            self.mx_node_tree = mx_node_tree

        except Exception as e:
            log.error(traceback.format_exc(), mtlx_file)
            return False

        return True


register, unregister = bpy.utils.register_classes_factory((
    MaterialProperties,
))
