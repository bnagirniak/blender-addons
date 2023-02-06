# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import os
from pathlib import Path
import tempfile
import shutil

import MaterialX as mx
import bpy

from . import ADDON_ALIAS

from . import logging
log = logging.Log('utils')

ADDON_ROOT_DIR = Path(__file__).parent
ADDON_DATA_DIR = Path(bpy.utils.user_resource('SCRIPTS', path=f"addons/{ADDON_ALIAS}_data", create=True))
BL_DATA_DIR = Path(bpy.utils.resource_path('LOCAL')).parent / "materialx"

MX_LIBS_FOLDER = "libraries"
MX_LIBS_DIR = BL_DATA_DIR / MX_LIBS_FOLDER
MX_ADDON_LIBS_DIR = ADDON_ROOT_DIR / MX_LIBS_FOLDER

NODE_CLASSES_FOLDER = "materialx_nodes"
NODE_CLASSES_DIR = ADDON_DATA_DIR / NODE_CLASSES_FOLDER

TEMP_FOLDER = "bl-materialx"

NODE_LAYER_SEPARATION_WIDTH = 280
NODE_LAYER_SHIFT_X = 30
NODE_LAYER_SHIFT_Y = 100


def with_prefix(name, separator='.', upper=False):
    return f"{ADDON_ALIAS.upper() if upper else ADDON_ALIAS}{separator}{name}"


def title_str(val):
    s = val.replace('_', ' ')
    return s[:1].upper() + s[1:]


def code_str(val):
    return val.replace(' ', '_').replace('.', '_')


def set_param_value(mx_param, val, nd_type, nd_output=None):
    from .bl_nodes.node_parser import NodeItem

    if isinstance(val, mx.Node):
        param_nodegraph = mx_param.getParent().getParent()
        val_nodegraph = val.getParent()
        node_name = val.getName()
        if val_nodegraph == param_nodegraph:
            mx_param.setNodeName(node_name)
            if nd_output:
                mx_param.setAttribute('output', nd_output.getName())
        else:
            # checking nodegraph paths
            val_ng_path = val_nodegraph.getNamePath()
            param_ng_path = param_nodegraph.getNamePath()
            ind = val_ng_path.rfind('/')
            ind = ind if ind >= 0 else 0
            if param_ng_path != val_ng_path[:ind]:
                raise ValueError(f"Inconsistent nodegraphs. Cannot connect input "
                                 f"{mx_param.getNamePath()} to {val.getNamePath()}")

            mx_output_name = f'out_{node_name}'
            if nd_output:
                mx_output_name += f'_{nd_output.getName()}'

            mx_output = val_nodegraph.getActiveOutput(mx_output_name)
            if not mx_output:
                mx_output = val_nodegraph.addOutput(mx_output_name, val.getType())
                mx_output.setNodeName(node_name)
                if nd_output:
                    mx_output.setType(nd_output.getType())
                    mx_output.setAttribute('output', nd_output.getName())

            mx_param.setAttribute('nodegraph', val_nodegraph.getName())
            mx_param.setAttribute('output', mx_output.getName())

    elif nd_type == 'filename':
        if isinstance(val, bpy.types.Image):
            image_path = cache_image_file(val)
            if image_path:
                mx_param.setValueString(str(image_path))
        else:
            mx_param.setValueString(str(val))

    elif hasattr(val, 'data') and isinstance(val.data, mx.Node):
        set_param_value(mx_param, val.data, nd_type, nd_output)

    else:
        mx_type = getattr(mx, title_str(nd_type), None)
        if mx_type:
            val = mx_type(val.data) if isinstance(val, NodeItem) else mx_type(val)

        elif nd_type == 'float':
            if isinstance(val, NodeItem):
                val = val.data
        
            if isinstance(val, tuple):
                val = val[0]

        mx_param.setValue(val)


def is_value_equal(mx_val, val, nd_type):
    if nd_type in ('string', 'float', 'integer', 'boolean', 'angle'):
        if nd_type == 'filename' and val is None:
            val = ""

        return mx_val == val

    if nd_type == 'filename':
        val = "" if val is None else val
        return mx_val == val

    return tuple(mx_val) == tuple(val)


def is_shader_type(mx_type):
    return not (mx_type in ('string', 'float', 'integer', 'boolean', 'filename', 'angle') or
                mx_type.startswith('color') or
                mx_type.startswith('vector') or
                mx_type.endswith('array'))


def get_attr(mx_param, name, else_val=None):
    return mx_param.getAttribute(name) if mx_param.hasAttribute(name) else else_val


def parse_value(node, mx_val, mx_type, file_prefix=None):
    if mx_type in ('string', 'float', 'integer', 'boolean', 'filename', 'angle'):
        if file_prefix and mx_type == 'filename':
            mx_val = str((file_prefix / mx_val).resolve())

        if node.category in ('texture2d', 'texture3d') and mx_type == 'filename':
            file_path = Path(mx_val)
            if file_path.exists():
                image = bpy.data.images.get(file_path.name)
                if image and image.filepath_from_user() == str(file_path):
                    return image

                image = bpy.data.images.load(str(file_path))
                return image

            return None

        return mx_val

    return tuple(mx_val)


def parse_value_str(val_str, mx_type, *, first_only=False, is_enum=False):
    if mx_type == 'string':
        if is_enum:
            res = tuple(x.strip() for x in val_str.split(','))
            return res[0] if first_only else res
        return val_str

    if mx_type == 'integer':
        return int(val_str)
    if mx_type in ('float', 'angle'):
        return float(val_str)
    if mx_type == 'boolean':
        return val_str == "true"
    if mx_type.endswith('array'):
        return val_str

    if mx_type.startswith('color') or mx_type.startswith('vector') or mx_type.startswith('matrix'):
        res = tuple(float(x) for x in val_str.split(','))
        return res[0] if first_only else res

    return val_str


def get_nodedef_inputs(nodedef, uniform=None):
    for nd_input in nodedef.getActiveInputs():
        if (uniform is True and nd_input.getAttribute('uniform') != 'true') or \
                (uniform is False and nd_input.getAttribute('uniform') == 'true'):
            continue

        yield nd_input


def get_file_prefix(mx_node, file_path):
    file_prefix = file_path.parent
    n = mx_node
    while True:
        n = n.getParent()
        file_prefix /= n.getFilePrefix()
        if isinstance(n, mx.Document):
            break

    return file_prefix.resolve()


def get_nodegraph_by_path(doc, ng_path, do_create=False):
    nodegraph_names = code_str(ng_path).split('/') if ng_path else ()
    mx_nodegraph = doc
    for nodegraph_name in nodegraph_names:
        next_mx_nodegraph = mx_nodegraph.getNodeGraph(nodegraph_name)
        if not next_mx_nodegraph:
            if do_create:
                next_mx_nodegraph = mx_nodegraph.addNodeGraph(nodegraph_name)
            else:
                return None

        mx_nodegraph = next_mx_nodegraph

    return mx_nodegraph


def get_nodegraph_by_node_path(doc, node_path, do_create=False):
    nodegraph_names = code_str(node_path).split('/')[:-1]
    return get_nodegraph_by_path(doc, '/'.join(nodegraph_names), do_create)


def get_node_name_by_node_path(node_path):
    return code_str(node_path.split('/')[-1])


def get_socket_color(mx_type):
    if mx_type.startswith('color'):
        return (0.78, 0.78, 0.16, 1.0)

    if mx_type in ('integer', 'float', 'boolean'):
        return (0.63, 0.63, 0.63, 1.0)

    if mx_type.startswith(('vector', 'matrix')) or mx_type in ('displacementshader'):
        return (0.39, 0.39, 0.78, 1.0)

    if mx_type in ('string', 'filename'):
        return (0.44, 0.7, 1.0, 1.0)

    if mx_type.endswith(('shader', 'material')) or mx_type in ('BSDF', 'EDF', 'VDF'):
        return (0.39, 0.78, 0.39, 1.0)

    return (0.63, 0.63, 0.63, 1.0)


def export_to_file(doc, filepath, *, export_textures=False, texture_dir_name='textures',
                   export_deps=False, copy_deps=False):
    root_dir = Path(filepath).parent
    root_dir.mkdir(parents=True, exist_ok=True)

    if export_textures:
        texture_dir = root_dir / texture_dir_name
        image_paths = set()
        mx_input_files = (v for v in doc.traverseTree() if isinstance(v, mx.Input) and v.getType() == 'filename')
        for mx_input in mx_input_files:
            texture_dir.mkdir(parents=True, exist_ok=True)

            val = mx_input.getValue()
            if not val:
                log.warn(f"Skipping wrong {mx_input.getType()} input value. Expected: path, got {val}")
                continue

            source_path = Path(val)
            if not source_path.is_file():
                log.warn("Image is missing", source_path)
                continue

            if source_path in image_paths:
                continue

            dest_path = texture_dir / source_path.name

            if source_path not in image_paths:
                image_paths.add(source_path)
                dest_path = texture_dir / source_path.name
                shutil.copy(source_path, dest_path)
                log(f"Export file {source_path} to {dest_path}: completed successfully")

            rel_dest_path = dest_path.relative_to(root_dir)
            mx_input.setValue(rel_dest_path.as_posix(), mx_input.getType())

    if export_deps:
        from .nodes import get_mx_node_cls

        deps_files = {get_mx_node_cls(mx_node)[0]._file_path
                      for mx_node in (it for it in doc.traverseTree() if isinstance(it, mx.Node))}

        for deps_file in deps_files:
            deps_file = Path(deps_file)
            if copy_deps:
                rel_path = deps_file.relative_to(deps_file.parent.parent)
                dest_path = root_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(deps_file, dest_path)
                deps_file = rel_path

            mx.prependXInclude(doc, str(deps_file))

    mx.writeToXmlFile(doc, str(filepath))
    log(f"Export MaterialX to {filepath}: completed successfully")


def temp_dir():
    d = Path(tempfile.gettempdir()) / TEMP_FOLDER
    if not d.is_dir():
        log("Creating temp dir", d)
        d.mkdir()

    return d


def clear_temp_dir():
    d = temp_dir()
    paths = tuple(d.iterdir())
    if not paths:
        return

    log("Clearing temp dir", d)
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)


def get_temp_file(suffix, name=None, is_rand=False):
    if not name:
        return Path(tempfile.mktemp(suffix, "tmp", temp_dir()))

    if suffix:
        if is_rand:
            return Path(tempfile.mktemp(suffix, f"{name}_", temp_dir()))

        name += suffix

    return temp_dir() / name


SUPPORTED_FORMATS = {".png", ".jpeg", ".jpg", ".hdr", ".tga", ".bmp"}
DEFAULT_FORMAT = ".hdr"
BLENDER_DEFAULT_FORMAT = "HDR"
BLENDER_DEFAULT_COLOR_MODE = "RGB"
READONLY_IMAGE_FORMATS = {".dds"}  # blender can read these formats, but can't write


def cache_image_file(image: bpy.types.Image, cache_check=True):
    image_path = Path(image.filepath_from_user())
    if not image.packed_file and image.source != 'GENERATED':
        if not image_path.is_file():
            # log.warn("Image is missing", image, image_path)
            return None

        image_suffix = image_path.suffix.lower()

        if image_suffix in SUPPORTED_FORMATS and \
                f".{image.file_format.lower()}" in SUPPORTED_FORMATS and not image.is_dirty:
            return image_path

        if image_suffix in READONLY_IMAGE_FORMATS:
            return image_path

    temp_path = get_temp_file(DEFAULT_FORMAT, image_path.stem, False)
    if cache_check and image.source != 'GENERATED' and temp_path.is_file():
        return temp_path

    scene = bpy.context.scene
    user_format = scene.render.image_settings.file_format
    user_color_mode = scene.render.image_settings.color_mode

    # in some scenes the color_mode is undefined
    # we can read it but unable to assign back, so switch it to 'RGB' if color_mode isn't selected
    if not user_color_mode:
        user_color_mode = 'RGB'

    scene.render.image_settings.file_format = BLENDER_DEFAULT_FORMAT
    scene.render.image_settings.color_mode = BLENDER_DEFAULT_COLOR_MODE

    try:
        image.save_render(filepath=str(temp_path))
    finally:
        scene.render.image_settings.file_format = user_format
        scene.render.image_settings.color_mode = user_color_mode

    return temp_path


def cache_image_file_path(image_path, cache_check=True):
    if image_path.suffix.lower() in SUPPORTED_FORMATS:
        return image_path

    if cache_check:
        temp_path = get_temp_file(DEFAULT_FORMAT, image_path.name)
        if temp_path.is_file():
            return temp_path

    image = bpy.data.images.load(str(image_path))
    try:
        return cache_image_file(image, cache_check)

    finally:
        bpy.data.images.remove(image)


def pass_node_reroute(link):
    while isinstance(link.from_node, bpy.types.NodeReroute):
        if not link.from_node.inputs[0].links:
            return None

        link = link.from_node.inputs[0].links[0]

    return link if link.is_valid else None


def update_ui(area_type='PROPERTIES', region_type='WINDOW'):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == area_type:
                for region in area.regions:
                    if region.type == region_type:
                        region.tag_redraw()


def update_materialx_data(depsgraph, materialx_data):
    if not depsgraph.updates:
        return

    for node_tree in (upd.id for upd in depsgraph.updates if isinstance(upd.id, bpy.types.ShaderNodeTree)):
        for material in bpy.data.materials:
            if material.node_tree and material.node_tree.name == node_tree.name:
                doc = export(material, None)
                if not doc:
                    # log.warn("MX export failed", mat)
                    continue

                matx_data = next((mat for mat in materialx_data if mat[0] == material.name), None)

                if not matx_data:
                    mx_file = get_temp_file(".mtlx",
                                            f'{material.name}{material.node_tree.name if material.node_tree else ""}',
                                            False)

                    mx.writeToXmlFile(doc, str(mx_file))
                    surfacematerial = next((node for node in doc.getNodes()
                                            if node.getCategory() == 'surfacematerial'))
                    materialx_data.append((material.name, str(mx_file), surfacematerial.getName()))
                else:
                    mx.writeToXmlFile(doc, str(matx_data[1]))


def import_materialx_from_file(node_tree, doc: mx.Document, file_path):
    def prepare_for_import():
        surfacematerial = next(
            (n for n in doc.getNodes() if n.getCategory() == 'surfacematerial'), None)
        if surfacematerial:
            return

        mat = doc.getMaterials()[0]
        sr = mat.getShaderRefs()[0]

        doc.removeMaterial(mat.getName())

        node_name = sr.getName()
        if not node_name.startswith("SR_"):
            node_name = f"SR_{node_name}"
        node = doc.addNode(sr.getNodeString(), node_name, 'surfaceshader')
        for sr_input in sr.getBindInputs():
            input = node.addInput(sr_input.getName(), sr_input.getType())
            ng_name = sr_input.getNodeGraphString()
            if ng_name:
                input.setAttribute('nodegraph', ng_name)
                input.setAttribute('output', sr_input.getOutputString())
            else:
                input.setValue(sr_input.getValue())

        surfacematerial = doc.addNode('surfacematerial', mat.getName(), 'material')
        input = surfacematerial.addInput('surfaceshader', node.getType())
        input.setNodeName(node.getName())

    def do_import():
        from .nodes import get_mx_node_cls

        node_tree.nodes.clear()

        def import_node(mx_node, mx_output_name=None, look_nodedef=True):
            mx_nodegraph = mx_node.getParent()
            node_path = mx_node.getNamePath()
            file_prefix = get_file_prefix(mx_node, file_path)

            if node_path in node_tree.nodes:
                return node_tree.nodes[node_path]

            try:
                MxNode_cls, data_type = get_mx_node_cls(mx_node)

            except KeyError as e:
                if not look_nodedef:
                    log.warn(e)
                    return None

                # looking for nodedef and switching to another nodegraph defined in doc
                nodedef = next(nd for nd in doc.getNodeDefs()
                               if nd.getNodeString() == mx_node.getCategory() and
                               nd.getType() == mx_node.getType())
                new_mx_nodegraph = next(ng for ng in doc.getNodeGraphs()
                                        if ng.getNodeDefString() == nodedef.getName())

                mx_output = new_mx_nodegraph.getActiveOutput(mx_output_name)
                node_name = mx_output.getNodeName()
                new_mx_node = new_mx_nodegraph.getNode(node_name)

                return import_node(new_mx_node, None, False)

            node = node_tree.nodes.new(MxNode_cls.bl_idname)
            node.name = node_path
            node.data_type = data_type
            nodedef = node.nodedef

            for mx_input in mx_node.getActiveInputs():
                input_name = mx_input.getName()
                nd_input = nodedef.getActiveInput(input_name)
                if nd_input.getAttribute('uniform') == 'true':
                    node.set_param_value(input_name, parse_value(
                        node, mx_input.getValue(), mx_input.getType(), file_prefix))
                    continue

                if input_name not in node.inputs:
                    log.error(f"Incorrect input name '{input_name}' for node {node}")
                    continue

                val = mx_input.getValue()
                if val is not None:
                    node.set_input_value(input_name, parse_value(
                        node, val, mx_input.getType(), file_prefix))
                    continue

                node_name = mx_input.getNodeName()

                if node_name:
                    new_mx_node = mx_nodegraph.getNode(node_name)
                    if not new_mx_node:
                        log.error(f"Couldn't find node '{node_name}' in nodegraph '{mx_nodegraph.getNamePath()}'")
                        continue

                    new_node = import_node(new_mx_node)

                    out_name = mx_input.getAttribute('output')
                    if len(new_node.nodedef.getActiveOutputs()) > 1 and out_name:
                        new_node_output = new_node.outputs[out_name]
                    else:
                        new_node_output = new_node.outputs[0]

                    node_tree.links.new(new_node_output, node.inputs[input_name])
                    continue

                new_nodegraph_name = mx_input.getAttribute('nodegraph')
                if new_nodegraph_name:
                    mx_output_name = mx_input.getAttribute('output')
                    new_mx_nodegraph = mx_nodegraph.getNodeGraph(new_nodegraph_name)
                    mx_output = new_mx_nodegraph.getActiveOutput(mx_output_name)
                    node_name = mx_output.getNodeName()
                    new_mx_node = new_mx_nodegraph.getNode(node_name)
                    new_node = import_node(new_mx_node, mx_output_name)
                    if not new_node:
                        continue

                    out_name = mx_output.getAttribute('output')
                    if len(new_node.nodedef.getActiveOutputs()) > 1 and out_name:
                        new_node_output = new_node.outputs[out_name]
                    else:
                        new_node_output = new_node.outputs[0]

                    node_tree.links.new(new_node_output, node.inputs[input_name])
                    continue

            node.check_ui_folders()
            return node

        mx_node = next(n for n in doc.getNodes() if n.getCategory() == 'surfacematerial')
        output_node = import_node(mx_node, 0)

        if not output_node:
            return

        # arranging nodes by layers
        layer = {output_node}
        layer_index = 0
        layers = {}
        while layer:
            new_layer = set()
            for node in layer:
                layers[node] = layer_index
                for inp in node.inputs:
                    for link in inp.links:
                        new_layer.add(link.from_node)
            layer = new_layer
            layer_index += 1

        node_layers = [[] for _ in range(max(layers.values()) + 1)]
        for node in node_tree.nodes:
            node_layers[layers[node]].append(node)

        # placing nodes by layers
        loc_x = 0
        for i, nodes in enumerate(node_layers):
            loc_y = 0
            for node in nodes:
                node.location = (loc_x, loc_y)
                loc_y -= NODE_LAYER_SHIFT_Y
                loc_x -= NODE_LAYER_SHIFT_X

            loc_x -= NODE_LAYER_SEPARATION_WIDTH

    prepare_for_import()
    do_import()


def export(material, obj: bpy.types.Object) -> [mx.Document, None]:
    from .bl_nodes.output import ShaderNodeOutputMaterial
    from .nodes.node import MxNode

    output_node = get_output_node(material)

    if not output_node:
        return None

    doc = mx.createDocument()

    if isinstance(output_node, MxNode):
        mx_node = output_node.compute('out', doc=doc)
        return doc

    node_parser = ShaderNodeOutputMaterial(doc, material, output_node, obj)
    if not node_parser.export():
        return None

    return doc


def get_materialx_data(material, obj: bpy.types.Object):
    doc = export(obj)
    if not doc:
        return None, None

    mtlx_file = get_temp_file(".mtlx", f'{material.name}_{material.node_tree.name if material.node_tree else ""}')
    mx.writeToXmlFile(doc, str(mtlx_file))

    return mtlx_file, doc


def get_output_node(material):
    if not material.node_tree:
        return None

    bl_output_node = next((node for node in material.node_tree.nodes if
                 node.bl_idname == 'ShaderNodeOutputMaterial' and
                 node.is_active_output and node.inputs['Surface'].links), None)

    if bl_output_node:
        return bl_output_node

    mx_output_node = next((node for node in material.node_tree.nodes if
                 node.bl_idname == with_prefix('MxNode_STD_surfacematerial') and
                 node.inputs['surfaceshader'].links), None)

    return mx_output_node
