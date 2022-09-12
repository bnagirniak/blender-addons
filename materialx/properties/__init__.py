import bpy


class MaterialXProperties(bpy.types.PropertyGroup):
    bl_type = None

    @classmethod
    def register(cls):
        setattr(cls.bl_type, "materialx", bpy.props.PointerProperty(
            name="MaterialX properties",
            description="MaterialX properties",
            type=cls,
        ))

    @classmethod
    def unregister(cls):
        delattr(cls.bl_type, "materialx")


from . import matlib


register_properties, unregister_properties = bpy.utils.register_classes_factory([
    matlib.MatlibProperties,
    matlib.WindowManagerProperties,
    ])


def register():
    register_properties()


def unregister():
    unregister_properties()