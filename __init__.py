import bpy
from pathlib import Path
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

bl_info = {
    "name": "Quick Fbx",
    "description": "One button. One Fbx. Boom. It's that simple.",
    "author": "Blendfx, Jonas Dichelle",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Scene",
    "category": "Export"
}

class FbxProps(PropertyGroup):
    fbx_path: StringProperty(
        name = "fbx export path",
        description="Path to save fbx to",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

def main(context):
    blendpath = Path(bpy.data.filepath)
    if context.scene.fbx_props.fbx_path:
        absolute = Path(bpy.path.abspath(context.scene.fbx_props.fbx_path))
        fbxpath = Path(context.scene.fbx_props.fbx_path) / Path(blendpath).stem
    else:
        fbxpath = Path(blendpath).parent / Path(blendpath).stem
    bpy.ops.export_scene.fbx(filepath=str(fbxpath) + "_export.fbx",
        check_existing=True,
        filter_glob="*.fbx",
        use_selection=False,
        use_active_collection=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        bake_space_transform=False,
        object_types={'ARMATURE', 'EMPTY', 'MESH', 'OTHER'},
        use_mesh_modifiers=True,
        use_mesh_modifiers_render=True,
        mesh_smooth_type='OFF',
        use_subsurf=False,
        use_mesh_edges=False,
        use_tspace=False,
        use_custom_props=True,
        add_leaf_bones=True,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_armature_deform_only=False,
        armature_nodetype='NULL',
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=1.0,
        path_mode='AUTO',
        embed_textures=False,
        batch_mode='OFF',
        use_batch_own_dir=True,
        use_metadata=True,
        axis_forward='-Z',
        axis_up='Y'
    )
    print("working")

class QuickFBX(bpy.types.Operator):
    """Quick FBX exporter"""
    bl_idname = "wm.quick_fbx"
    bl_label = "Quick Fbx"

    def execute(self, context):
        main(context)
        return {'FINISHED'}


class Quick_fbx_panel(Panel):
    bl_label = "Quick FBX Panel"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        props = context.scene.fbx_props
        layout = self.layout
        scene = context.scene
        layout.operator("wm.quick_fbx")
        layout.prop(props, "fbx_path", expand=True)

def register():
    bpy.utils.register_class(QuickFBX)
    bpy.utils.register_class(FbxProps)
    bpy.utils.register_class(Quick_fbx_panel)
    bpy.types.Scene.fbx_props = PointerProperty(type=FbxProps)

def unregister():
    bpy.utils.unregister_class(QuickFBX)
    bpy.utils.unregister_class(FbxProps)
    bpy.utils.unregister_class(Quick_fbx_panel)

    del bpy.types.Scene.fbx_props


if __name__ == "__main__":
    register()
