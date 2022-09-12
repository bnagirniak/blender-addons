import bpy

from . import ui


register_ui, unregister_ui = bpy.utils.register_classes_factory(
    [
        ui.MATLIB_PT_matlib,
        ui.MATLIB_PT_matlib_tools,
        ui.MATLIB_OP_load_materials,
        ui.MATLIB_OP_load_package,
        ui.MATLIB_OP_import_material,
        ui.MATERIAL_OP_matlib_clear_search,
    ]
)


def register():
    register_ui()


def unregister():
    unregister_ui()