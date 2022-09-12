# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2022, AMD

import bpy

from ..matlib.manager import manager
from ..utils import MaterialXProperties


class MatlibProperties(bpy.types.PropertyGroup):
    def get_materials(self) -> dict:
        materials = {}
        search_str = self.search.strip().lower()

        materials_list = manager.materials_list
        for mat in materials_list:
            if search_str not in mat.title.lower():
                continue

            if not (mat.category.id == self.category_id or self.category_id == 'ALL'):
                continue

            materials[mat.id] = mat

        return materials

    def get_materials_prop(self, context):
        materials = []
        for i, mat in enumerate(sorted(self.get_materials().values())):
            description = mat.title
            if mat.description:
                description += f"\n{mat.description}"
            description += f"\nCategory: {mat.category.title}\nAuthor: {mat.author}"

            icon_id = mat.renders[0].thumbnail_icon_id if mat.renders else 'MATERIAL'
            materials.append((mat.id, mat.title, description, icon_id, i))

        return materials

    def get_categories_prop(self, context):
        categories = []
        if manager.categories is None:
            return categories

        categories += [('ALL', "All Categories", "Show materials for all categories")]

        categories_list = manager.categories_list
        categories += ((cat.id, cat.title, f"Show materials with category {cat.title}")
                       for cat in sorted(categories_list))
        return categories

    def get_packages_prop(self, context):
        packages = []
        mat = self.material
        if not mat:
            return packages

        for i, p in enumerate(sorted(mat.packages)):
            description = f"Package: {p.label} ({p.size_str})\nAuthor: {p.author}"
            if p.has_file:
                description += "\nReady to import"
            icon_id = 'RADIOBUT_ON' if p.has_file else 'RADIOBUT_OFF'

            packages.append((p.id, f"{p.label} ({p.size_str})", description, icon_id, i))

        return packages

    def update_material(self, context):
        mat = self.material
        if mat:
            self.package_id = min(mat.packages).id

    def update_category(self, context):
        materials = self.get_materials()
        if not materials:
            return

        mat = min(materials.values())
        self.material_id = mat.id
        self.package_id = min(mat.packages).id

    def update_search(self, context):
        materials = self.get_materials()
        if not materials or self.material_id in materials:
            return

        mat = min(materials.values())
        self.material_id = mat.id
        self.package_id = min(mat.packages).id

    material_id: bpy.props.EnumProperty(
        name="Material",
        description="Select material",
        items=get_materials_prop,
        update=update_material,
    )
    category_id: bpy.props.EnumProperty(
        name="Category",
        description="Select materials category",
        items=get_categories_prop,
        update=update_category,
    )
    search: bpy.props.StringProperty(
        name="Search",
        description="Search materials by title",
        update=update_search,
    )
    package_id: bpy.props.EnumProperty(
        name="Package",
        description="Selected material package",
        items=get_packages_prop,
    )

    @property
    def material(self):
        return manager.materials.get(self.material_id)

    @property
    def package(self):
        mat = self.material
        if not mat:
            return None

        return next((p for p in mat.packages if p.id == self.package_id), None)


class WindowManagerProperties(MaterialXProperties):
    bl_type = bpy.types.WindowManager

    matlib: bpy.props.PointerProperty(type=MatlibProperties)
