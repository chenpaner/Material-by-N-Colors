
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
    "category" : "CP" 
}


import os
import bpy
import math
import random
from bpy.app.handlers import persistent
from bpy.types import (
    Operator,
    AddonPreferences,
    GizmoGroup,
    Panel,
    UIList,
    PropertyGroup,
)
from bpy.props import (
    StringProperty, #字符串
    IntProperty, #整数
    BoolProperty, #布尔
    FloatVectorProperty,#一个记录两个浮点数的属性
    FloatProperty,#浮点
    EnumProperty,#枚举列表
    )

if bpy.app.version >= (4, 1):
    from bpy.app.translations import pgettext_rpt as rpt_###这个让函数可用字典翻译的，4.1里要打开语言下的影响报告才有用
else:
    from bpy.app.translations import pgettext_tip as rpt_

import textwrap

##插件PowerProps值得参考

# ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #


#todo 在顶部放一个活动物体的所有自定义属性的枚举，然后设置这个名的属性，这样可以为一个物体有多个材质solt都要用不同颜色的属性新建多个自定义属性
class NODE_OT_Add_Prop_Attributenode_285D0(Operator):
    bl_idname = "wm.add_prop_and_attributenode_285d0"
    bl_label = "添加一个属性节点和给所有使用该材质的物体添加自定义属性"
    bl_description = "Add a Custom to all objects with this material\nAdd node"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # # 获取所有选中的物体
        # selected_objects = bpy.context.selected_objects
        # # 遍历选中的物体
        # for obj in selected_objects:


        # 获取场景中所有物体  ？？在blender所有物体里获取，材质能跨场景
        #all_objects = bpy.context.scene.objects
        # 获取Blender中的所有物体
        all_objects = bpy.data.objects
        # 存储具有活动材质的物体
        objects_with_active_material = []
        # 遍历场景中的所有物体
        for obj in all_objects:
            # 检查每个材质槽是否存在且是否包含活动材质    如果是钉住编辑器了，应该是检查材质节点树是当前的编辑材质节点树！！！可以判断钉住编辑器后不显示面板，编辑节点树不等于活动材质节点树
            if any(slot.material == bpy.context.material for slot in obj.material_slots):
                objects_with_active_material.append(obj)

        for obj in objects_with_active_material:
            # 检查物体是否为网格
            #if obj.type == 'MESH':
         #颜色属性
            if "CP Custom colors" not in obj:
                obj["CP Custom colors"]= bpy.context.scene.Matby_N_Colors.edit_selected_objects_colors_C1A81#(1.0, 1.0, 1.0, 1.0)
                obj.data.update()#重要东西用来刷新属性，不然颜色没用
                #obj["CP Custom colors"]=(1.0, 0.0, 0.0)
                #del obj["CP Custom colors"]
            # get or create the UI object for the property
            ui = obj.id_properties_ui("CP Custom colors")
            ui.update(description = "设置活动物体的属性颜色,方便多个物体同材质但不同色")
            ui.update(subtype='COLOR')
            ui.update(default=(1.0, 1.0,1.0,1.0))     
            ui.update(min=0.0, soft_min=0.0)
            ui.update(max=1.0, soft_max=1.0)
         #浮点属性
            if "CP Custom float" not in obj:
                obj["CP Custom float"]= bpy.context.scene.Matby_N_Colors.edit_selected_objects_float_C0000
                obj.data.update()
            ui = obj.id_properties_ui("CP Custom float")
            ui.update(description = "设置活动物体的浮点属性,方便多个物体同材质但不同法线高度等待")
            #ui.update(subtype='COLOR')
            ui.update(default=0.5) 
            ui.update(precision=2)   
            ui.update(min=0.0, soft_min=0.0)
            ui.update(max=1.0, soft_max=1.0)
        
        # 获取当前节点编辑器的节点树
        node_tree = context.space_data.edit_tree#bpy.context.material
        colornode=None
        floatnode=None
        for node in node_tree.nodes:
            node.select = False
            if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Custom colors':
                colornode=node#这行代码能否简化
                context.space_data.edit_tree.nodes.active = node
                node.select = True
                bpy.ops.node.view_selected()
            if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Custom float':
                floatnode=node#这行代码能否简化
                context.space_data.edit_tree.nodes.active = node
                node.select = True
                bpy.ops.node.view_selected()

        nodes = context.space_data.edit_tree.nodes
        if colornode is None:
            prev_context = bpy.context.area.type
            bpy.context.area.type = 'NODE_EDITOR'
            #bpy.ops.node.add_node('INVOKE_DEFAULT', use_transform=True, type='ShaderNodeAttribute')#这个是根据鼠标位置定位 
            colornode: bpy.types.ShaderNodeAttribute = nodes.new(bpy.types.ShaderNodeAttribute.__name__)
            bpy.context.area.type = prev_context

            colornode.name = 'CP Custom colors'
            colornode.label = 'CP Custom colors'
            colornode.attribute_type = 'OBJECT'
            colornode.attribute_name = 'CP Custom colors'
            colornode.width=125
            colornode.use_custom_color=True
            colornode.color=0.75,0.75,0.0

            colornode.outputs[1].hide=True
            colornode.outputs[2].hide=True
            colornode.outputs[3].hide=True
            colornode.show_options=False

            colornode.select = True
            # for node in node_tree.nodes:
            #     if node != colornode:node.select = False  
            nodes.active = colornode
            bpy.ops.node.view_selected()

        if floatnode is None:
            floatnode: bpy.types.ShaderNodeAttribute = nodes.new(bpy.types.ShaderNodeAttribute.__name__)

            floatnode.name = 'CP Custom float'
            floatnode.label = 'CP Custom float'
            floatnode.attribute_type = 'OBJECT'
            floatnode.attribute_name = 'CP Custom float'
            floatnode.width=125
            floatnode.use_custom_color=True
            floatnode.color=0.5,0.5,0.5
            floatnode.location=colornode.location[0],colornode.location[1]-60

            floatnode.outputs[1].hide=True
            floatnode.outputs[0].hide=True
            floatnode.outputs[3].hide=True
            floatnode.show_options=False

            floatnode.select = True
            # for node in node_tree.nodes:
            #     if node != floatnode:node.select = False  
            nodes.active = floatnode
            bpy.ops.node.view_selected()

        
        return {"FINISHED"}

def update_min_max(self, context):
    # 检查每个属性的最小值和最大值，确保最小值不大于最大值
    for prop in ['float', 'r', 'g', 'b']:
        min_val = getattr(self, prop + '_min')
        max_val = getattr(self, prop + '_max')
        if min_val > max_val:
            setattr(self, prop + '_min', max_val)
            setattr(self, prop + '_max', min_val)

#todo 按某个色库里的颜色随机化颜色值
class MNC_OT_randomize_property(Operator):
    bl_idname = 'mnc.randomize_property'
    bl_label = 'Randomize Property'
    bl_description = 'Randomize property on all selected objects\n随机化所有选中对象的属性'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    prop_name: bpy.props.StringProperty(options={'HIDDEN'})
    seed: bpy.props.IntProperty(name='Seed', description='Seed for the random number generator',options={'HIDDEN'})

    # float_min: bpy.props.FloatProperty(name='Min',default=0.0,min=0.0, max=1.0, step=5, precision=2,)
    # float_max: bpy.props.FloatProperty(name='Max',default=1.0,min=0.0, max=1.0, step=5, precision=2,)

    # r_min: bpy.props.FloatProperty(name='Min',default=0.0,min=0.0, max=1.0, step=5, precision=2,)
    # r_max: bpy.props.FloatProperty(name='Max',default=1.0,min=0.0, max=1.0, step=5, precision=2,)

    # g_min: bpy.props.FloatProperty(name='Min',default=0.0,min=0.0, max=1.0, step=5, precision=2,)
    # g_max: bpy.props.FloatProperty(name='Max',default=1.0,min=0.0, max=1.0, step=5, precision=2,)

    # b_min: bpy.props.FloatProperty(name='Min',default=0.0,min=0.0, max=1.0, step=5, precision=2,)
    # b_max: bpy.props.FloatProperty(name='Max',default=1.0,min=0.0, max=1.0, step=5, precision=2,)

    float_min: bpy.props.FloatProperty(
        name='Min',
        default=0.0,     
        step=5,
        precision=2,
        update=update_min_max
    )

    float_max: bpy.props.FloatProperty(
        name='Max',
        default=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )

    r_min: bpy.props.FloatProperty(
        name='Min',
        default=0.0,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )

    r_max: bpy.props.FloatProperty(
        name='Max',
        default=1.0,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )

    g_min: bpy.props.FloatProperty(
        name='Min',
        default=0.0,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )

    g_max: bpy.props.FloatProperty(
        name='Max',
        default=1.0,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )

    b_min: bpy.props.FloatProperty(
        name='Min',
        default=0.0,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )

    b_max: bpy.props.FloatProperty(
        name='Max',
        default=1.0,
        min=0.0,
        max=1.0,
        step=5,
        precision=2,
        update=update_min_max
    )



    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        if self.prop_name == "CP Custom colors":
            # col=layout.column(align=True)
            # rrow = col.row(align=True)
            # rrow.label(text='', icon="EVENT_R")
            # rrow.prop(self,"r_min",text='Min')
            # rrow.prop(self,"r_max",text='Max')

            # grow = col.row(align=True)
            # grow.label(text='', icon="EVENT_G")
            # grow.prop(self,"g_min",text='')
            # grow.prop(self,"g_max",text='')

            # brow = col.row(align=True)
            # brow.label(text='', icon="EVENT_B")
            # brow.prop(self,"b_min",text='')
            # brow.prop(self,"b_max",text='')

            col_0A252 = layout.column(heading='', align=True)
            col_0A252.alignment = 'Expand'.upper()
            grid_19F27 = col_0A252.grid_flow(columns=3, row_major=False, even_columns=False, even_rows=False, align=True)

            grid_19F27.label(text='', icon_value=906)#R
            grid_19F27.label(text='', icon_value=895)#G
            grid_19F27.label(text='', icon_value=890)#B
            row_3AD8E = col_0A252.row(heading='', align=True)
           
            row_3AD8E.alignment = 'Expand'.upper()

            row_3AD8E.prop(self, 'r_min', text='Min', icon_value=0, emboss=True)
            row_3AD8E.prop(self, 'g_min', text='', icon_value=0, emboss=True)
            row_3AD8E.prop(self, 'b_min', text='', icon_value=0, emboss=True)
            
            row_84EA7 = col_0A252.row(heading='', align=True)      
            row_84EA7.alignment = 'Expand'.upper()
            row_84EA7.prop(self, 'r_max', text='Max', icon_value=0, emboss=True)
            row_84EA7.prop(self, 'g_max', text='', icon_value=0, emboss=True)
            row_84EA7.prop(self, 'b_max', text='', icon_value=0, emboss=True)

         
        elif self.prop_name == "CP Custom float":
            col=layout.column(align=True)
            rrow = col.row(align=True)
            #rrow.label(text='',)
            rrow.prop(self,"float_min",text='Min')
            rrow.prop(self,"float_max",text='Max')

    def execute(self, context):
        objects = context.selected_objects
        #random.seed(self.seed)
        self.seed = random.randint(-10000, 10000)
        rand = random.Random(self.seed)

        for obj in objects:
            if self.prop_name in obj:
                #prop = getattr(obj, self.prop_name)
                # min_val = prop.get_min_value()
                # max_val = prop.get_max_value()
                min_val, max_val = 0.0, 1.0
                if self.prop_name == "CP Custom colors":
                    # 随机化RGBA颜色 
                    r = round(rand.uniform(self.r_min, self.r_max), 2)       
                    g = round(rand.uniform(self.g_min, self.g_max), 2)
                    b = round(rand.uniform(self.b_min, self.b_max), 2)
                    a = 1.0  # 设为固定值，若需要随机化可以解除注释
                    #print(r, g, b, a)
                    obj[self.prop_name]=(r, g, b, a)
                    obj.data.update()

                elif self.prop_name == "CP Custom float":
                    f = round(rand.uniform(self.float_min, self.float_max), 2)
                    #print(f)
                    obj[self.prop_name]= f
                    obj.data.update()

        return {'FINISHED'}

# class SNA_OT_Operator001_D53F7(Operator):
    #     bl_idname = "sna.operator001_d53f7"
    #     bl_label = "Refresh color"
    #     bl_description = "The material color is not updated until it is refreshed\n刷新后才会更新材质颜色"
    #     bl_options = {"REGISTER", "UNDO"}

    #     def execute(self, context):
    #         bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')#设置几何中心到原点
    #         #bpy.ops.ed.undo('INVOKE_DEFAULT', )
    #         #bpy.ops.ed.redo('INVOKE_DEFAULT', )
    #         # for area in context.screen.areas:
    #         #     area.tag_redraw()
    #         return {"FINISHED"}

def are_colors_almost_equal(color1, color2, threshold=0.001):
    """检查两个颜色是否在给定的阈值内几乎相等。"""
    for c1, c2 in zip(color1, color2):
        # 使用 math.isclose 函数比较两个颜色分量是否几乎相等
        if math.isclose(c1, c2, rel_tol=threshold):
            continue
        else:
            return False
    return True

class SNA_OT_SelectObjectsWithSameAttribute(Operator):
    bl_idname = "sna.select_same_attribute"
    bl_label = "Select Objects with Same Attribute"
    bl_description = "Select Objects with Same Attribute \n选择与活动对象属性颜色一样的物体"
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

class SNA_PT_MATERIAL_BY_NCOLORS_85AF2(Panel):
    bl_label = 'Material by N-Colors'
    bl_idname = 'SNA_PT_MATERIAL_BY_NCOLORS_85AF2'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):###参考bl官方代码space_node.py的class NODE_HT_header(Header):
        #data=context.space_data
        snode = context.space_data
        if snode.tree_type == 'ShaderNodeTree':
        # # 检查是否存在节点树以及其他必要条件
        # if data and data.tree_type == "ShaderNodeTree" and data.edit_tree:
        #     # 检查当前节点树是否不同于世界节点树
        #     if data.node_tree and data.node_tree != world.node_tree:
            return True
        return False
        #len(bpy.context.selected_objects) > 0 and

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.active_object

        if obj and obj.active_material and obj.active_material==bpy.context.material:
            op = layout.operator('object.select_linked', text=f'Select Objs use [{bpy.context.material.name}]', icon_value=256, emboss=True, depress=False)
            op.type = 'MATERIAL'

        if obj and ("CP Custom colors" in obj or "CP Custom float" in obj):
            box_9C21B = layout.box()
            co=box_9C21B.column(align=True, heading='', heading_ctxt='', translate=True)
            co.label(text='设置与活动物体属性值相等的物体属性', icon_value=551)
            row_3835D = co.row(heading='', align=False)
            row_3835D.prop(bpy.context.scene.Matby_N_Colors, 'edit_same_color_as_active_object_B2B90', text='', icon_value=0, emboss=True)
            #row_3835D.label(text='选择和活动物体一样材质，并且属性的颜色一样的物体', icon_value=256)
            row_3835D.operator('sna.select_same_attribute', text='', icon_value=256, emboss=True, depress=False)

            co.prop(bpy.context.scene.Matby_N_Colors, 'edit_same_float_as_active_object__C0000', text='Float', icon_value=0, emboss=True)

            box_CCCCC = layout.box()
            col=box_CCCCC.column(align=True, heading='', heading_ctxt='', translate=True)
            col.label(text='设置所有选中物体(活动物体)属性', icon="STICKY_UVS_LOC")
            row_D = col.row(heading='', align=False)
            row_D.prop(bpy.context.scene.Matby_N_Colors, 'edit_selected_objects_colors_C1A81', text='', icon_value=0, emboss=True)
            op=row_D.operator('mnc.randomize_property', text='', icon="MOD_NOISE", emboss=True, depress=False)
            op.prop_name="CP Custom colors"

            row_E = col.row(heading='', align=False)
            row_E.prop(bpy.context.scene.Matby_N_Colors, 'edit_selected_objects_float_C0000', text='Float', icon_value=0, emboss=True)
            op=row_E.operator('mnc.randomize_property', text='', icon="MOD_NOISE", emboss=True, depress=False)
            op.prop_name="CP Custom float"

        row = layout.row(heading='', align=True)
        row.scale_y = 1.0
        icon="ADD"
        all_objects = bpy.data.objects
        objects_with_active_material = []
        for obj in all_objects:
            if any(slot.material == bpy.context.material for slot in obj.material_slots):##bpy.context.material
                objects_with_active_material.append(obj)
        tex='Add/Select Node'
        for obj in objects_with_active_material:
            if "CP Custom colors" not in obj or 'CP Custom float' not in obj :
                row.alert = True
                icon="FILE_REFRESH"
                row.scale_y = 2.0
                tex='Add prop to objs using this material'#给使用该材质的物体添加属性
                break  # 只要有一个满足条件就停止循环

        row.operator('wm.add_prop_and_attributenode_285d0', text=tex, icon=icon, emboss=True, depress=False)
        #row.operator('wm.add_prop_and_node_to_scene', text='sence porp', icon="MOD_NOISE", emboss=True, depress=False)
 
##############       
def get_active_object_color(self):
    active_object = bpy.context.active_object
    if active_object:
        attribute_name = "CP Custom colors"
        attribute_value = active_object.get(attribute_name)
        if attribute_value:
            return attribute_value
    return (1.0, 1.0, 1.0, 1.0)  # 默认值
#def update_edit_selected_objects_colors_C1A81(self, context):
    # new_color = self.edit_selected_objects_colors_C1A81
    # # 获取所有选中的物体
    # selected_objects = bpy.context.selected_objects
    # # 遍历选中的物体
    # for obj in selected_objects:
    #     # 检查物体是否为网格
    #     #if obj.type == 'MESH':
    #         #        if "CP Custom colors" not in obj:
    #         #            obj["CP Custom colors"]=(1.0, 1.0,1.0,1.0)
    #         #            # get or create the UI object for the property
    #         #            ui = obj.id_properties_ui("CP Custom colors")
    #         #            ui.update(description = "自定义颜色,方便多个物体同材质但不同色")
    #         #            ui.update(subtype='COLOR')
    #         #            ui.update(default=(1.0, 1.0,1.0,1.0))     
    #         #            ui.update(min=0.0, soft_min=0.0)
    #         #            ui.update(max=1.0, soft_max=1.0)
    # #        else:
    #     obj["CP Custom colors"]=new_color
    #     obj.data.update()#重要东西用来刷新属性，不然颜色没用
def set_edit_selected_objects_colors_C1A81(self, value):
    selected_objects = bpy.context.selected_objects
    attribute_name = "CP Custom colors"
    for obj in selected_objects:
        if attribute_name in obj:
            obj["CP Custom colors"]=value
            obj.data.update()#重要东西用来刷新属性，不然颜色没用

##############
# @persistent
# def get_edit_same_color_as_active_object_B2B90(scene, depsgraph):#
    #     active_object = bpy.context.active_object#bpy.context.object
    #     if active_object:
    #         attribute_name = "CP Custom colors"
    #         attribute_value = active_object.get(attribute_name)
    #         if attribute_value:
    #             bpy.types.scene.edit_same_color_as_active_object_B2B90 = attribute_value
def get_edit_same_color_as_active_object_B2B90(self):
    active_object = bpy.context.active_object
    if active_object:
        attribute_name = "CP Custom colors"
        attribute_value = active_object.get(attribute_name)
        if attribute_value:
            return attribute_value
    return (1.0, 1.0, 1.0, 1.0)  # 默认值
#def are_colors_almost_float(color1, color2):
    # """检查两个颜色是否几乎相等，只精确到小数点后两位。"""
    # # 将颜色的每个分量转换为小数点后两位
    # color1_rounded = [round(c, 1) for c in color1]
    # color2_rounded = [round(c, 1) for c in color2]

    # # 检查每个分量是否相等
    # for c1, c2 in zip(color1_rounded, color2_rounded):
    #     if c1 != c2:
    #         return False
    # return True
# def update_active_color(self, context):
    #     new_color = self.edit_same_color_as_active_object_B2B90
    #     active_object = context.object
    #     attribute_name = "CP Custom colors"
    #     attribute_value = active_object.get(attribute_name)
    #     # print(f"11Attribute value:{active_object.name}")
    #     # print("11Attribute value:", list(attribute_value))
    #     # 遍历场景中的所有物体
    #     for obj in bpy.context.scene.objects:
    #         if obj != active_object:##重要逻辑，要先修改非活动物体的属性，最后再修改活动物体的颜色，不然先修改活动颜色，下面的判断就要以新的活动颜色判断，自然无效
    #             # 检查物体是否具有指定的属性并且属性值与活动物体的属性值几乎相同
    #             if attribute_name in obj and are_colors_almost_equal(obj.get(attribute_name), attribute_value):
    #                 # print(f"22Attribute value:{obj.name}")
    #                 # print("22Attribute value:", list(obj.get(attribute_name)))
    #                 obj["CP Custom colors"]=new_color
    #                 obj.data.update()#重要东西用来刷新属性，不然颜色没用

    #     active_object["CP Custom colors"]=new_color#最后再修改活动物体的颜色
    #     active_object.data.update()
def set_edit_same_color_as_active_object_B2B90(self, value):
    new_color = value
    active_object = bpy.context.active_object
    if active_object:
        attribute_name = "CP Custom colors"
        attribute_value = active_object.get(attribute_name)
        
        for obj in bpy.data.objects:
            if obj != active_object:
                if attribute_name in obj and are_colors_almost_equal(obj.get(attribute_name), attribute_value):
                    obj["CP Custom colors"] = new_color
                    obj.data.update()#重要东西用来刷新属性，不然颜色没用

        active_object["CP Custom colors"] = new_color
        active_object.data.update()#重要东西用来刷新属性，不然颜色没用

##############       
def get_active_object_float(self):
    active_object = bpy.context.active_object
    if active_object:
        attribute_name = "CP Custom float"
        attribute_value = active_object.get(attribute_name)
        if attribute_value:
            return attribute_value
    return (0.5)  # 默认值

def set_edit_selected_objects_float_C0000(self, value):
    selected_objects = bpy.context.selected_objects
    attribute_name = "CP Custom float"
    for obj in selected_objects:
        if attribute_name in obj:
            obj["CP Custom float"]=value
            obj.data.update()#重要东西用来刷新属性，不然颜色没用

##############       
def set_edit_same_float_as_active_object__C0000(self, value):
    new_color = value
    active_object = bpy.context.active_object
    if active_object:
        attribute_name = "CP Custom float"
        attribute_value = active_object.get(attribute_name) 
        for obj in bpy.data.objects:
            if obj != active_object:
                if attribute_name in obj and obj.get(attribute_name)==attribute_value:
                    obj["CP Custom float"] = new_color
                    obj.data.update()#重要东西用来刷新属性，不然颜色没用

        active_object["CP Custom float"] = new_color
        active_object.data.update()#重要东西用来刷新属性，不然颜色没用

# 所有场景属性汇总---------------------------------------------------- #
class Materialby_N_Colors_props(PropertyGroup):
    edit_selected_objects_colors_C1A81 :FloatVectorProperty(
        name='Sets the property color of all selected objects', description='设置所有选中物体(活动物体)的属性颜色', 
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 
        get=get_active_object_color,
        set=set_edit_selected_objects_colors_C1A81,
        #update=update_edit_selected_objects_colors_C1A81
        )

    edit_same_color_as_active_object_B2B90 :FloatVectorProperty(
        name='Also adjust the attribute color of the same attribute color as the active object',
        description='调整与活动物体同色的物体属性颜色',
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=5, precision=2, 
        get=get_active_object_color,
        set=set_edit_same_color_as_active_object_B2B90,
        #update=update_active_color,
    )

    edit_selected_objects_float_C0000 :FloatProperty(
        name="Float",description="Edit selected objects float",default=0.5, step=5, precision=2,  #min=0.0, max=1.0,
        get=get_active_object_float,
        set=set_edit_selected_objects_float_C0000,
        )
    
    edit_same_float_as_active_object__C0000 :FloatProperty(
        name="Float",description="Edit same float as active object",default=0.5,step=3, precision=2, #min=0.0, max=1.0,
        get=get_active_object_float,
        set=set_edit_same_float_as_active_object__C0000,
        )


# ----------------------------------------------------根据场景不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据场景不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据场景不同自动切换属性值---------------------------------------------------- #
fontsize = 4 #這個實際影響段落寬度
def update_font_size():
    global fontsize
    prefs = bpy.context.preferences
    ui_scale = prefs.view.ui_scale
    points = prefs.ui_styles[0].widget_label.points
    fontsize = math.ceil(ui_scale * points)

class SNA_PT_MATERIAL_BY_NScene_85AF2(Panel):
    bl_label = 'Material by N-Scene'
    bl_idname = 'SNA_PT_MATERIAL_BY_NScene_85AF2'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 1
    bl_parent_id = 'SNA_PT_MATERIAL_BY_NCOLORS_85AF2'

    @classmethod
    def poll(cls, context):###参考bl官方代码space_node.py的class NODE_HT_header(Header):
        scenes = bpy.data.scenes
        if len(scenes) > 1:
            return True
        return False

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row(heading='', align=False)
        row.scale_y = 1.5
        row.operator('wm.add_prop_and_node_to_scene', text='场景属性/刷新属性', icon="SCENE_DATA", emboss=True, depress=False)

        if len(scene_prop_nodes)>1:
            box_CCCCC = layout.box()
            
            
            width = context.region.width#- 45- 20 #N面板的宽度
            ui_scale = bpy.context.preferences.view.ui_scale
            fontCount = math.floor(width / (fontsize*ui_scale* 1.5)) # 调整为中文字符宽度 这样中文才会自动换行##fontCount = floor(width / (fontsize))#+ 10#fontsize = 12
            textTowrap = rpt_("Blender里有多个Scene Prop Group属性的节点树,它们都会被自动修改,把不用自动刷新的节点树属性改为默认." )
            wrapp = textwrap.TextWrapper(width=fontCount) #50 = maximum length       
            wList = wrapp.wrap(text=textTowrap)#对textTowrap中的单独段落自动换行以使每行长度最多为 width 个字符

            for i, text in enumerate(wList):
                icon = 'ERROR'
                if i > 0:  # 如果是第二行
                    text = "    " + text  # 在文本开头添加一个空格
                    icon = 'BLANK1'
                box_CCCCC.row()  # 创建一个行，用作空行的占位符
                c = box_CCCCC.column(align=True)
                c.alert = True
                c.alignment = 'LEFT'
                c.scale_y = 0.5
                c.label(text=text, icon=icon)


            col=box_CCCCC.column(align=True)
            #col.label(text='Blender里有多个Scene Prop Group属性的节点树！', icon="ERROR") 
            #col.label(text='它们都会被自动修改,把不用自动刷新的节点树属性改为默认', icon="ERROR")
            #row_3835D = col.row(heading='', align=False)
            for tree in scene_prop_nodes:
                #s = col.split(factor=0.75, align=True)
                col.label(text=tree.name, icon="NODETREE")
                col.prop(tree, 'Matby_N_Colors_type', text='', icon_value=0, emboss=True)

scene_prop_nodes=[]

class NODE_OT_Add_Prop_Node_To_Scene(Operator):
    bl_idname = "wm.add_prop_and_node_to_scene"
    bl_label = "Add customs to all scenes\nAdd node"
    bl_description = "自动给所有场景添加属性\n给节点树添加节点\n添加场景后刷新属性"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        #重新导入一个新的节点组，先清除bl里Matby_N_Colors_type=='Scene Prop'的属性，然后导入一个新的，可用按住shift操作

        #先检测bl里有几个Matby_N_Colors_type=='Scene Prop'的节点树，如果有多个就显示再N面板然后把这两个节点的属性显示在N面板里
        global scene_prop_nodes
        scene_prop_nodes.clear()
        for node_group in bpy.data.node_groups:
            if node_group.Matby_N_Colors_type=='Scene Prop':
                scene_prop_nodes.append(node_group)
        if len(scene_prop_nodes)>1:
            self.report({'ERROR'}, "Blender里只能有一个Scene Prop Group属性的节点树！")
            return {"FINISHED"}

        scenes = bpy.data.scenes
        if len(scenes) == 1:
            self.report({'ERROR'}, "Just one scene.")
            return {"FINISHED"}
        
        i = 0
        length = len(scenes)
        for scene in scenes:
            #self.report({'ERROR'}, f"{scene.name}")
            i += 1
            
            if "CP Scene Material" in scene:
                del scene["CP Scene Material"]
                # 可选：更新当前视图层
                #bpy.context.view_layer.update()


            # 检查属性是否存在，不存在则创建
            #if "CP Scene Material" not in scene:
            scene["CP Scene Material"] = i
            #scene['data'].update()
            #scene.update()没用了
            

            bpy.context.view_layer.update()
            # else:
            #     scene["CP Sence Material"] = i#已有就更新顺序，不对会重复添加属性
            # 获取或创建属性
            ui = scene.id_properties_ui("CP Scene Material")
            # 更新属性
            ui.update(description=f"Scene Material: {i},don`t change!")
            #ui.update(subtype='INT')
            # 报错'INT' not found in ('NONE', 'FILE_PATH', 'DIR_PATH', 'FILE_NAME', 'BYTE_STRING', 'PASSWORD', 'PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'TIME_ABSOLUTE', 'DISTANCE', 'DISTANCE_CAMERA', 'POWER', 'TEMPERATURE', 'WAVELENGTH', 'COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'XYZ_LENGTH', 'COLOR_GAMMA', 'COORDINATES', 'LAYER', 'LAYER_MEMBER')
            ui.update(default=i)
            ui.update(min=i)#min=1
            ui.update(max=i)#max=length
        
        #暂时用这个更新属性效果 重新启用所有材质的节点树
        for mat in bpy.data.materials:
            mat.use_nodes=False
            mat.use_nodes=True
        
        # 当前编辑的节点树里添加主节点组
        node_tree = context.space_data.edit_tree
        nodes = node_tree.nodes
        mainnode=None
        for node in nodes:
            node.select = False
            if node.bl_idname=='ShaderNodeGroup' and node.node_tree and node.node_tree.Matby_N_Colors_type=='Scene Prop':
                mainnode=node#这行代码能否简化
                context.space_data.edit_tree.nodes.active = node
                node.select = True
                bpy.ops.node.view_selected()

        if mainnode is None:            
            mainnode = nodes.new(type='ShaderNodeGroup')
            mainnode.node_tree = import_node('.CP_Scene_Material',True)
            mainnode.name='CP Scene Material'
            mainnode.show_options=False
            mainnode.select = True
            for node in node_tree.nodes:
                if node != mainnode:node.select = False  
            nodes.active = mainnode
            bpy.ops.node.view_selected()

        # #把这个属性节点直接移动到节点组内部 获取当前节点编辑器的节点树
            # node_tree = context.space_data.edit_tree#bpy.context.material
            # colornode=None
            # for node in node_tree.nodes:
            #     node.select = False
            #     if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Scene Material':
            #         colornode=node#这行代码能否简化
            #         context.space_data.edit_tree.nodes.active = node
            #         node.select = True
            #         bpy.ops.node.view_selected()
            #         node.attribute_type = 'VIEW_LAYER'
            #         node.attribute_name = 'CP Scene Material'

            #         # node.mute = not node.mute
            #         # node.mute = False

                
            # nodes = context.space_data.edit_tree.nodes
            # if colornode is None:
            #     prev_context = bpy.context.area.type
            #     bpy.context.area.type = 'NODE_EDITOR'
            #     #bpy.ops.node.add_node('INVOKE_DEFAULT', use_transform=True, type='ShaderNodeAttribute')#这个是根据鼠标位置定位 
            #     colornode: bpy.types.ShaderNodeAttribute = nodes.new(bpy.types.ShaderNodeAttribute.__name__)
            #     bpy.context.area.type = prev_context

            #     colornode.name = 'CP Scene Material'
            #     colornode.label = 'CP Scene Material'
            #     colornode.attribute_type = 'VIEW_LAYER'
            #     colornode.attribute_name = 'CP Scene Material'
            #     colornode.width=125
            #     #colornode.use_custom_color=True
            #     #colornode.color=0.75,0.75,0.0

            #     colornode.outputs[1].hide=True
            #     colornode.outputs[0].hide=True
            #     colornode.outputs[3].hide=True
            #     colornode.show_options=False

            #     colornode.select = True
            #     for node in node_tree.nodes:
            #         if node != colornode:node.select = False  
            #     nodes.active = colornode
            #     bpy.ops.node.view_selected()

        ##修改节点组的面板序号和名字为对应的场景名
        if bpy.app.version >= (4, 0, 0):
            # 存储所有场景的名字
            scene_names = [scene.name for scene in scenes]

            need_del=False
            need_add=False

            for node_group in bpy.data.node_groups:
                if node_group.Matby_N_Colors_type=='Scene Prop':
                    links=node_group.links
                    ngnodes = node_group.nodes
                    propnode=check_propnode(ngnodes)#检查属性节点
                    panels=0
                    for item in node_group.interface.items_tree[:]:
                        if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.socket_type == 'NodeSocketInt': #修改切换端口的最大值
                            item.min_value = 1
                            item.max_value = len(scene_names)
                            #item.hide_value = True

                        if item.item_type == 'PANEL':##修改面板名
                            panels += 1
                            #item.name=str(panels)
                            if panels <= len(scene_names):#节点里面板数和场景数比较
                                # 更新 item.name 为序号加上对应的场景名字  "-" + str(panels) + "-  " + 
                                item.name = scene_names[(panels - 1) % len(scene_names)]# +  "]"##% len(scene_names): 取模运算，确保索引值在列表范围内,大于范围时从第一个开始
                                #self.report({'ERROR'}, f"{item.name},{item.item_type}")
                                if panels < len(scene_names):
                                    need_add=True
                            else:# panels > len(scene_names):
                                need_del=True
                                item.name = "-----Useless-----"
                    #break

                    #新增面板和节点组
                    if need_add:
                        #找出输入输出节点
                        in_node = next((node for node in node_group.nodes if node.bl_idname == 'NodeGroupInput'), None)
                        out_node = next((node for node in node_group.nodes if node.bl_idname == 'NodeGroupOutput'), None)
                        

                        add_nodes=len(scene_names)-panels
                        start_int=panels
                        for i in range(add_nodes):
                            start_int+=1
                            panel_name= scene_names[start_int-1] #"-" + str(start_int) + "-  " + 
                            #self.report({'ERROR'}, f"{panel_name}")

                            #新建面板
                            new_panel = node_group.interface.new_panel(name=panel_name, description='', default_closed=False)
                            #这里新建的端口名字先和节点组默认一样方便连接到输入节点
                            color_socket = node_group.interface.new_socket(name="B",in_out='INPUT',socket_type = 'NodeSocketColor', parent=new_panel)
                            float_socket = node_group.interface.new_socket(name="B",in_out='INPUT',socket_type = 'NodeSocketFloat', parent=new_panel)
                            vector_socket = node_group.interface.new_socket(name="B",in_out='INPUT',socket_type = 'NodeSocketVector', parent=new_panel)

                            # #找出输出端Start Int没有连接的节点组作为新节点组的输入连接节点
                            last_node=None
                            for node in node_group.nodes:
                                if node.bl_idname == 'ShaderNodeGroup':
                                    for out_socket in node.outputs:
                                        if out_socket.name=="Start Int" and not out_socket.links:
                                            last_node=node
                                            #self.report({'ERROR'}, f"{node.name}")
                                            # 找到符合条件的节点，跳出最外层的循环
                                            break
                                    else:
                                        # 如果在内层循环中没有找到符合条件的输出端口，继续下一个节点
                                        continue
                                    # 找到符合条件的节点并报告了错误，跳出最外层的循环
                                    break


                            #在node_group节点树里新建一个节点组类型的节点，然后指定它的节点树是bpy.data.node_groups里叫.CP_Scene_Material2-&的节点树
                            # 创建新的节点组类型的节点
                            new_node_group = node_group.nodes.new('ShaderNodeGroup')
                            nodename='.CP_Scene_Material2-&'
                            new_node_group.node_tree = import_node(nodename,False)#bpy.data.node_groups[".CP_Scene_Material2-&"]
                            new_node_group.show_options=False

                            connect_nodes(links, propnode, new_node_group)#连接到属性节点，所以每个节点组的切换端口和类型要修改为和属性节点"系数一样"
                            #上面这个连接要在前面，因为属性端口里也有浮点和颜色这两个端口会自动连接，下面的连接会自动替换连接到组输入节点上

                            if last_node and in_node and out_node:
                                new_node_group.location=last_node.location[0]+250,last_node.location[1]#
                                out_node.location=new_node_group.location[0]+250,new_node_group.location[1]#
                                
                                connect_nodes(links, last_node, new_node_group)
                                connect_nodes(links, in_node, new_node_group)
                                connect_nodes(links, new_node_group,out_node)



                            color_socket.name=""
                            float_socket.name=""
                            vector_socket.name=""
                            vector_socket.hide_value = True


           
                    if need_del:
                        #删除多余的面板
                        i=0
                        for item in node_group.interface.items_tree[:]:
                            if item.item_type == 'PANEL':##修改面板名
                                i += 1
                                if i > len(scene_names):
                                    for childitem in node_group.interface.items_tree[:]:
                                        if childitem.item_type == 'SOCKET' and childitem.parent == item:
                                            node_group.interface.remove(childitem)#移除面板里的项目 这个是移除端口，后面一个布尔再移除面板类型端口时将面板下的端口移动到主面板下move_content_to_parent=True
                                    node_group.interface.remove(item)#移除面板

                        #删除节点树里多余的节点组
                        for n in reversed(ngnodes[:]):
                            if n.bl_idname=='ShaderNodeGroup':
                                for input_socket in n.inputs:
                                    if input_socket.name=="B" and not input_socket.links:#用端口是否连接判断是否是多余的节点组
                                        # n.select = True
                                        # ngnodes.active = n#设置活动节点
                                        
                                        # 获取第二个输入端口Start Int连接的节点
                                        second_input_node = None
                                        for link in links:
                                            if link.to_socket == n.inputs["Start Int"]:#Start Int[1]
                                                second_input_node = link.from_node
                                                break
                                        
                                        # 获取第一个输出端口连接的节点
                                        first_output_node = None
                                        for link in links:
                                            if link.from_socket == n.outputs[0]:
                                                first_output_node = link.to_node
                                                break                                
                                        
                                        # 进行连接
                                        if second_input_node and first_output_node:
                                            connect_nodes(links, second_input_node, first_output_node)
                                            first_output_node.location=second_input_node.location[0]+250,second_input_node.location[1]#
                                        # 删除节点
                                        ngnodes.remove(n)

                                        break

        return {"FINISHED"}

def import_node(nodename,bytype=False):
    resultnode=None
    if bytype:##主节点组
        for node_group in bpy.data.node_groups:
            if node_group.Matby_N_Colors_type=='Scene Prop':
                resultnode=node_group
                break
    else:#内部切换的子节点组
        for node_group in bpy.data.node_groups:
            if node_group.name==nodename:
                resultnode=node_group
                break

    if resultnode is None:
        # 设置文件路径和节点组名称
        filepath = os.path.join(os.path.dirname(__file__), 'assets', 'Asset.blend')
        group_name = nodename

        # 导入节点组
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.node_groups = [name for name in data_from.node_groups if name == group_name]

        # 将导入的节点组添加到节点树中
        if data_to.node_groups:
            node_group_name = data_to.node_groups[0].name  # 获取节点组的名称，node_groups[0]就是导入的第一个，如果是-1哪就是最后一个导入的，也就是子节点组
            resultnode = bpy.data.node_groups[node_group_name]

    return resultnode 

#将fromnode的所有输出端和tonode输入端依次连接，连接的判断条件是输出端的名字和类型和输入端的名字和类型都相同才建立连接
def connect_nodes(links, from_node, to_node):   
    for output_socket in from_node.outputs:
        for input_socket in to_node.inputs:
            if output_socket.name == input_socket.name and output_socket.bl_idname == input_socket.bl_idname:
                links.new(output_socket, input_socket)

def check_propnode(nodes):
    colornode=None
    for node in nodes:
        if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Scene Material':
            colornode=node#这行代码能否简化
            node.attribute_type = 'VIEW_LAYER'
            node.attribute_name = 'CP Scene Material'

    if colornode is None:
        colornode: bpy.types.ShaderNodeAttribute = nodes.new(bpy.types.ShaderNodeAttribute.__name__)
        colornode.name = 'CP Scene Material'
        colornode.label = 'CP Scene Material'
        colornode.attribute_type = 'VIEW_LAYER'
        colornode.attribute_name = 'CP Scene Material'
        colornode.width=125
        
        colornode.outputs[1].hide=True
        colornode.outputs[0].hide=True
        colornode.outputs[3].hide=True
        #colornode.show_options=False
    return colornode


# ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #


classes = (
    NODE_OT_Add_Prop_Attributenode_285D0,
    MNC_OT_randomize_property,
    #SNA_OT_Operator001_D53F7,
    SNA_OT_SelectObjectsWithSameAttribute,
    SNA_PT_MATERIAL_BY_NCOLORS_85AF2,

    Materialby_N_Colors_props,##所有场景属性汇总

    NODE_OT_Add_Prop_Node_To_Scene,
    SNA_PT_MATERIAL_BY_NScene_85AF2,
    
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    ##注意这个要在所有class注册后，也就是它的type注册后再注册这个 所有场景属性汇总
    bpy.types.Scene.Matby_N_Colors = bpy.props.PointerProperty(name = "HDRLight main prop",type=Materialby_N_Colors_props)

    bpy.types.NodeTree.Matby_N_Colors_type = EnumProperty( #先留着备用,这个属性可以在模板bl文件里直接先给到节点树
        items=[
            ('Default', 'Default', ''),
            ('Scene Prop', 'Scene Prop Group', ''),
            ('View_layer Prop', 'View_layer Group', ''),
            
        ],
        name="Matby_N_Colors NodeTree Type",
        description="Do not modify this property manually, it is automatically generated",
        default="Default",
        )

        # bpy.types.Scene.edit_selected_objects_colors_C1A81 = bpy.props.FloatVectorProperty(
        #     name='Sets the property color of all selected objects', description='设置所有选中物体(活动物体)的属性颜色', 
        #     size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 
        #     get=get_active_object_color,
        #     set=set_edit_selected_objects_colors_C1A81,
        #     #update=update_edit_selected_objects_colors_C1A81
        #     )

        # bpy.types.Scene.edit_same_color_as_active_object_B2B90 = bpy.props.FloatVectorProperty(
        #     name='Also adjust the attribute color of the same attribute color as the active object',
        #     description='调整与活动物体同色的物体属性颜色',
        #     size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=5, precision=2, 
        #     get=get_active_object_color,
        #     set=set_edit_same_color_as_active_object_B2B90,
        #     #update=update_active_color,
        # )

        # bpy.types.Scene.edit_selected_objects_float_C0000 = bpy.props.FloatProperty(
        #     name="Float",description="Edit selected objects float",default=0.5,min=0.0, max=1.0, step=5, precision=2,
        #     get=get_active_object_float,
        #     set=set_edit_selected_objects_float_C0000,
        #     )
        
        # bpy.types.Scene.edit_same_float_as_active_object__C0000 = bpy.props.FloatProperty(
        #     name="Float",description="Edit same float as active object",default=0.5,min=0.0, max=1.0, step=3, precision=2,
        #     get=get_active_object_float,
        #     set=set_edit_same_float_as_active_object__C0000,
        #     )

        # #bpy.app.handlers.depsgraph_update_post.append(get_edit_same_color_as_active_object_B2B90)#多余了用get了

        # #bpy.types.Scene.shoud_refresh_color = bpy.props.BoolProperty(name = "", description = "", default = False)


def unregister():
    for cls in reversed(classes):#自定义工具图标
        bpy.utils.unregister_class(cls)#先注销这个

    del bpy.types.Scene.Matby_N_Colors
    del bpy.types.NodeTree.Matby_N_Colors_type

        # del bpy.types.Scene.edit_selected_objects_colors_C1A81
        # del bpy.types.Scene.edit_same_color_as_active_object_B2B90
        # del bpy.types.Scene.edit_selected_objects_float_C0000
        # del bpy.types.Scene.edit_same_float_as_active_object__C0000
        # #bpy.app.handlers.depsgraph_update_post.remove(get_edit_same_color_as_active_object_B2B90)

        # #del bpy.types.Scene.shoud_refresh_color
    
if __name__ == "__main__":
    register()