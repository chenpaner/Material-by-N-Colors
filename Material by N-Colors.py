
bl_info = {
    "name" : "Material by N-Colors",
    "author" : "CP", 
    "description" : "通过给物体添加属性来控制材质颜色，实现同材质不同色的功能",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "节点编辑器>工具>Material by N-Colors",
    "warning" : "",
    "doc_url": "https://space.bilibili.com/2711518?spm_id_from=333.788.0.0", 
    "tracker_url": "", 
    "category" : "Material" 
}


import bpy
import math

class SNA_OT_Operator_285D0(bpy.types.Operator):
    bl_idname = "sna.operator_285d0"
    bl_label = "Operator"
    bl_description = "Add CP Custom colors for selected objects \nAdd node"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        # # 获取所有选中的物体
        # selected_objects = bpy.context.selected_objects
        # # 遍历选中的物体
        # for obj in selected_objects:


        # 获取场景中所有物体
        all_objects = bpy.context.scene.objects
        # 存储具有活动材质的物体
        objects_with_active_material = []
        # 遍历场景中的所有物体
        for obj in all_objects:
            # 检查每个材质槽是否存在且是否包含活动材质    如果是钉住编辑器了，应该是检查材质节点树是当前的编辑材质节点树！！！可以判断钉住编辑器后不显示面板，编辑节点树不等于活动材质节点树
            if any(slot.material == bpy.context.object.active_material for slot in obj.material_slots):
                objects_with_active_material.append(obj)

        for obj in objects_with_active_material:
            # 检查物体是否为网格
            #if obj.type == 'MESH':
            if "CP Custom colors" not in obj:
                obj["CP Custom colors"]= bpy.context.scene.sna_cp_custom_colors#(1.0, 1.0, 1.0, 1.0)
                #obj["CP Custom colors"]=(1.0, 0.0, 0.0)
                #del obj["CP Custom colors"]
            # get or create the UI object for the property
            ui = obj.id_properties_ui("CP Custom colors")
            ui.update(description = "设置活动物体的属性颜色,方便多个物体同材质但不同色")
            ui.update(subtype='COLOR')
            ui.update(default=(1.0, 1.0,1.0,1.0))     
            ui.update(min=0.0, soft_min=0.0)
            ui.update(max=1.0, soft_max=1.0)
        
        # 获取当前节点编辑器的节点树
        node_tree = context.space_data.edit_tree
        havenode=None
        for node in node_tree.nodes:
            node.select = False
            if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Custom colors':
                havenode=node#这行代码能否简化
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

        bpy.types.Scene.shoud_refresh_color=True
        return {"FINISHED"}

class SNA_OT_Operator001_D53F7(bpy.types.Operator):
    bl_idname = "sna.operator001_d53f7"
    bl_label = "Refresh color"
    bl_description = "The material color is not updated until it is refreshed\n刷新后才会更新材质颜色"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        bpy.ops.ed.undo('INVOKE_DEFAULT', )
        bpy.ops.ed.redo('INVOKE_DEFAULT', )
        # for area in context.screen.areas:
        #     area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        bpy.types.Scene.shoud_refresh_color=False
        return self.execute(context)

def are_colors_almost_equal(color1, color2, threshold=0.001):
    """检查两个颜色是否在给定的阈值内几乎相等。"""
    for c1, c2 in zip(color1, color2):
        # 使用 math.isclose 函数比较两个颜色分量是否几乎相等
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

        # 取消选择所有物体
        bpy.ops.object.select_all(action='DESELECT')

        # 遍历场景中的所有物体
        for obj in bpy.context.scene.objects:
            # 检查物体是否具有指定的属性并且属性值与活动物体的属性值几乎相同
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
        return  data.tree_type == "ShaderNodeTree" and data.node_tree != world.node_tree and data.edit_tree #len(bpy.context.selected_objects) > 0 and

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj and "CP Custom colors" in obj :
            row_30EA9 = layout.row(heading='', align=True)

            row_30EA9.label(text='', icon_value=551)

            row_3835D = row_30EA9.row(heading='', align=False)

            attr_85EE8 = '["' + str('CP Custom colors' + '"]') 
            row_3835D.prop(bpy.context.view_layer.objects.active, attr_85EE8, text='', icon_value=0, emboss=True)

            #row_3835D.label(text='选择和活动物体一样材质，并且属性的颜色一样的物体', icon_value=256)
            row_3835D.operator('sna.select_same_attribute', text='', icon_value=256, emboss=True, depress=False)
        else:
            layout.label(text='活动物体没[CP Custom colors]属性', icon='ERROR')

        if (len(bpy.context.selected_objects) > 1):
            row_61394 = layout.row(heading='', align=True)
            if bpy.types.Scene.shoud_refresh_color==True:
                row_61394.alert = True
                #row_61394.label(text='刷新后才会更新材质颜色', icon_value=692)
                row_61394.operator('sna.operator001_d53f7', text='马上刷新后才会更新材质颜色', icon_value=692, emboss=True, depress=False)
            else:
                row_61394.alert = False

                row_61394.label(text='', icon_value=580)
            row_61394.prop(bpy.context.scene, 'sna_cp_custom_colors', text='', icon_value=0, emboss=True)

        op = layout.operator('sna.operator_285d0', text='Add ', icon="ADD", emboss=True, depress=False)
        #为添加属性后没有自动刷新，要手动刷新下
        row_61394 = layout.row(heading='', align=True)
        if bpy.types.Scene.shoud_refresh_color==True:
            row_61394.alert = True
            #row_61394.label(text='刷新后才会更新材质颜色', icon_value=692)
            row_61394.operator('sna.operator001_d53f7', text='马上刷新后才会更新材质颜色', icon_value=692, emboss=True, depress=False)

def sna_update_sna_cp_custom_colors_C1A81(self, context):
    new_color = self.sna_cp_custom_colors
    # 获取所有选中的物体
    selected_objects = bpy.context.selected_objects
    # 遍历选中的物体
    for obj in selected_objects:
        # 检查物体是否为网格
        if obj.type == 'MESH':
    #        if "CP Custom colors" not in obj:
    #            obj["CP Custom colors"]=(1.0, 1.0,1.0,1.0)
    #            # get or create the UI object for the property
    #            ui = obj.id_properties_ui("CP Custom colors")
    #            ui.update(description = "自定义颜色,方便多个物体同材质但不同色")
    #            ui.update(subtype='COLOR')
    #            ui.update(default=(1.0, 1.0,1.0,1.0))     
    #            ui.update(min=0.0, soft_min=0.0)
    #            ui.update(max=1.0, soft_max=1.0)
    #        else:
            obj["CP Custom colors"]=new_color
            bpy.types.Scene.shoud_refresh_color=True

    # for area in context.screen.areas:
    #     area.tag_redraw()

def register():
    bpy.types.Scene.sna_cp_custom_colors = bpy.props.FloatVectorProperty(
        name='', description='设置所有选中物体的属性颜色\n设置属性后要马上刷新颜色!', 
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 
        update=sna_update_sna_cp_custom_colors_C1A81
        )

    bpy.types.Scene.shoud_refresh_color = bpy.props.BoolProperty(name = "", description = "", default = False)

    bpy.utils.register_class(SNA_OT_Operator_285D0)
    bpy.utils.register_class(SNA_OT_Operator001_D53F7)
    bpy.utils.register_class(SNA_OT_SelectObjectsWithSameAttribute)

    bpy.utils.register_class(SNA_PT_MATERIAL_BY_NCOLORS_85AF2)


def unregister():
    del bpy.types.Scene.sna_cp_custom_colors
    del bpy.types.Scene.shoud_refresh_color
    bpy.utils.unregister_class(SNA_OT_Operator_285D0)
    bpy.utils.unregister_class(SNA_OT_Operator001_D53F7)
    bpy.utils.unregister_class(SNA_OT_SelectObjectsWithSameAttribute)

    bpy.utils.unregister_class(SNA_PT_MATERIAL_BY_NCOLORS_85AF2)
