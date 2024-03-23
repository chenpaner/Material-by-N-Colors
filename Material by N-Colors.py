
bl_info = {
    "name" : "Material by N-Colors",
    "author" : "chenpaner", 
    "description" : "通过给物体添加属性来控制材质颜色,实现同材质不同色的功能 Control the color of the material by adding attributes to the object to achieve the function of different colors for the same material",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "节点编辑器>工具>Material by N-Colors",
    "warning" : "",
    "doc_url": "https://github.com/chenpaner", 
    "tracker_url": "", 
    "category" : "Material" 
}

import bpy
import math
from bpy.app.handlers import persistent

class SNA_OT_Operator_285D0(bpy.types.Operator):
    bl_idname = "sna.operator_285d0"
    bl_label = "Operator"
    bl_description = "Add a Custom to all objects with this material\nAdd node"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        all_objects = bpy.context.scene.objects

        objects_with_active_material = []

        for obj in all_objects:

            if any(slot.material == bpy.context.object.active_material for slot in obj.material_slots):
                objects_with_active_material.append(obj)

        for obj in objects_with_active_material:

            if "CP Custom colors" not in obj:
                obj["CP Custom colors"]= bpy.context.scene.sna_cp_custom_colors
                obj.data.update()

            ui = obj.id_properties_ui("CP Custom colors")
            ui.update(description = "设置活动物体的属性颜色,方便多个物体同材质但不同色")
            ui.update(subtype='COLOR')
            ui.update(default=(1.0, 1.0,1.0,1.0))     
            ui.update(min=0.0, soft_min=0.0)
            ui.update(max=1.0, soft_max=1.0)

        node_tree = context.space_data.edit_tree
        havenode=None
        for node in node_tree.nodes:
            node.select = False
            if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Custom colors':
                havenode=node
                context.space_data.edit_tree.nodes.active = node
                node.select = True
                bpy.ops.node.view_selected()

        if havenode is None:
            prev_context = bpy.context.area.type
            bpy.context.area.type = 'NODE_EDITOR'
            bpy.ops.node.add_node('INVOKE_DEFAULT', use_transform=True, type='ShaderNodeAttribute')
            bpy.context.area.type = prev_context

            node_tree.nodes[-1].name = 'CP Custom colors'
            node_tree.nodes[-1].label = 'CP Custom colors'
            node_tree.nodes[-1].attribute_type = 'OBJECT'
            node_tree.nodes[-1].attribute_name = 'CP Custom colors'
            node_tree.nodes[-1].width=173

            node_tree.nodes[-1].outputs[1].hide=True
            node_tree.nodes[-1].outputs[2].hide=True
            node_tree.nodes[-1].show_options=False

        return {"FINISHED"}

def are_colors_almost_equal(color1, color2, threshold=0.001):
    """检查两个颜色是否在给定的阈值内几乎相等。"""
    for c1, c2 in zip(color1, color2):
        if math.isclose(c1, c2, rel_tol=threshold):
            continue
        else:
            return False
    return True

class SNA_OT_SelectObjectsWithSameAttribute(bpy.types.Operator):
    bl_idname = "sna.select_same_attribute"
    bl_label = "Select Objects with Same Attribute"
    bl_description = "选择与活动对象属性颜色一样的物体,让后统一设置设置"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        active_object = context.object
        attribute_name = "CP Custom colors"
        attribute_value = active_object.get(attribute_name)

        bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.context.scene.objects:

            if attribute_name in obj and are_colors_almost_equal(obj.get(attribute_name), attribute_value):
                obj.select_set(True)

        return {'FINISHED'}

class SNA_PT_MATERIAL_BY_NCOLORS_85AF2(bpy.types.Panel):
    bl_label = 'Material by N-Colors'
    bl_idname = 'SNA_PT_MATERIAL_BY_NCOLORS_85AF2'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        world = context.scene.world
        data=context.space_data
        return  data.tree_type == "ShaderNodeTree" and data.node_tree != world.node_tree and data.edit_tree 

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj and "CP Custom colors" in obj :
            row_30EA9 = layout.row(heading='', align=True)

            row_30EA9.label(text='', icon_value=551)

            row_3835D = row_30EA9.row(heading='', align=False)

            row_3835D.prop(bpy.context.scene, 'sna_byactive_cp_custom_colors', text='', icon_value=0, emboss=True)

            row_3835D.operator('sna.select_same_attribute', text='', icon_value=256, emboss=True, depress=False)
        else:
            layout.label(text='活动物体没[CP Custom colors]属性', icon='ERROR')

        row_61394 = layout.row(heading='', align=True)

        row_61394.label(text='', icon_value=580)
        row_61394.prop(bpy.context.scene, 'sna_cp_custom_colors', text='', icon_value=0, emboss=True)

        row = layout.row(heading='', align=True)
        row.scale_y = 1.0
        icon="ADD"
        all_objects = bpy.context.scene.objects
        objects_with_active_material = []
        for obj in all_objects:
            if any(slot.material == bpy.context.object.active_material for slot in obj.material_slots):
                objects_with_active_material.append(obj)
        for obj in objects_with_active_material:
            if "CP Custom colors" not in obj:
                row.alert = True
                icon="FILE_REFRESH"
                row.scale_y = 2.0

        row.operator('sna.operator_285d0', text='Add ', icon=icon, emboss=True, depress=False)

def sna_update_sna_cp_custom_colors_C1A81(self, context):
    new_color = self.sna_cp_custom_colors
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        obj["CP Custom colors"]=new_color
        obj.data.update()

@persistent
def get_active_color(scene, depsgraph):
    active_object = bpy.context.object
    if active_object:
        attribute_name = "CP Custom colors"
        attribute_value = active_object.get(attribute_name)
        if attribute_value:
            scene.sna_byactive_cp_custom_colors = attribute_value

def update_active_color(self, context):
    new_color = self.sna_byactive_cp_custom_colors
    active_object = context.object
    attribute_name = "CP Custom colors"
    attribute_value = active_object.get(attribute_name)

    for obj in bpy.context.scene.objects:
        if obj != active_object:

            if attribute_name in obj and are_colors_almost_equal(obj.get(attribute_name), attribute_value):

                obj["CP Custom colors"]=new_color
                obj.data.update()

    active_object["CP Custom colors"]=new_color
    active_object.data.update()

def register():
    bpy.types.Scene.sna_cp_custom_colors = bpy.props.FloatVectorProperty(
        name='Sets the property color of all selected objects', description='设置所有选中物体的属性颜色', 
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 
        update=sna_update_sna_cp_custom_colors_C1A81
        )

    bpy.types.Scene.sna_byactive_cp_custom_colors = bpy.props.FloatVectorProperty(
        name='Also adjust the attribute color of the same attribute color as the active object', description='同时调整与活动物体同属性颜色的属性颜色', 
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 

        update=update_active_color,
        )

    bpy.app.handlers.depsgraph_update_post.append(get_active_color)

    bpy.utils.register_class(SNA_OT_Operator_285D0)
    bpy.utils.register_class(SNA_OT_SelectObjectsWithSameAttribute)

    bpy.utils.register_class(SNA_PT_MATERIAL_BY_NCOLORS_85AF2)

def unregister():
    del bpy.types.Scene.sna_cp_custom_colors
    del bpy.types.Scene.sna_byactive_cp_custom_colors
    bpy.app.handlers.depsgraph_update_post.remove(get_active_color)

    bpy.utils.unregister_class(SNA_OT_Operator_285D0)
    bpy.utils.unregister_class(SNA_OT_SelectObjectsWithSameAttribute)

    bpy.utils.unregister_class(SNA_PT_MATERIAL_BY_NCOLORS_85AF2)

if __name__ == "__main__":
    register()