# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import importlib

import bpy
import nodeitems_utils
import sys

from . import node, categories, generate_node_classes
from .. import utils


sys.path.append(str(utils.ADDON_DATA_DIR))
generate_node_classes.generate_basic_classes()

gen_modules = [importlib.import_module(f"{utils.NODE_CLASSES_FOLDER}.{f.name[:-len(f.suffix)]}")
               for f in utils.NODE_CLASSES_DIR.glob("gen_*.py")]

mx_node_classes = []
for mod in gen_modules:
    mx_node_classes.extend(mod.mx_node_classes)

# sorting by category and label
mx_node_classes = sorted(mx_node_classes, key=lambda cls: (cls.category.lower(), cls.bl_label.lower()))


register_sockets, unregister_sockets = bpy.utils.register_classes_factory([
    node.MxNodeInputSocket,
    node.MxNodeOutputSocket,
])

register_nodes, unregister_nodes = bpy.utils.register_classes_factory(mx_node_classes)


def register():
    register_sockets()
    register_nodes()

    nodeitems_utils.register_node_categories(utils.with_prefix("MX_NODES"), categories.get_node_categories())


def unregister():
    nodeitems_utils.unregister_node_categories(utils.with_prefix("MX_NODES"))

    unregister_nodes()
    unregister_sockets()


def get_mx_node_cls(mx_node):
    node_name = mx_node.getCategory()

    suffix = f'_{node_name}'
    classes = tuple(cls for cls in mx_node_classes if cls.__name__.endswith(suffix))
    if not classes:
        raise KeyError(f"Unable to find MxNode class for {mx_node}")

    def params_set(node, out_type):
        return {f"in_{p.getName()}:{p.getType()}" for p in node.getActiveInputs()} | \
               {out_type}

    node_params_set = params_set(mx_node, mx_node.getType())

    for cls in classes:
        for nodedef, data_type in cls.get_nodedefs():
            nd_outputs = nodedef.getActiveOutputs()
            nd_params_set = params_set(nodedef, 'multioutput' if len(nd_outputs) > 1 else
                                       nd_outputs[0].getType())
            if node_params_set.issubset(nd_params_set):
                return cls, data_type

    raise TypeError(f"Unable to find suitable nodedef for {mx_node}")
