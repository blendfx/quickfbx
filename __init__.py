import bpy, math
from mathutils import Matrix
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
    "author": "Blendfx, Jonas Dichelle, Simeon Conzendorf, Clemens Beute",
    "version": (0, 0, 4),
    "blender": (2, 80, 0),
    "location": "Properties > Scene",
    "category": "Export"
}

# oooooo     oooo                     o8o             .o8       oooo
#  `888.     .8'                      `"'            "888       `888
#   `888.   .8'    .oooo.   oooo d8b oooo   .oooo.    888oooo.   888   .ooooo.   .oooo.o 
#    `888. .8'    `P  )88b  `888""8P `888  `P  )88b   d88' `88b  888  d88' `88b d88(  "8 
#     `888.8'      .oP"888   888      888   .oP"888   888   888  888  888ooo888 `"Y88b.  
#      `888'      d8(  888   888      888  d8(  888   888   888  888  888    .o o.  )88b 
#       `8'       `Y888""8o d888b    o888o `Y888""8o  `Y8bod8P' o888o `Y8bod8P' 8""888P' 

class FbxProps(PropertyGroup):
    fbx_path: StringProperty(
        name = "path",
        description="Path to save fbx to",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    b_selectedObjs: bpy.props.BoolProperty(name="only selected objects",default=False)
    b_activeCol: bpy.props.BoolProperty(name="only active colection",default=False)
    b_filenameIsCollection: bpy.props.BoolProperty(name="name file like collection",default=False)
    b_forceKeys: bpy.props.BoolProperty(name="force start/end keyframes",default=False)
    b_leaveBones: bpy.props.BoolProperty(name="add leave bones",default=False)

# oooooooooooo                                       .    o8o
# `888'     `8                                     .o8    `"'
#  888         oooo  oooo  ooo. .oo.    .ooooo.  .o888oo oooo   .ooooo.  ooo. .oo.    .oooo.o 
#  888oooo8    `888  `888  `888P"Y88b  d88' `"Y8   888   `888  d88' `88b `888P"Y88b  d88(  "8 
#  888    "     888   888   888   888  888         888    888  888   888  888   888  `"Y88b.  
#  888          888   888   888   888  888   .o8   888 .  888  888   888  888   888  o.  )88b 
# o888o         `V88V"V8P' o888o o888o `Y8bod8P'   "888" o888o `Y8bod8P' o888o o888o 8""888P' 

def apply_obj_rotation(obj=None):
    # https://blender.stackexchange.com/questions/159538/how-to-apply-all-transformations-to-an-object-at-low-level
    # https://blenderartists.org/t/apply-transform-and-rotation-without-ops/1217959
    
    loc, rot, scale = obj.matrix_world.decompose()

    # save the child object states    
    children = [(child, child.matrix_world) for child in obj.children]

    # save the obj scale
    scale_matrix = Matrix()
    for i in range(3):
        scale_matrix[i][i] = scale[i]

    # save the obj rotation
    rot_matrix = rot.to_matrix().to_4x4()

    # get a clean matrix with 0 rotaion but with saved locatioan and scale
    new_matrix = Matrix.Translation(loc) @ scale_matrix

    # apply the rotation on a mesh level
    if obj.data is not None:
        obj.data.transform(rot_matrix)

    # set the clean matrix
    obj.matrix_world = new_matrix
    
    
    # reset the child states
    for obj, child_matrix in children:
        obj.matrix_world = child_matrix
    
    bpy.context.view_layer.update()

def apply_obj_modifiers(obj=None):
    # https://blender.community/c/rightclickselect/xcfbbc/?sorting=hot
    if obj.type == 'MESH':
        modifiers = [mod.type for mod in obj.modifiers]
        print(modifiers)
        if not 'ARMATURE' in modifiers:
            # objects with armature werden einfach ignoriert -> später vlt alle modifier bis auf die armature anwenden?
            if obj.data is not None:
                dg = bpy.context.view_layer.depsgraph
                dg.update()
                eval_obj = obj.evaluated_get(dg)
                applied_mesh = bpy.data.meshes.new_from_object(eval_obj, depsgraph=dg)

                obj.modifiers.clear()
                obj.data = applied_mesh

def recursivlely_apply_children(obj=None):
    """recursively go trough every child and apply transform"""
    if obj.children == ():
        return 'FINISHED'
    else:
        for child_obj in obj.children:
            print(child_obj.name)
            apply_obj_rotation(obj=child_obj)
            recursivlely_apply_children(obj=child_obj)
    
def rotate_obj(obj=None, rot=[0,0,0]):
    obj.rotation_euler.x = math.radians(rot[0])
    obj.rotation_euler.y = math.radians(rot[1])
    obj.rotation_euler.z = math.radians(rot[2])
    bpy.context.view_layer.update()

#   .oooooo.                                               .
#  d8P'  `Y8b                                            .o8
# 888      888 oo.ooooo.   .ooooo.  oooo d8b  .oooo.   .o888oo  .ooooo.  oooo d8b  .oooo.o
# 888      888  888' `88b d88' `88b `888""8P `P  )88b    888   d88' `88b `888""8P d88(  "8
# 888      888  888   888 888ooo888  888      .oP"888    888   888   888  888     `"Y88b.
# `88b    d88'  888   888 888    .o  888     d8(  888    888 . 888   888  888     o.  )88b
#  `Y8bood8P'   888bod8P' `Y8bod8P' d888b    `Y888""8o   "888" `Y8bod8P' d888b    8""888P'
#               888
#              o888o

class QuickFBX(bpy.types.Operator):
    """Quick FBX exporter"""
    bl_idname = "wm.quick_fbx"
    bl_label = "Quick Fbx"

    def execute(self, context):
        # filepath construction
        blendpath = Path(bpy.data.filepath)
        print ("blendpath: " + str(blendpath))
        
        parentPath = blendpath.parent
        print ("parent: "+str(parentPath))
        
        filename = str (blendpath.stem)
        filename = filename.replace(".","")
        print ("file " + filename)    

        if context.scene.fbx_props.b_activeCol:
            collectionName = context.view_layer.active_layer_collection.name
            
            if context.scene.fbx_props.b_filenameIsCollection:
                filename = collectionName
            else:
                filename = filename+"_"+collectionName
        
        if context.scene.fbx_props.fbx_path:        
            fbxpath = str(Path(bpy.path.abspath(context.scene.fbx_props.fbx_path)) / Path(filename))
            print ("abolute: "+fbxpath)
        else:
            fbxpath = str(parentPath / Path(filename))
            print("relative "+fbxpath)    

        fbxpath = fbxpath+".fbx"    

        # save the scene state in undo history
        bpy.ops.ed.undo_push(message="before_export_changes")
        

        # prep the assets for export (axles and rotation issue fix)
        # get the objects wich need to be changed
        if context.scene.fbx_props.b_selectedObjs:
            objects_to_export = bpy.context.selected_objects
        elif context.scene.fbx_props.b_activeCol:
            objects_to_export = [obj for obj in bpy.context.view_layer.active_layer_collection.collection.objects]
        elif context.scene.fbx_props.b_selectedObjs and context.scene.fbx_props.b_activeCol:
            selected_collection_objects = []
            for obj in [obj for obj in bpy.context.view_layer.active_layer_collection.collection.objects]:
                if obj in bpy.context.selected_objects:
                    selected_collection_objects.append(obj)
            objects_to_export = selected_collection_objects
        else:
            objects_to_export = bpy.context.scene.objects

        # get just the parent ones
        parent_objs = [obj for obj in objects_to_export if obj.parent == None]

        print(objects_to_export)
        print(parent_objs)

        # apply the modifiers first
        for obj in objects_to_export:
            apply_obj_modifiers(obj=obj)

        # do rotation stuff just on parents
        for obj in parent_objs:
            # UNITY fix 180° aka axels issue
            # (x should stay same and positive)
            # (y and z should swap, but also stay positive)
            rotate_obj(obj=obj, rot=[0,0,180])
            apply_obj_rotation(obj=obj)
            # look for childrens and also apply transform
            recursivlely_apply_children(obj=obj)

            # UNITY fix -89.99° issue
            rotate_obj(obj=obj, rot=[-90,0,0])
            apply_obj_rotation(obj=obj)
            # # look for childrens and also apply transform
            recursivlely_apply_children(obj=obj)
            rotate_obj(obj=obj, rot=[90,0,0])

        bpy.ops.ed.undo_push(message="after_export_changes")

        # fbx export
        bpy.ops.export_scene.fbx(filepath=str(fbxpath),
            check_existing=True,
            filter_glob="*.fbx",
            use_selection=context.scene.fbx_props.b_selectedObjs,
            use_active_collection=context.scene.fbx_props.b_activeCol,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL', # was FBX_SCALE_ALL - why was that? -> FBX_SCALE_NONE is needed, to have 0 rotaion on import in unity
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

        # restore the scene state from undo history
        bpy.ops.ed.undo()

        return {'FINISHED'}

# ooooo     ooo                                ooooo                 .                       .o88o.
# `888'     `8'                                `888'               .o8                       888 `"
#  888       8   .oooo.o  .ooooo.  oooo d8b     888  ooo. .oo.   .o888oo  .ooooo.  oooo d8b o888oo   .oooo.    .ooooo.   .ooooo.  
#  888       8  d88(  "8 d88' `88b `888""8P     888  `888P"Y88b    888   d88' `88b `888""8P  888    `P  )88b  d88' `"Y8 d88' `88b 
#  888       8  `"Y88b.  888ooo888  888         888   888   888    888   888ooo888  888      888     .oP"888  888       888ooo888 
#  `88.    .8'  o.  )88b 888    .o  888         888   888   888    888 . 888    .o  888      888    d8(  888  888   .o8 888    .o 
#    `YbodP'    8""888P' `Y8bod8P' d888b       o888o o888o o888o   "888" `Y8bod8P' d888b    o888o   `Y888""8o `Y8bod8P' `Y8bod8P' 

class Quick_fbx_panel(Panel):
    bl_label = "Quick FBX Export"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        props = context.scene.fbx_props
        layout = self.layout

        layout.label(text="What do you want to export?")
        layout.prop(props, "b_selectedObjs")
        layout.prop(props, "b_activeCol")
        if context.scene.fbx_props.b_activeCol:
            split = layout.split(factor=0.03)
            split.separator_spacer()
            split.prop(props, "b_filenameIsCollection")
        col = layout.column()
        col.enabled = False
        col.label(text="Or just leave empty to export everything")
    
        layout.separator()

        layout.label(text="Extra Options:")
        layout.prop(props, "b_forceKeys")
        layout.prop(props, "b_leaveBones")

        layout.separator()

        layout.prop(props, "fbx_path", expand=True)
        layout.operator("wm.quick_fbx", icon="EXPORT")
        
# ooooooooo.                         o8o               .                          .    o8o
# `888   `Y88.                       `"'             .o8                        .o8    `"'
#  888   .d88'  .ooooo.   .oooooooo oooo   .oooo.o .o888oo oooo d8b  .oooo.   .o888oo oooo   .ooooo.  ooo. .oo.
#  888ooo88P'  d88' `88b 888' `88b  `888  d88(  "8   888   `888""8P `P  )88b    888   `888  d88' `88b `888P"Y88b
#  888`88b.    888ooo888 888   888   888  `"Y88b.    888    888      .oP"888    888    888  888   888  888   888
#  888  `88b.  888    .o `88bod8P'   888  o.  )88b   888 .  888     d8(  888    888 .  888  888   888  888   888
# o888o  o888o `Y8bod8P' `8oooooo.  o888o 8""888P'   "888" d888b    `Y888""8o   "888" o888o `Y8bod8P' o888o o888o
#                        d"     YD
#                        "Y88888P'

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