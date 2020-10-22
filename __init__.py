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
    "author": "Blendfx, Jonas Dichelle, Simeon Conzendorf",
    "version": (0, 0, 3),
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
    b_forceKeys: bpy.props.BoolProperty(name="force start/end keyframes")
    b_activeCol: bpy.props.BoolProperty(name="active colection",default=False)
    b_leaveBones: bpy.props.BoolProperty(name="add leave bones",default=False)
    b_filenameIsCollection: bpy.props.BoolProperty(name="name file like collection",default=False)

def main(context):
    blendpath = Path(bpy.data.filepath)
    print ("blendpath " + str(blendpath))    
    filename = str (Path(blendpath).stem)
    
    if context.scene.fbx_props.fbx_path:        
        fbxpath = str(Path(bpy.path.abspath(context.scene.fbx_props.fbx_path)) / Path(blendpath).stem)        
        print ("abolute: "+fbxpath)
    else:
        fbxpath = str(Path(blendpath).parent / Path(blendpath).stem)        
        fbxpath = fbxpath.replace(".","")
        print("relative "+fbxpath)
    
    if context.scene.fbx_props.b_activeCol:
        collectionName = context.view_layer.active_layer_collection.name
        
        if context.scene.fbx_props.b_filenameIsCollection:
            fbxpath = fbxpath.replace(filename,collectionName)
        else:
            fbxpath = fbxpath+"_"+collectionName

    fbxpath = fbxpath+".fbx"
    print(fbxpath +" "+filename)    
        
    bpy.ops.export_scene.fbx(filepath=str(fbxpath),
        check_existing=True,
        filter_glob="*.fbx",
        use_selection=False,
        use_active_collection=context.scene.fbx_props.b_activeCol,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=False,
        object_types={'ARMATURE', 'EMPTY', 'MESH', 'OTHER'},
        use_mesh_modifiers=True,
        use_mesh_modifiers_render=True,
        mesh_smooth_type='OFF',
        use_subsurf=False,
        use_mesh_edges=False,
        use_tspace=False,
        use_custom_props=True,
        add_leaf_bones=context.scene.fbx_props.b_leaveBones,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_armature_deform_only=False,
        armature_nodetype='NULL',
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=context.scene.fbx_props.b_forceKeys,
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
        layout.prop(props, "b_forceKeys", expand=True)
        layout.prop(props, "b_activeCol", expand=True)
        layout.prop(props, "b_leaveBones", expand=True)
        layout.prop(props, "b_filenameIsCollection", expand=True)       
        

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
