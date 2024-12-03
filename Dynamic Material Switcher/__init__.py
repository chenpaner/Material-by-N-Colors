

bl_info = {
    "name" : "Dynamic Material Switcher只支持4.0及以上，节点组面板的问题",##instance material实例材质   Dynamic Material Switcher动态材质切换器 Material by N-Colors
    "author" : "CP-Design", 
    "description" : "Control materials by adding properties to objects/view layers,enabling the same material to automatically switch to different effects based on the object or view layer(scene).",
    "blender" : (4, 0, 0),
    "version" : (1, 0, 0),
    "location" : "Node Editor's N panel > Tool > Dynamic Material Switcher",
    "warning" : "This plugin is for Blender version 4.0.0 or above!",
    "doc_url": "https://blendermarket.com/creators/cp-design", 
    "tracker_url": "", 
    "category" : "CP" 
}

import os
import bpy
import sys
import math
from datetime import datetime
from pathlib import Path
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

from bpy.app.translations import pgettext_iface as iface_

import textwrap

##插件PowerProps值得参考

# ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #


#todo 在顶部放一个活动物体的所有自定义属性的枚举，然后设置这个名的属性，这样可以为一个物体有多个材质solt都要用不同颜色的属性新建多个自定义属性
class NODE_OT_Add_Prop_Attributenode_285D0(Operator):
    bl_idname = "wm.add_prop_and_attributenode_285d0"
    bl_label = ""
    bl_description = "Add property to all objects with this material\nAdd node"
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
                obj["CP Custom colors"]= bpy.context.scene.CPBR_Main_Props.edit_selected_objects_colors_C1A81#(1.0, 1.0, 1.0, 1.0)
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
                obj["CP Custom float"]= bpy.context.scene.CPBR_Main_Props.edit_selected_objects_float_C0000
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
    bl_description = 'Randomize property on all selected objects'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    prop_name: bpy.props.StringProperty(options={'HIDDEN'})
    seed: bpy.props.IntProperty(name='Seed', description='Seed for the random number generator',options={'HIDDEN'})

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
    bl_label = ""
    bl_description = "Select Objects with Same Attribute"
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
                try:
                    obj.select_set(True)
                except:
                    pass

        return {'FINISHED'}

class SNA_PT_MATERIAL_BY_NCOLORS_85AF2(Panel):
    bl_label = 'Dynamic Material Switcher'
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
        if snode.tree_type == 'ShaderNodeTree' and context.space_data.edit_tree:#要当前时节点编辑器还要有树
        # # 检查是否存在节点树以及其他必要条件
        # if data and data.tree_type == "ShaderNodeTree" and data.edit_tree:
        #     # 检查当前节点树是否不同于世界节点树
        #     if data.node_tree and data.node_tree != world.node_tree:
            return snode.shader_type == 'OBJECT'
        return False
        #len(bpy.context.selected_objects) > 0 and

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        # if context.space_data.shader_type == 'WORLD':# 'OBJECT'
        #     return

        layout = self.layout
        obj = bpy.context.view_layer.objects.active

        panel=True
        # if context.space_data.shader_type == 'OBJECT':
        if bpy.app.version >= (4, 1):
            header, panel = layout.panel("my_panel_a", default_closed=False)#bl4.1
            header.label(text="Material by N-Objects",icon="MESH_MONKEY")
        else:
            r = layout.row(heading='', align=False)
            r.alignment = 'CENTER'.upper()
            r.label(text="Material by N-Objects")
        if panel:
            layout = layout.box()
            if obj and obj.active_material and obj.active_material==bpy.context.material:
                tex=iface_("Select all use [%s] objs") % (bpy.context.material.name)
                op = layout.operator('object.select_linked', text=tex, icon_value=256, emboss=True, depress=False)
                op.type = 'MATERIAL'

            if obj and ("CP Custom colors" in obj or "CP Custom float" in obj):
                box_CCCCC = layout.box()
                col=box_CCCCC.column(align=True, heading='', heading_ctxt='', translate=True)
                col.label(text='Edit selected obj\'s prop', icon="STICKY_UVS_LOC")
                row_D = col.row(heading='', align=False)
                row_D.prop(bpy.context.scene.CPBR_Main_Props, 'edit_selected_objects_colors_C1A81', text='', icon_value=0, emboss=True)
                op=row_D.operator('mnc.randomize_property', text='', icon="MOD_NOISE", emboss=True, depress=False)
                op.prop_name="CP Custom colors"

                row_E = col.row(heading='', align=False)
                row_E.prop(bpy.context.scene.CPBR_Main_Props, 'edit_selected_objects_float_C0000', text='Float', icon_value=0, emboss=True)
                op=row_E.operator('mnc.randomize_property', text='', icon="MOD_NOISE", emboss=True, depress=False)
                op.prop_name="CP Custom float"


                box_9C21B = layout.box()
                co=box_9C21B.column(align=True, heading='', heading_ctxt='', translate=True)
                co.label(text='Edit prop for objs matching active obj\'s prop value', icon_value=551)
                row_3835D = co.row(heading='', align=False)
                row_3835D.prop(bpy.context.scene.CPBR_Main_Props, 'edit_same_color_as_active_object_B2B90', text='', icon_value=0, emboss=True)
                #row_3835D.label(text='选择和活动物体一样材质，并且属性的颜色一样的物体', icon_value=256)
                row_3835D.operator('sna.select_same_attribute', text='', icon_value=256, emboss=True, depress=False)

                co.prop(bpy.context.scene.CPBR_Main_Props, 'edit_same_float_as_active_object__C0000', text='Float', icon_value=0, emboss=True)


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

            row.operator('wm.add_prop_and_attributenode_285d0', text=iface_(tex), icon=icon, emboss=True, depress=False)


        scenes = bpy.data.scenes
        viewlayers = context.scene.view_layers
        if len(viewlayers) == 1 and len(scenes) == 1:
            return

        layout = self.layout

        pan=True
        if bpy.app.version >= (4, 1):
            header, pan = layout.panel("my_panel_b", default_closed=False)#bl4.1
            header.label(text="Material by N-Viewlayer(Scene)",icon="RENDER_RESULT")
        else:
            r = layout.row(heading='', align=False)
            r.alignment = 'CENTER'.upper()
            r.label(text="Material by N-Viewlayer(Scene)")
        if pan:
            box = layout.box()
            row = box.row(heading='', align=False)
            row.scale_y = 1.5
            t='Add node/Refresh node/Add property to viewlayer'
            # 判断场景数视图层数是否和节点组的面板数量一样，不一样就警告提示要刷新

            # 使用列表推导式和 sum 函数计算视图层总数
            vl_count = sum(len(scene.view_layers) for scene in bpy.data.scenes)
            nodes = context.space_data.edit_tree.nodes
            node_group = next((node for node in nodes if node.bl_idname == 'ShaderNodeGroup' and node.node_tree and node.node_tree.Matby_N_Colors_type == 'Viewlayer Prop'), None)
            # node_group = next((ng for ng in bpy.data.node_groups if ng.Matby_N_Colors_type == 'Viewlayer Prop'), None)#这个是在bl所有节点树里查找
            if node_group:
                panels = sum(1 for item in node_group.node_tree.interface.items_tree if item.item_type == 'PANEL')
                if panels != vl_count:
                    row.alert = True
                    t='Refresh node'
            row.operator('wm.add_prop_and_node_to_viewlayer', text=t, icon="RENDER_RESULT", emboss=True, depress=False)

            return
            # if len(viewlayer_prop_nodes)>1:
                # box_CCCCC = layout.box()

                # width = context.region.width#- 45- 20 #N面板的宽度
                # ui_scale = bpy.context.preferences.view.ui_scale
                # fontCount = math.floor(width / (fontsize*ui_scale* 1.5)) # 调整为中文字符宽度 这样中文才会自动换行##fontCount = floor(width / (fontsize))#+ 10#fontsize = 12
                # textTowrap = iface_("There are multiple nodetrees with \"Viewlayer Group\" properties.they will all be automatically refreshed. Change properties of nodetrees that do not need automatic refreshing to \"Default\"" )
                # wrapp = textwrap.TextWrapper(width=fontCount) #50 = maximum length       
                # wList = wrapp.wrap(text=textTowrap)#对textTowrap中的单独段落自动换行以使每行长度最多为 width 个字符

                # for i, text in enumerate(wList):
                #     icon = 'ERROR'
                #     if i > 0:  # 如果是第二行
                #         text = "    " + text  # 在文本开头添加一个空格
                #         icon = 'BLANK1'
                #     box_CCCCC.row()  # 创建一个行，用作空行的占位符
                #     c = box_CCCCC.column(align=True)
                #     c.alert = True
                #     c.alignment = 'LEFT'
                #     c.scale_y = 0.5
                #     c.label(text=text, icon=icon)


                # col=box_CCCCC.column(align=True)
                # #col.label(text='Blender里有多个Scene Prop Group属性的节点树！', icon="ERROR") 
                # #col.label(text='它们都会被自动修改,把不用自动刷新的节点树属性改为默认', icon="ERROR")
                # #row_3835D = col.row(heading='', align=False)
                # for tree in viewlayer_prop_nodes:
                #     #s = col.split(factor=0.75, align=True)
                #     col.label(text=tree.name, icon="NODETREE")
                #     col.prop(tree, 'Matby_N_Colors_type', text='', icon_value=0, emboss=True)
 
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
''' 不用通过场景设置了，用更底层的视图层就包括了所有场景
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
            textTowrap = iface_("Blender里有多个Scene Prop Group属性的节点树,它们都会被自动修改,把不用自动刷新的节点树属性改为默认." )
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
'''

# ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #
# ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #
def import_node(nodename,bytype=False):
    resultnode=None
    if bytype:##主节点组
        for node_group in bpy.data.node_groups:
            if node_group.Matby_N_Colors_type=='Viewlayer Prop':
                resultnode=node_group
                break
    else:#寻找内部切换的子节点树是否已经导入
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
        if node.bl_idname == 'ShaderNodeAttribute' and node.attribute_name == 'CP Viewlayers Material':
            colornode=node#这行代码能否简化
            break

    if colornode is None:
        colornode: bpy.types.ShaderNodeAttribute = nodes.new(bpy.types.ShaderNodeAttribute.__name__)
        colornode.name = 'CP Viewlayers Material'
        colornode.label = 'CP Viewlayers Material'
        #这里缺少一个将系数输出端口连接到其它所有节点组的同名输入端的
        
        # colornode.width=125
    colornode.attribute_type = 'VIEW_LAYER'
    colornode.attribute_name = 'CP Viewlayers Material'
    colornode.outputs[1].hide=True
    colornode.outputs[0].hide=True
    colornode.outputs[3].hide=True
    colornode.show_options=False
    return colornode

'''
class SNA_PT_MATERIAL_BY_Nviewlayer_85AF2(Panel):
    bl_label = 'Material by N-Viewlayer(Scene)'
    bl_idname = 'SNA_PT_MATERIAL_BY_Nviewlayer_85AF2'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_order = 2
    bl_parent_id = 'SNA_PT_MATERIAL_BY_NCOLORS_85AF2'

    @classmethod
    def poll(cls, context):###参考bl官方代码space_node.py的class NODE_HT_header(Header):
        scenes = bpy.data.scenes
        viewlayers = context.scene.view_layers
        if len(viewlayers) == 1 and len(scenes) == 1:
            return False
        return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row(heading='', align=False)
        row.scale_y = 1.5
        row.operator('wm.add_prop_and_node_to_viewlayer', text='视图层属性/刷新属性', icon="RENDER_RESULT", emboss=True, depress=False)

        if len(viewlayer_prop_nodes)>1:
            box_CCCCC = layout.box()

            width = context.region.width#- 45- 20 #N面板的宽度
            ui_scale = bpy.context.preferences.view.ui_scale
            fontCount = math.floor(width / (fontsize*ui_scale* 1.5)) # 调整为中文字符宽度 这样中文才会自动换行##fontCount = floor(width / (fontsize))#+ 10#fontsize = 12
            textTowrap = iface_("当前页面里有多个Viewlayer Group属性的节点树,它们都会被自动修改,把不用自动刷新的节点树属性改为默认." )
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
            for tree in viewlayer_prop_nodes:
                #s = col.split(factor=0.75, align=True)
                col.label(text=tree.name, icon="NODETREE")
                col.prop(tree, 'Matby_N_Colors_type', text='', icon_value=0, emboss=True)
'''

# viewlayer_prop_nodes=[]


def makejustone_viewlayer_prop_nodetree():
    newtree = bpy.data.node_groups.get(".CP_ViewLayer_Material")
    if not newtree:
        for node_tree in bpy.data.node_groups:
            if hasattr(node_tree, 'Matby_N_Colors_type') and node_tree.Matby_N_Colors_type == 'Viewlayer Prop':
                node_tree.name = ".CP_ViewLayer_Material"
                break
    if not newtree:
        return  # 如果还是没有找到 .CP_ViewLayer_Material，则不执行后续操作
    # 迭代场景中的所有材质是否有重复属性的节点树
    for material in bpy.data.materials:
        if material.node_tree:
            nodetree=material.node_tree
            for node in nodetree.nodes:
                if node.bl_idname == 'ShaderNodeGroup':
                    if node.node_tree and node.node_tree.Matby_N_Colors_type=='Viewlayer Prop':
                        if node.node_tree.name != ".CP_ViewLayer_Material":
                            
                            node.node_tree=newtree
                        
    #迭代所有blender节点树里自定义节点是否有重复属性的节点树
    for node_tree in bpy.data.node_groups:
        for node in node_tree.nodes:
            if node.bl_idname == 'ShaderNodeGroup':
                if node.node_tree and node.node_tree.Matby_N_Colors_type=='Viewlayer Prop':
                    if node.node_tree.name != ".CP_ViewLayer_Material":
                        node.node_tree=newtree
    ##删除多余属性的节点树
    for node_tree in bpy.data.node_groups:
        if node_tree.Matby_N_Colors_type=='Viewlayer Prop' and node_tree.name != ".CP_ViewLayer_Material":
                bpy.data.node_groups.remove(node_tree, do_unlink=True)

class NODE_OT_Add_Prop_Node_To_Viewlayer(Operator):
    bl_idname = "wm.add_prop_and_node_to_viewlayer"
    bl_label = ""
    bl_description = "Automatically add properties to each view layer in all scenes\nAdd nodes to editting tree\nRefresh properties after the view layer changes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # 当前编辑的节点树里添加主节点组
        node_tree = context.space_data.edit_tree
        nodes = node_tree.nodes

        #重新导入一个新的节点组，先清除bl里Matby_N_Colors_type=='Scene Prop'的属性，然后导入一个新的，可用按住shift操作

        #先检测当前页面里有几个Viewlayer Group属性的节点树，如果有多个就显示再N面板然后把这两个节点的属性显示在N面板里
        # global viewlayer_prop_nodes
        # viewlayer_prop_nodes.clear()
        # for node_group in bpy.data.node_groups:
        #     if node_group.Matby_N_Colors_type=='Viewlayer Prop':
        #         viewlayer_prop_nodes.append(node_group)
        # if len(viewlayer_prop_nodes)>1:
        #     # self.report({'ERROR'}, "There are multiple node trees with \"Viewlayer Group\" properties in Blender! However, only one nodetree with this property can run the operation!")
        #     # return {"FINISHED"}
        #改为自动将所有节点树为Viewlayer Prop的节点组的节点树都改为.CP_ViewLayer_Material名的，
        #然后删除多余的为Viewlayer Prop的但名字不是.CP_ViewLayer_Material的节点树
        makejustone_viewlayer_prop_nodetree()

        scenes = bpy.data.scenes
        viewlayers = context.scene.view_layers
        if len(viewlayers) == 1 and len(scenes) == 1:
            self.report({'ERROR'}, "Just one viewlayer.")
            return {"FINISHED"}
        
        #视图层添加属性
        i = 0
        length = len(viewlayers)
        for scene in scenes:
            for vlayer in scene.view_layers:
                #self.report({'ERROR'}, f"{vlayer.name}")
                i += 1
                if "CP Viewlayers Material" in vlayer:
                    del vlayer["CP Viewlayers Material"]
                    # 可选：更新当前视图层
                    #bpy.context.view_layer.update()


                # 检查属性是否存在，不存在则创建
                #if "CP Viewlayers Material" not in vlayer:
                vlayer["CP Viewlayers Material"] = i
                #vlayer['data'].update()
                #vlayer.update()没用了
                

                bpy.context.view_layer.update()
                # else:
                #     vlayer["CP Sence Material"] = i#已有就更新顺序，不对会重复添加属性
                # 获取或创建属性
                ui = vlayer.id_properties_ui("CP Viewlayers Material")
                # 更新属性
                ui.update(description=f"Auto set int: {i},don`t change!")
                #ui.update(subtype='INT')
                # 报错'INT' not found in ('NONE', 'FILE_PATH', 'DIR_PATH', 'FILE_NAME', 'BYTE_STRING', 'PASSWORD', 'PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'TIME_ABSOLUTE', 'DISTANCE', 'DISTANCE_CAMERA', 'POWER', 'TEMPERATURE', 'WAVELENGTH', 'COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'XYZ_LENGTH', 'COLOR_GAMMA', 'COORDINATES', 'LAYER', 'LAYER_MEMBER')
                ui.update(default=i)
                ui.update(min=i)#min=1
                ui.update(max=i)#max=length
        
        # #暂时用这个更新属性效果 重新启用所有材质的节点树
        # for mat in bpy.data.materials:
        #     mat.use_nodes=False
        #     mat.use_nodes=True
        

        mainnode=None
        for node in nodes:
            node.select = False
            if node.bl_idname=='ShaderNodeGroup' and node.node_tree and node.node_tree.Matby_N_Colors_type=='Viewlayer Prop':
                mainnode=node#这行代码能否简化
                context.space_data.edit_tree.nodes.active = node
                node.select = True
                bpy.ops.node.view_selected()

        if mainnode is None:            
            mainnode = nodes.new(type='ShaderNodeGroup')
            mainnode.node_tree = import_node('.CP_ViewLayer_Material',True)
            mainnode.name='CP Viewlayers Material'
            mainnode.label='CP Viewlayers Material'
            mainnode.show_options=False
            mainnode.select = True
            for node in node_tree.nodes:
                if node != mainnode:node.select = False  
            nodes.active = mainnode
            bpy.ops.node.view_selected()
       

        ##修改节点组的面板序号和名字为对应的场景名
        if bpy.app.version >= (4, 0, 0):
            # 存储所有场景的名字
            #scene_names = [vlayer.name for vlayer in viewlayers]
            scene_names = []
            for scene in scenes:
                for vlayer in scene.view_layers:
                    scene_names.append("["+scene.name+"]"+" "+vlayer.name)

            
            node_group = next((ng for ng in bpy.data.node_groups if ng.Matby_N_Colors_type == 'Viewlayer Prop'), None)

            links=node_group.links
            ngnodes = node_group.nodes
            propnode=check_propnode(ngnodes)#检查节点组里的属性节点
            
            panels = sum(1 for item in node_group.interface.items_tree if item.item_type == 'PANEL')
            
            # 比较面板数和场景数
            need_add = panels < len(scene_names)
            need_del = panels > len(scene_names)
            # # 打印结果
            # print(f"panels: {panels}, len(scene_names): {len(scene_names)}")
            # print(f"need_add: {need_add}, need_del: {need_del}")

            if need_add or need_del:#只有在面板数量变化时才备份，并且要在下面重命名现有节点的面板名字前备份
                #修改输入端口的名字为面板名字  #这里要先修改节点树里的端口，将每个面板下的输入端口的名字都改为和面板名一样，因为节点组外是没有面板信息可记录用作判断的
                for item in node_group.interface.items_tree[:]:
                    if item.item_type == 'PANEL':
                        # for socket in item.items:##没有面板子级这个属性
                        
                        # 记录子项
                        children_socket = []
                        for childitem in node_group.interface.items_tree[:]:
                            if childitem.item_type == 'SOCKET' and childitem.parent == item:#and childitem.name=="" 
                                children_socket.append(childitem)

                        for socket in children_socket:
                            socket.name=item.name #修改端口名为面板名字

                ##备份blender里所有材质的节点里 节点组类节点 的节点树是node_group的 输入端的值和 连接到的节点(如果有的话)，备份到一个字典里，以输入端的名字为标签，记录输入端类型同时根据输入端类型记录颜色或浮点值或矢量 暂时忽略节点树
                # 备份所有材质的节点组类节点的输入端口信息
                backup_data = {}
                for material in bpy.data.materials:
                    if material.use_nodes:
                        material_backup = backup_node_group_inputs(material,node_group)
                        if material_backup:
                            backup_data[material.name] = material_backup
                
                #print(backup_data)# 输出备份数据

                had_tree_ng=[]##获取所有节点树里 有用该节点树的节点组的 列表备份
                for nodetree in bpy.data.node_groups:
                    if nodetree.contains_tree(node_group):#官方工具检测节点树里是否包含另外一个节点树，但返回的打印第一个会是node_group的名字  file:///F:/Downloads/blender_python_reference_4_1/blender_python_reference_4_1/bpy.types.NodeTree.html#bpy.types.NodeTree.contains_tree
                        #print(nodetree.name)
                        if nodetree != node_group:
                            had_tree_ng.append(nodetree)                            
                #print(had_tree_ng)
                backup_ng_data = {}
                if had_tree_ng:
                    for tree in had_tree_ng:
                        ng_backup = backup_node_group_inputs_innodetree(tree,node_group)
                        if ng_backup:
                            backup_ng_data[tree.name] = ng_backup
                #print(backup_ng_data)

            ##重命名现有节点的面板名字
            ipanel=0
            for item in node_group.interface.items_tree[:]:
                if item.item_type == 'PANEL':##修改面板名
                    ipanel += 1
                    item.name = scene_names[(ipanel - 1) % len(scene_names)]# +  "]"##% len(scene_names): 取模运算，确保索引值在列表范围内,大于范围时从第一个开始
                    #self.report({'ERROR'}, f"{item.name},{item.item_type}")

            if need_add or need_del:
                #新增面板和节点组
                if need_add:
                    #找出输入输出节点
                    in_node = next((node for node in node_group.nodes if node.bl_idname == 'NodeGroupInput'), None)
                    out_node = next((node for node in node_group.nodes if node.bl_idname == 'NodeGroupOutput'), None)
                    

                    add_nodes=len(scene_names)-panels
                    start_int=panels
                    #print(f"need_add ,{len(scene_names)}图层数{add_nodes},面板数{panels}")
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
                        shader_socket = node_group.interface.new_socket(name="B",in_out='INPUT',socket_type = 'NodeSocketShader', parent=new_panel)

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
                            new_node_group.location=last_node.location[0]+250,last_node.location[1]-160#
                            out_node.location=new_node_group.location[0]+250,new_node_group.location[1]#
                            
                            connect_nodes(links, last_node, new_node_group)
                            connect_nodes(links, in_node, new_node_group)
                            connect_nodes(links, new_node_group,out_node)

                        color_socket.name=panel_name
                        float_socket.name=panel_name
                        vector_socket.name=panel_name
                        vector_socket.hide_value = True
                        shader_socket.name=panel_name

                if need_del:
                    #print("need_del")
                    #删除多余的面板
                    i=0
                    #这里直接循环里用[:]还是会导致闪退，先用一个列表存要删除的index
                    delindex=[]
                    for item in node_group.interface.items_tree[:]:
                        if item.item_type == 'PANEL':##修改面板名
                            i += 1
                            if i > len(scene_names):
                                for childitem in node_group.interface.items_tree[:]:
                                    if childitem.item_type == 'SOCKET' and childitem.parent == item:
                                        delindex.append(childitem.index)
                                        #node_group.interface.remove(childitem)#移除面板里的项目 这个是移除端口，后面一个布尔再移除面板类型端口时将面板下的端口移动到主面板下move_content_to_parent=True
                                #node_group.interface.remove(item)#移除面板
                                delindex.append(item.index)

                    #print(f"{delindex}")
                    # 对 delindex 进行排序，从大到小,保证从最后往前删除
                    delindex.sort(reverse=True)
                    items_tree_copy = node_group.interface.items_tree[:]
                    for index in delindex:
                        #print(f"{index}")
                        for item in items_tree_copy:
                            if item.index==index:
                                node_group.interface.remove(item)

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


                #修改输入端口的名字为面板名字  因为上面##重命名现有节点的面板名字 会导致子端口和父面板名字不一样
                for item in node_group.interface.items_tree[:]:
                    if item.item_type == 'PANEL':
                        #children_socket = []
                        for childitem in node_group.interface.items_tree[:]:
                            if childitem.item_type == 'SOCKET' and childitem.parent == item:#and childitem.name=="" 
                                #children_socket.append(childitem)
                                childitem.name=item.name #修改端口名为面板名字
                        # for socket in children_socket:
                        #     socket.name=item.name #修改端口名为面板名字

                # # #根据backup_data字典 恢复每个材质里该节点组的输入值和连接
                for material in bpy.data.materials:
                    if material.use_nodes and material.name in backup_data:
                        restore_node_group_inputs(material, backup_data[material.name], node_group)

                if had_tree_ng:
                    for tree in had_tree_ng:
                        restore_node_group_inputs_innodetree(tree, backup_ng_data,node_group)

            # 清空输入端的名字
            for item in node_group.interface.items_tree:
                if item.item_type == 'SOCKET' and item.in_out=="INPUT":
                    item.name = " " #改为空格名 这里设置为空名字会导致Voronoi Linker预览时直接闪退  尝试新建一个新端口或面板后删除也没有用
                    # if item.socket_type == 'NodeSocketColor':
                    #     item.name = "Color"
                    # if item.socket_type == 'NodeSocketFloat':
                    #     item.name = "Float"
                    if item.socket_type == 'NodeSocketVector':
                        item.name = "Vector"
                    if item.socket_type == 'NodeSocketShader':
                        item.name = "Shader"

            #node_group.interface_update(context)
            
        return {"FINISHED"}

#备份每个材质节点树里的该节点的输入端值
def backup_node_group_inputs(material, protree):
    backup_data = {}
    # 遍历材质的节点树
    if material.use_nodes:
        for node in material.node_tree.nodes:
            links=material.node_tree.links
            if node.type == 'GROUP' and node.node_tree and node.node_tree==protree:
                # 初始化节点的信息字典
                node_info = {
                }

                # 记录每个输入端口的信息
                for index, input in enumerate(node.inputs):
                    # if input.type == 'SHADER':
                    #     continue  # 跳过后续代码，继续下一个循环

                    value=1
                    if input.type in ['VALUE','INT','BOOLEAN']:#浮点
                        value=input.default_value
                    elif input.type == 'RGBA':
                        value=input.default_value[:4]
                    elif input.type == 'VECTOR':
                        value=input.default_value[:3]
                    elif input.type == 'SHADER':
                        value=None

                    input_info = {
                        'name': input.name,
                        'type': input.type,
                        'default_value': value,
                        'linked':False,
                        #'linked_node': None,
                        'linked_socket': None
                    }

                    # 检查是否有连接
                    if input.is_linked:
                        link = input.links[0]
                        input_info['linked'] = True
                        #input_info['linked_node'] = link.from_node.name
                        input_info['linked_socket'] = link.from_socket

                        #断开连接避免端口数量变化后连接错位
                        links.remove(link)

                    # 将输入端口信息添加到节点信息字典中
                    #不能用名字做标签重名的话会覆盖 node_info[input.name] = input_info
                    # 将输入端口信息添加到节点信息字典中
                    node_info[index] = input_info


                # 将节点信息添加到备份字典中
                backup_data[node.name] = node_info

    return backup_data

#根据备份恢复材质节点树里的连接或节点组端口的自定义值
def restore_node_group_inputs(material, backup_data, protree):
    # 遍历备份数据
    for node_name, node_info in backup_data.items():
        node = material.node_tree.nodes.get(node_name)
        if node and node.type == 'GROUP' and node.node_tree == protree:
            # # 恢复输入端口的值和连接
            # for index, input_info in node_info.items():
            #     if isinstance(index, int):  # 确保索引是整数
            #         input = node.inputs[index]
            #         input.default_value = input_info['default_value']
            #         if input_info['linked']:
            #             linked_socket = input_info['linked_socket']#material.node_tree.nodes.get(input_info['linked_socket'].node.name).outputs[input_info['linked_socket'].index]
            #             material.node_tree.links.new(linked_socket, input)

            #应该循环inputs，从最后一个往前 # 恢复输入端口的值和连接
            for input in node.inputs:
                # if input.type == 'SHADER':
                #     continue  # 跳过后续代码，继续下一个循环
                for index, input_info in node_info.items():
                    #for input_info in input_infoss:
                    #print(f"{input_info['name']}")
                    if input.name==input_info['name'] and input.type==input_info['type']:
                        if input.type != 'SHADER':
                            input.default_value = input_info['default_value']
                        # print(f"{input_info['linked']}++{input_info['linked_socket']}+{input}")
                        if input_info['linked']:
                            material.node_tree.links.new(input_info['linked_socket'], input)

#备份节点树里子节点组的该节点的输入端值
def backup_node_group_inputs_innodetree(tree,protree):
    backup_data = {}
    for node in tree.nodes:
        links=tree.links
        if node.type == 'GROUP' and node.node_tree and node.node_tree==protree:
            # 初始化节点的信息字典
            node_info = {
            }

            # 记录每个输入端口的信息
            for index, input in enumerate(node.inputs):
                # if input.type == 'SHADER':
                #     continue  # 跳过后续代码，继续下一个循环

                value=1
                if input.type in ['VALUE','INT','BOOLEAN']:#浮点
                    value=input.default_value
                elif input.type == 'RGBA':
                    value=input.default_value[:4]
                elif input.type == 'VECTOR':
                    value=input.default_value[:3]
                elif input.type == 'SHADER':
                    value=None

                input_info = {
                    'name': input.name,
                    'type': input.type,
                    'default_value': value,
                    'linked':False,
                    #'linked_node': None,
                    'linked_socket': None
                }

                # 检查是否有连接
                if input.is_linked:
                    link = input.links[0]
                    input_info['linked'] = True
                    #input_info['linked_node'] = link.from_node.name
                    input_info['linked_socket'] = link.from_socket

                    #断开连接避免端口数量变化后连接错位
                    links.remove(link)

                node_info[index] = input_info

            # 将节点信息添加到备份字典中
            backup_data[node.name] = node_info

    return backup_data

#根据备份恢复节点树里子节点组的该节点的自定义值
def restore_node_group_inputs_innodetree(tree, backup_data, protree):
    # 遍历备份数据
    for ng, node_infos in backup_data.items():
        for node_name, node_info in node_infos.items():
            node = tree.nodes.get(node_name)
            if node and node.type == 'GROUP' and node.node_tree == protree:
                #应该循环inputs，从最后一个往前 # 恢复输入端口的值和连接
                for input in node.inputs:
                    for index, input_info in node_info.items():
                        if input.name==input_info['name'] and input.type==input_info['type']:
                            if input.type != 'SHADER':
                                input.default_value = input_info['default_value']
                            if input_info['linked']:
                                tree.links.new(input_info['linked_socket'], input)

# ----------------------------------------------------视图层批量渲染---------------------------------------------------- #
# ----------------------------------------------------视图层批量渲染---------------------------------------------------- #
# ----------------------------------------------------视图层批量渲染---------------------------------------------------- #
def get_ac_scene_list_index(self):
    try:
        scenes = bpy.data.scenes

        for index, node in enumerate(scenes):
            if node == bpy.context.window.scene:
                return index

        return -1
    except Exception as err:
        import sys
        print('-----', err, end=' | ')
        print('get_ac_scene_list_index Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

def set_ac_scene_list_index(self, value):
    try:
        scenes = bpy.data.scenes
        scene = scenes[value]
        if scene:
            bpy.context.window.scene = scene
        update_viewlayercamera()
    except Exception as err:
        print('-----', err, end=' | ')
        print('set_ac_scene_list_index Error on line {}'.format(sys.exc_info()[-1].tb_lineno))


def rna_idprop_quote_path(prop):
    return "[\"%s\"]" % bpy.utils.escape_identifier(prop)

class CPBR_UL_viewlayer_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        wm = context.window_manager
        scene = data  # data 是当前场景对象
        renderscenen=scene.CPBR_Main_Props.cp_render_scene
        # 获取当前场景的活动视图层 没有这个属性 active_view_layer = scene.view_layer

        col = layout.column(heading='', align=True)

        row=col.row(heading='', align=True)
        if renderscenen:
            row.prop(item, "use", text="",icon='RENDER_STILL')#是否渲染该图层

        # row.prop(item, "name", text="", emboss=False, icon='RENDERLAYERS')
        r=row.row(heading='', align=True)
        if item == context.window.view_layer:
            r.alert = True
        op=r.operator("cpbr.switch_scene_view_layer", text=item.name, icon='RENDERLAYERS')
        op.scenename = scene.name
        op.viewlayername = item.name

        show_preview=wm.WM_CPBR_Main_Props.show_all_preview and scene.CPBR_Main_Props.show_scene_preview
        if show_preview:
            op=row.operator("cpbr.render_viewport", icon='RESTRICT_RENDER_OFF', text='')
            op.scenename = scene.name
            op.layername = item.name

        if renderscenen and item.use:
            try:
                row = col.row(heading='', align=True)
                if not scene.CPBR_Main_Props.cp_use_scene_camera:
                    row_7C74D = row.row(heading='', align=True)
                    attr_6CE1A = '["' + str('CPBatchRender Viewlayers render_camera' + '"]') 
                    if hasattr(item, attr_6CE1A):
                        row_7C74D.prop(item, attr_6CE1A, text='', icon='VIEW_CAMERA', emboss=True)
                        # #参考官方的rna_prop_ui.py显示方法
                        # row_7C74D.template_ID(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_camera"), text="",filter='AVAILABLE',)

                if not scene.CPBR_Main_Props.cp_use_scene_world:
                    row_7C74D = row.row(heading='', align=True)
                    attr_6CE22 = '["' + str('CPBatchRender Viewlayers render_world' + '"]')
                    if hasattr(item, attr_6CE22):
                        row_7C74D.prop(item, attr_6CE22, text='', icon='WORLD', emboss=True)
                        #row_7C74D.template_ID(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_world"), text="",filter='AVAILABLE',)
                    
                if not scene.CPBR_Main_Props.cp_use_scene_resolution:
                    row_1FD8B = col.row(heading='', align=True)
                    attr_6CE33 = '["' + str('CPBatchRender Viewlayers render_resolution' + '"]') 
                    if hasattr(item, attr_6CE33):
                        row_1FD8B.prop(item, attr_6CE33, text='', icon_value=0, emboss=True)
                        #row_1FD8B.prop(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_resolution"), text="")
            except:
                pass

        ## 缩略图
        if show_preview:
            tex="Screenshot preview"
            image = None
            if "CPBatchRender Viewlayers render_preview" in item and item["CPBatchRender Viewlayers render_preview"]:
                image = bpy.data.images.get(item["CPBatchRender Viewlayers render_preview"].name)
            if image :
                if image.preview is not None:
                    col.template_icon(icon_value=image.preview.icon_id, scale=wm.WM_CPBR_Main_Props.scale_preview)

            else:
                tex="Screenshot preview ⇑ "
                prerow=col.row()
                prerow.alert = True

                r0=prerow.row(align=True)
                r0.alignment = 'RIGHT'#[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]
                r0.label(text=tex)
            
                # op=prerow.operator("cpbr.render_viewport", icon='RESTRICT_RENDER_OFF', text=tex)
                # op.scenename = scene.name
                # op.layername = item.name

        if bpy.app.version >= (4, 2):
            col.separator(type="LINE") 
        else:
            # col.separator()
            col.label(text="." * 300)
        
class CPBR_UL_scenes_list(UIList):
    # def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # if isinstance(item, bpy.types.Scene):
        #     prefs = get_prefs()   

        #     col = layout.column(heading="", align=True)
        #     r=col.row(align=True)
        #     r.scale_y = 1.1
        #     r.prop(item.CPBR_Main_Props, "cp_render_scene", text="",icon_value=192)#是否渲染该场景
        #     r.prop(item, "name", text="", emboss=False, icon='SCENE_DATA')#场景名# emboss=False让文本不是编辑状态而是要双击才编辑
        #     if item.CPBR_Main_Props.show_all_preview:
        #         r.prop(item.CPBR_Main_Props, "show_scene_preview",icon_value=755, text="")
        #     renderscenen=item.CPBR_Main_Props.cp_render_scene
        #     if renderscenen:
        #         s0=col.split(factor=0.05, align=True)
        #         s0.scale_y = 1.0
        #         s0.separator(factor=0.0)
        #         box_scene = s0.box()
        #         box_col = box_scene.column(heading="", align=True)

        #         r=box_col.row(align=True)

        #         #场景相机
        #         r0=r.row(align=True)
        #         #r0.alert = True
        #         r0.enabled = item.CPBR_Main_Props.cp_use_scene_camera
        #         r0.active = item.CPBR_Main_Props.cp_use_scene_camera            
        #         r0.prop(item, "camera", text="")

        #         ##所有视图层用场景相机
        #         r.prop(item.CPBR_Main_Props, "cp_use_scene_camera", text="", icon_value=772)

        #         #if item.world:
        #         r_world=box_col.row(align=True)
        #         r0=r_world.row(align=True)
        #         #r0.alert = True
        #         r0.enabled = item.CPBR_Main_Props.cp_use_scene_world
        #         r0.active = item.CPBR_Main_Props.cp_use_scene_world  
        #         r0.template_ID(item, "world")
        #         r_world.prop(item.CPBR_Main_Props, "cp_use_scene_world", text="", icon_value=158)

                
        #         r1=box_col.row(align=True)

        #         r2=r1.row(align=True)
        #         r2.enabled = item.CPBR_Main_Props.cp_use_scene_resolution
        #         r2.active = item.CPBR_Main_Props.cp_use_scene_resolution   
        #         r2.prop(item.render, "resolution_x", text="X")
        #         r2.prop(item.render, "resolution_y", text="Y")

        #         r1.prop(item.CPBR_Main_Props, "cp_use_scene_resolution", text="", icon_value=597)

        #         col.separator(factor=1.0)

        #     scenes = bpy.data.scenes
        #     view_layers = scenes[item.name].view_layers
        
        #     is_active = item.name == bpy.context.window.scene.name
        #     for layer in view_layers:

        #         if item.CPBR_Main_Props.show_all_preview and item.CPBR_Main_Props.show_scene_preview:
        #             ##C:\Users\CP\AppData\Roaming\Blender Foundation\Blender\Addons_Big addons\addons\gscatter\common  ops.py 53
        #             # col.template_icon(icon_value=previews.get(icons.get_icon_path("tutorial_cover")).icon_id, scale=18)
        #             image = None
        #             if "CPBatchRender Viewlayers render_preview" in layer and layer["CPBatchRender Viewlayers render_preview"]:
        #                 image = bpy.data.images.get(layer["CPBatchRender Viewlayers render_preview"].name)
        #             if image is not None:
        #                 if image.preview is not None:
        #                     # s1=col.split(factor=0.05, align=True)
        #                     # s1.scale_y = 1.5
        #                     # s1.separator(factor=0.0)
        #                     # box_e = s1.box()
        #                     # #prow=box_e.row(align=True)
        #                     col.template_icon(icon_value=image.preview.icon_id, scale=wm.WM_CPBR_Main_Props.scale_preview)
        #             else:
        #                 col.template_icon(icon_value=53, scale=wm.WM_CPBR_Main_Props.scale_preview)


        #         s1=col.split(factor=0.05, align=True)
        #         s1.scale_y = 1.5
        #         s1.separator(factor=0.0)



        #         row=s1.row(align=True)
        #         s2=row.split(factor=0.05, align=True)
        #         if renderscenen:
        #             s2.prop(layer, "use", text="",icon_value=192)#是否渲染该图层
        #         else:
        #             s2.label(text="", icon_value=0)
                
        #         rr=s2.row(align=True)
        #         if layer == context.window.view_layer and is_active:
        #             rr.alert =True
        #         op=rr.operator("cpbr.switch_scene_view_layer", text=layer.name)#icon_value=187, 
        #         op.scenename = item.name
        #         op.viewlayername = layer.name

        #         if item.CPBR_Main_Props.show_all_preview and item.CPBR_Main_Props.show_scene_preview:
        #             op=rr.operator("cpbr.render_viewport", icon_value=83, text="")
        #             op.scenename = item.name
        #             op.layername = layer.name



        #         if renderscenen:
        #             #
        #             if not item.CPBR_Main_Props.cp_use_scene_camera:
        #                 r1=col.split(factor=0.1, align=True)
        #                 r1.separator(factor=0.0)
        #                 #参考官方的rna_prop_ui.py显示方法
        #                 r1.template_ID(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_camera"), text="",filter='AVAILABLE',)

        #             if not item.CPBR_Main_Props.cp_use_scene_world:
        #                 r1=col.split(factor=0.1, align=True)
        #                 r1.separator(factor=0.0)
        #                 #参考官方的rna_prop_ui.py显示方法
        #                 r1.template_ID(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_world"), text="",filter='AVAILABLE',)
                    
        #             if not item.CPBR_Main_Props.cp_use_scene_resolution:
        #                 r2=col.split(factor=0.1, align=True)
        #                 r2.separator(factor=5.0)
        #                 row3=r2.row(align=True)
        #                 #参考官方的rna_prop_ui.py显示方法
        #                 row3.label(text="", icon_value=597)
        #                 row3.prop(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_resolution"), text="")

        #             col.separator(factor=1.0)

    # 成功，但不是采用子列表
    # def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # if isinstance(item, bpy.types.Scene):
        #     #prefs = get_prefs()   
        #     renderscenen=item.CPBR_Main_Props.cp_render_scene

        #     col_49E9F = layout.column(heading='', align=True)
            
        #     row_A41D3 = col_49E9F.row(heading='', align=True)

        #     #row_A41D3.label(text="", icon_value=0)

        #     row_A41D3.alert = False
        #     row_A41D3.enabled = True
        #     row_A41D3.active = True
        #     row_A41D3.use_property_split = False
        #     row_A41D3.use_property_decorate = False
        #     row_A41D3.scale_x = 1.0
        #     row_A41D3.scale_y = 1.0
        #     row_A41D3.alignment = 'EXPAND'#[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]

        #     try:
        #         sub=row_A41D3.row(align=True)
        #         sub.scale_x = 0.35 if item.CPBR_Main_Props.show_all_preview else 0.3
        #         # 使用当前项的索引显示序号
        #         sub.label(text="-%d" % (index + 1))
        #     except ValueError:
        #         pass

        #     sub2=row_A41D3.row(align=True)
        #     sub.scale_y = 1.0
        #     sub2.prop(item, "name", text="", emboss=False, icon='SCENE_DATA')#场景名# emboss=False让文本不是编辑状态而是要双击才编辑

        #     sub2.prop(item.CPBR_Main_Props, "cp_use_scene_camera", text="", icon_value=772)
        #     sub2.prop(item.CPBR_Main_Props, "cp_use_scene_world", text="", icon_value=158)
        #     sub2.prop(item.CPBR_Main_Props, "cp_use_scene_resolution", text="", icon_value=597)
        #     sub2.separator(factor=1.0)

        #     if item.CPBR_Main_Props.show_all_preview:
        #         sub2.prop(item.CPBR_Main_Props, "show_scene_preview",icon_value=755, text="")

        #     row_kong = col_49E9F.row(heading='', align=True)
        #     row_kong.scale_y = 0.2
        #     row_kong.label(text="", icon_value=0)

            

        #     grid_C74E9 = col_49E9F.grid_flow(columns=2, row_major=True, even_columns=False, even_rows=False, align=True)
            
        #     grid_C74E9.prop(item.CPBR_Main_Props, "cp_render_scene", text="",icon_value=192)#是否渲染该场景

        #     box_86729 = grid_C74E9.box()
            
        #     col_01C15 = box_86729.column(heading='', align=True)
        #     if renderscenen:
        #         row_4AA07 = col_01C15.row(heading='', align=True)

        #         #场景相机
        #         # if item.CPBR_Main_Props.cp_use_scene_camera:
        #         r0=row_4AA07.row(align=True)
        #         #r0.alert = True
        #         r0.enabled = item.CPBR_Main_Props.cp_use_scene_camera
        #         r0.active = item.CPBR_Main_Props.cp_use_scene_camera            
        #         #r0.prop(item, "camera", text="")
        #         r0.prop(item, "camera", text='', icon_value=772, emboss=True)

        #         # row_4AA07.prop(item.CPBR_Main_Props, "cp_use_scene_camera", text="", icon_value=772)

        #         #场景世界环境
        #         # row_DBF9D = col_01C15.row(heading='', align=True)
        #         #if item.CPBR_Main_Props.cp_use_scene_world:
        #         # r_world=row_DBF9D.row(align=True)
        #         r1=row_4AA07.row(align=True)#r_world.row(align=True)
        #         #r0.alert = True
        #         r1.enabled = item.CPBR_Main_Props.cp_use_scene_world
        #         r1.active = item.CPBR_Main_Props.cp_use_scene_world  
        #         #r1.template_ID(item, "world")
        #         r1.prop(item, 'world', text='', icon_value=82, emboss=True)

        #         # row_DBF9D.prop(item.CPBR_Main_Props, "cp_use_scene_world", text="", icon_value=158)

        #         #if item.CPBR_Main_Props.cp_use_scene_resolution:
        #         #场景分辨率
        #         row_53579 = col_01C15.row(heading='', align=True)

        #         r3=row_53579.row(align=True)
        #         r3.enabled = item.CPBR_Main_Props.cp_use_scene_resolution
        #         r3.active = item.CPBR_Main_Props.cp_use_scene_resolution   
        #         r3.prop(item.render, "resolution_x", text="Resolution X")
        #         r3.prop(item.render, "resolution_y", text="Y")
                
        #         # row_53579.prop(item.CPBR_Main_Props, "cp_use_scene_resolution", text="", icon_value=597)

        #         col_01C15.separator(factor=1.0)

        #     scenes = bpy.data.scenes
        #     view_layers = scenes[item.name].view_layers
        #     is_active = item.name == bpy.context.window.scene.name
        #     for layer in view_layers:

        #         box_78EBA = col_01C15.box()
                
        #         col_EA64C = box_78EBA.column(heading='', align=True)
                
        #         if item.CPBR_Main_Props.show_all_preview and item.CPBR_Main_Props.show_scene_preview:
        #             ##C:\Users\CP\AppData\Roaming\Blender Foundation\Blender\Addons_Big addons\addons\gscatter\common  ops.py 53
        #             # col.template_icon(icon_value=previews.get(icons.get_icon_path("tutorial_cover")).icon_id, scale=18)
        #             tex=""
        #             image = None
        #             if "CPBatchRender Viewlayers render_preview" in layer and layer["CPBatchRender Viewlayers render_preview"]:
        #                 image = bpy.data.images.get(layer["CPBatchRender Viewlayers render_preview"].name)
        #             if image is not None:
        #                 if image.preview is not None:
        #                     # s1=col.split(factor=0.05, align=True)
        #                     # s1.scale_y = 1.5
        #                     # s1.separator(factor=0.0)
        #                     # box_e = s1.box()
        #                     # #prow=box_e.row(align=True)
        #                     col_EA64C.template_icon(icon_value=image.preview.icon_id, scale=context.scene.CPBR_Main_Props.scale_preview)
        #             else:
        #                 tex="Screenshot preview"
        #             #     col_EA64C.alignment = 'RIGHT'#[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]
        #             #     col_EA64C.label(text="Manually screenshot thumbnails ↴  ", icon_value=0)
        #             #     # row_render = col_EA64C.row(heading='', align=True)
        #             #     # row_render.scale_y = 1.5
        #             #     # row_render.alignment = 'CENTER'
        #             #     # op=row_render.operator("cpbr.render_viewport", icon_value=83, text="")
        #             #     # op.scenename = item.name
        #             #     # op.layername = layer.name


        #         split_C95C3 = col_EA64C.split(factor=0.1 if renderscenen else 1, align=True)
                
        #         split_C95C3.scale_y = 1.5
        #         if renderscenen:
        #             split_C95C3.prop(layer, "use", text="",icon_value=192)#是否渲染该图层
 
        #         row_823B1 = split_C95C3.row(heading='', align=True)
        #         if layer == context.window.view_layer and is_active:
        #             row_823B1.alert = True
                
        #         op=row_823B1.operator("cpbr.switch_scene_view_layer", text=layer.name)#icon_value=187, 
        #         op.scenename = item.name
        #         op.viewlayername = layer.name

        #         if item.CPBR_Main_Props.show_all_preview and item.CPBR_Main_Props.show_scene_preview:
        #             row_030C8 = row_823B1.row(heading='', align=True)
        #             row_030C8.alert = False
                    
        #             op=row_030C8.operator("cpbr.render_viewport", icon_value=83, text=tex)
        #             op.scenename = item.name
        #             op.layername = layer.name

        #         if renderscenen:
        #             try:   
        #                 row_7C74D = col_EA64C.row(heading='', align=True)
        #                 row_7C74D.scale_y = 1.0

        #                 if not item.CPBR_Main_Props.cp_use_scene_camera:
        #                     attr_6CE1A = '["' + str('CPBatchRender Viewlayers render_camera' + '"]') 
        #                     row_7C74D.prop(layer, attr_6CE1A, text='', icon_value=772, emboss=True)
        #                     # #参考官方的rna_prop_ui.py显示方法
        #                     # row_7C74D.template_ID(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_camera"), text="",filter='AVAILABLE',)

        #                 if not item.CPBR_Main_Props.cp_use_scene_world:
        #                     attr_6CE22 = '["' + str('CPBatchRender Viewlayers render_world' + '"]') 
        #                     row_7C74D.prop(layer, attr_6CE22, text='', icon_value=82, emboss=True)
        #                     #row_7C74D.template_ID(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_world"), text="",filter='AVAILABLE',)
                        
        #                 if not item.CPBR_Main_Props.cp_use_scene_resolution:
        #                     row_1FD8B = col_EA64C.row(heading='', align=True)
        #                     #row_1FD8B.label(text="", icon_value=597)
        #                     attr_6CE33 = '["' + str('CPBatchRender Viewlayers render_resolution' + '"]') 
        #                     row_1FD8B.prop(layer, attr_6CE33, text='', icon_value=0, emboss=True)
        #                     #row_1FD8B.prop(layer, rna_idprop_quote_path("CPBatchRender Viewlayers render_resolution"), text="")
        #             except:
        #                 pass

        #         col_01C15.separator(factor=1.0)

        #     #col_49E9F.separator(factor=2.0)
        #     if bpy.app.version >= (4, 2):
        #         col_49E9F.separator(type="LINE") 
                
        #     else:
        #         col_49E9F.separator()

    # 采用子列表
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if isinstance(item, bpy.types.Scene):
            #prefs = get_prefs()   
            renderscenen=item.CPBR_Main_Props.cp_render_scene
            wm = context.window_manager

            col_49E9F = layout.column(heading='', align=True)
            
            row_A41D3 = col_49E9F.row(heading='', align=True)

            #row_A41D3.label(text="", icon_value=0)

            row_A41D3.alert = False
            row_A41D3.enabled = True
            row_A41D3.active = True
            row_A41D3.use_property_split = False
            row_A41D3.use_property_decorate = False
            row_A41D3.scale_x = 1.0
            row_A41D3.scale_y = 1.3
            row_A41D3.alignment = 'EXPAND'#[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]

            row_A41D3.prop(item.CPBR_Main_Props, "cp_render_scene", text="",icon='RENDER_STILL')#是否渲染该场景

            row_A41D3.prop(item.CPBR_Main_Props, "zhedie", text="",icon='DOWNARROW_HLT' if item.CPBR_Main_Props.zhedie else 'RIGHTARROW', emboss=False)#折叠

            # try:
            #     sub=row_A41D3.row(align=True)
            #     sub.scale_x = 0.35 if wm.WM_CPBR_Main_Props.show_all_preview else 0.3
            #     # 使用当前项的索引显示序号
            #     sub.label(text="-%d" % (index + 1))
            # except ValueError:
            #     pass

            sub2=row_A41D3.row(align=True)
            # sub.scale_y = 1.0
            sub2.prop(item, "name", text="", emboss=False, icon='SCENE_DATA')#场景名# emboss=False让文本不是编辑状态而是要双击才编辑

            sub2.prop(item.CPBR_Main_Props, "cp_use_scene_camera", text="", icon='VIEW_CAMERA')
            sub2.prop(item.CPBR_Main_Props, "cp_use_scene_world", text="", icon='WORLD_DATA')
            sub2.prop(item.CPBR_Main_Props, "cp_use_scene_resolution", text="", icon='ORIENTATION_VIEW')
            sub2.separator(factor=1.0)

            if wm.WM_CPBR_Main_Props.show_all_preview:
                sub2.prop(item.CPBR_Main_Props, "show_scene_preview",icon='SEQ_PREVIEW', text="")

            if not item.CPBR_Main_Props.zhedie:
                if bpy.app.version >= (4, 2):
                    col_49E9F.separator(type="LINE") 
                else:
                    col_49E9F.label(text="." * 300)
                return

            # if renderscenen:
            r=col_49E9F.row(align=True)
            r0=r.row(align=True)
            r0.alignment = 'LEFT'#[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]
            r0.label(icon_value=0)
            s = r.grid_flow(columns=0, row_major=True, even_columns=False, even_rows=False, align=True)
            # r=col_49E9F.row(align=True)
            #场景相机
            r0=s.row(align=True)
            r0.enabled = item.CPBR_Main_Props.cp_use_scene_camera
            r0.active = item.CPBR_Main_Props.cp_use_scene_camera            
            r0.prop(item, "camera", text='', icon='VIEW_CAMERA', emboss=True)

            #场景世界环境
            r1=s.row(align=True)#r_world.row(align=True)
            #r0.alert = True
            r1.enabled = item.CPBR_Main_Props.cp_use_scene_world
            r1.active = item.CPBR_Main_Props.cp_use_scene_world  
            r1.prop(item, 'world', text='', icon='WORLD_DATA', emboss=True)

            #场景分辨率
            r3=s.row(align=True)
            r3.enabled = item.CPBR_Main_Props.cp_use_scene_resolution
            r3.active = item.CPBR_Main_Props.cp_use_scene_resolution   
            r3.prop(item.render, "resolution_x", text="Resolution X")
            r3.prop(item.render, "resolution_y", text="Y")
            
            # if not item.CPBR_Main_Props.zhedie:
            #     if bpy.app.version >= (4, 2):
            #         col_49E9F.separator(type="LINE") 
            #     else:
            #         col_49E9F.label(text="." * 300)
            #     return
           
            col_49E9F.separator(factor=1.0)

            # s = col_49E9F.grid_flow(columns=2, row_major=True, even_columns=False, even_rows=False, align=True)

            # s.prop(item.CPBR_Main_Props, "cp_render_scene", text="",icon='RENDER_STILL')#是否渲染该场景

            r=col_49E9F.row(align=True)
            r0=r.row(align=True)
            r0.alignment = 'LEFT'#[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]
            r0.label(icon_value=0)
            r.template_list("CPBR_UL_viewlayer_list", "", item, "view_layers", item.CPBR_Main_Props, "cp_active_viewlayer_index",rows=len(item.view_layers))

            if bpy.app.version >= (4, 2):
                col_49E9F.separator(type="LINE") 
            else:
                col_49E9F.separator()

            return

class CPBR_PT_UIListPanel(Panel):
    bl_label = "Batch Render"#Viewlayer(Scenes) List
    bl_idname = "CPBR_PT_UIListPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Batch Render'
    bl_order = 1
    bl_context = "objectmode"

    def draw(self, context):
        #prefs = get_prefs()
        layout = self.layout
        wm = context.window_manager
        col = layout.column(heading="", align=True)

        r = col.row(heading='Viewlayers List:', align=True)
        #col.label(text='Viewlayer(Scenes) List')
        if wm.WM_CPBR_Main_Props.show_all_preview:
            r.prop(wm.WM_CPBR_Main_Props, "scale_preview", text="Scale")
        r.prop(wm.WM_CPBR_Main_Props, "show_all_preview",icon='SEQ_PREVIEW', text="")

        r.separator(factor=1.0)

        # col.template_list("CPBR_UL_scenes_list", "", bpy.data, "scenes", context.scene.CPBR_Main_Props, "cp_change_active_scene_index")
        col.template_list("CPBR_UL_scenes_list", "", bpy.data, "scenes", wm.WM_CPBR_Main_Props, "cp_change_active_scene_index",rows=len(bpy.data.scenes))


        rowpath = layout.row(heading='', align=True)
        rp = rowpath.row(heading='', align=True)
        use_blendpath=wm.WM_CPBR_Main_Props.use_auto_blenderpath
        # rp.active = use_blendpath  
        rp.prop(wm.WM_CPBR_Main_Props, "use_auto_blenderpath",text="Save to BL file`s directory")

        blendPath = str(bpy.path.abspath('//'))  #返回相对于当前混合文件的绝对路径
        blendPath += os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0]#去除.blend后缀的名字
        ro = rowpath.row(heading='', align=True)
        ro.prop(wm.WM_CPBR_Main_Props, "auto_saverendertext")
        ro.operator("wm.path_open", text="",icon = 'FILE_FOLDER').filepath = blendPath if use_blendpath else wm.WM_CPBR_Main_Props.directory
        if not use_blendpath:
            layout.prop(wm.WM_CPBR_Main_Props, "directory", text="")


        row = layout.row(heading='', align=True)
        row.scale_y = 2.5
        row.operator("cpbr.batch_render", icon='RENDER_STILL',)
        global bugmes
        if bugmes:
            # 将字符串按照 '-' 分割
            segments = bugmes.split('- ')
            col = layout.column(heading="", align=True)
            for t in segments:
                r=col.row(align=True)
                r.alert = True
                r.label(text=t, icon='ERROR')
            # layout.label(text="Batch rendering....", icon_value=1)
        #     # global progress
        #     # layout.progress(factor = progress, text = "Updating")
        if bpy.app.version >= (4, 2):
            layout.separator(type="LINE")  
        else:
            layout.separator()

        #if CPBR_OT_BatchRender.running:
            # text=renderscenename
            # layout.label(text=text, icon_value=0)
        #layout.label(text="视图层设置独立相机时记得选择对应场景里的相机!", icon_value=1)
        layout.label(text=iface_("Batch rendering is saved with the compositor\'s output node!"), icon='QUESTION')
        layout.label(text=iface_("Only need one viewlayer node and one output node in compositor!"), icon='QUESTION')
        layout.label(text=iface_("Other plugins that automatically set the path of the output node will affect the save path!"), icon='QUESTION')

        if bpy.app.version >= (4, 2):
            layout.separator(type="LINE")  
        else:
            layout.separator()
        ##！！！同步渲染器的面板何和色彩空和视图层的

# 操作类用于切换场景和视图层
class CPBR_OT_SwitchSceneViewLayer(Operator):
    bl_idname = "cpbr.switch_scene_view_layer"
    bl_label = ""
    bl_description = "Switch Scene and ViewLayer"
    bl_options = {"UNDO"}#"REGISTER",

    scenename: StringProperty()
    viewlayername: StringProperty()

    def execute(self, context):
        scenes = bpy.data.scenes
        for scene in scenes:
            if scene.name == self.scenename:
                bpy.context.window.scene = scene
                break
        
        view_layers = scenes[self.scenename].view_layers
        for layer in view_layers:
            if layer.name == self.viewlayername:
                #bpy.context.scene.view_layers.active = layer
                #https://blender.stackexchange.com/questions/131881/change-active-view-layer-with-python
                context.window.view_layer = layer
                
                update_viewlayer_props()

                ##根据视图层相机 切换场景相机
                try:
                    if not bpy.data.scenes[self.scenename].CPBR_Main_Props.cp_use_scene_camera and "CPBatchRender Viewlayers render_camera" in layer and layer["CPBatchRender Viewlayers render_camera"]:
                        #print(layer["CPBatchRender Viewlayers render_camera"])
                        #bpy.data.scenes[self.scenename].camera=bpy.data.objects[layer["CPBatchRender Viewlayers render_camera"].name]
                        camera=bpy.data.scenes[self.scenename].objects.get(layer["CPBatchRender Viewlayers render_camera"].name)
                        bpy.data.scenes[self.scenename].camera=camera
                except:
                    pass

                try:
                    if not bpy.data.scenes[self.scenename].CPBR_Main_Props.cp_use_scene_resolution and "CPBatchRender Viewlayers render_resolution" in layer and layer["CPBatchRender Viewlayers render_resolution"]:
                        bpy.data.scenes[self.scenename].render.resolution_x,bpy.data.scenes[self.scenename].render.resolution_y=layer["CPBatchRender Viewlayers render_resolution"]
                except:
                    pass
                   
                try:
                    if not bpy.data.scenes[self.scenename].CPBR_Main_Props.cp_use_scene_world and "CPBatchRender Viewlayers render_world" in layer and layer["CPBatchRender Viewlayers render_world"]:
                        bpy.data.scenes[self.scenename].world=layer["CPBatchRender Viewlayers render_world"]
                except:
                    pass

                break

        # 修改列表里活动视图层
        scenes = bpy.data.scenes
        for scene in scenes:
            if scene.name == self.scenename:
                for i,layer in enumerate(scene.view_layers):
                    if layer.name == self.viewlayername:
                        scene.CPBR_Main_Props.cp_active_viewlayer_index=i
                        break
        return {'FINISHED'}

renderscenename=""

render_list = []

import threading
progress = 0.0
def update_ui():
    # Force UI update
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    # if is_scanning:
    #     return 0.1  # Call every 0.1 seconds
    # else:
    return None  # Stop the timer

bugmes=''

class CPBR_OT_BatchRender(Operator):
    bl_idname = "cpbr.batch_render"
    bl_label = "Batch Render"
    bl_description = "Batch renders the selected scene and its selected viewlayers"
    #bl_options = {"REGISTER","UNDO"}#

    running = False

    # def execute(self, context):
        # scenes = bpy.data.scenes
        # global renderscenename,bugmes
        # bugmes=''
        # running = True

        # # 检查是否已保存文件
        # if not bpy.data.is_saved:
        #     self.report({'ERROR'}, "Please save the file before render!")
        #     bugmes='Please save the file before render!'
        #     return {'CANCELLED'}  # 取消操作

        # #def update_viewlayercamera():#检查视图层相机属性的相机是否是场景里的相机
        # reset_camera = []
        # for scene in scenes:
        #     scenepro=scene.CPBR_Main_Props
        #     if scenepro.cp_render_scene :
        #         if not scenepro.cp_use_scene_camera: 
        #             for layer in scene.view_layers:
        #                 # 检查属性是否存在，不存在则创建
        #                 if "CPBatchRender Viewlayers render_camera" in layer:
        #                     if layer["CPBatchRender Viewlayers render_camera"]:
        #                         pass
        #                         # cameraname = layer["CPBatchRender Viewlayers render_camera"].name
        #                         # hascamera=scene.objects.get(cameraname)
        #                         # if not hascamera:
        #                         #     reset_camera.append(f"Camera({cameraname}) not in {scene.name}\n")
        #                         #     #print(f"Camera({cameraname}) not in {scene.name}")
        #                         #     layer["CPBatchRender Viewlayers render_camera"] =  None
                               
        #                     else:
        #                         reset_camera.append(f"{scene.name}({layer.name}) no camera!\n")
        #                 else:
        #                     reset_camera.append(f"{scene.name}({layer.name}) no camera-property!\n")  
        #         else:
        #             if scene.camera is None:
        #                 reset_camera.append(f"{scene.name} no camera!\n")

        #         if not scenepro.cp_use_scene_world: 
        #             for layer in scene.view_layers:
        #                 if "CPBatchRender Viewlayers render_world" in layer:
        #                     if layer["CPBatchRender Viewlayers render_world"]:
        #                         pass
        #                     else:
        #                         reset_camera.append(f"{scene.name}({layer.name}) no world!\n")
        #                 else:
        #                     reset_camera.append(f"{scene.name}({layer.name}) no world-property!\n")  
        #         else:
        #             if scene.world is None:
        #                 reset_camera.append(f"{scene.name} no world!\n")

        #         if not scenepro.cp_use_scene_resolution: 
        #             for layer in scene.view_layers:
        #                 if "CPBatchRender Viewlayers render_resolution" not in layer:
        #                     reset_camera.append(f"{scene.name}({layer.name}) no render_resolution-property!\n")      
        
        # if reset_camera:
        #     #self.report({'ERROR'}, f"{reset_camera}")
        #     self.report({'ERROR'}, f"\n{''.join(reset_camera)}")
        #     # 将列表中的所有元素连接成一个字符串
        #     bugmes = '- '.join(reset_camera)
        #     return {'FINISHED'}

        # for window in bpy.context.window_manager.windows:
        #     # 获取当前窗口的上下文，以便安全地操作区域
        #     screen = window.screen
        #     for area in screen.areas:
        #         if area.type == 'VIEW_3D':
        #             area.spaces[0].shading.type = 'SOLID'

        # # 自动保存文件
        # bpy.ops.wm.save_mainfile()

        # # 记录当前场景和世界环境
        # original_scene = bpy.context.scene
        # original_world = original_scene.world

        # running = True

        # # r = [i for i in bpy.data.images if i.name == 'Render Result']
        # # r = r[0]
        
        # # step = 0
        # # total = len(r.render_slots)

        # # for scene in scenes:
        #     #     if scene.CPBR_Main_Props.cp_render_scene:
        #     #         bpy.context.window.scene = scene
        #     #         olduse_single_layer=scene.render.use_single_layer#
        #     #         scene.render.use_single_layer= False##关闭渲染活动视图层
        #     #         view_layers = scene.view_layers
        #     #         #try:
        #     #         r.render_slots.active_index = step
        #     #         # print(len(view_layers))
        #     #         for layer in view_layers:
        #     #             if layer.use:#启用渲染 
                            
        #     #                 context.window.view_layer = layer
        #     #         #         print(step+1)
        #     #                 renderscenename="Rendering [" + scene.name + f"]... in solt[{step+1}]"
        #     #                 print(renderscenename)
        #     #                 #renderscenename="Rendering ["+scene.name+"]`s"  
                            
        #     #                 camera=bpy.data.scenes[scene.name].objects.get(layer["CPBatchRender Viewlayers render_camera"].name)
        #     #                 bpy.data.scenes[scene.name].camera=camera

                            
        #     #                 bpy.ops.render.render(use_viewport=True, write_still=True)
        #     #                 #bpy.ops.render.render(use_viewport=True, write_still=True, layer=layer.name, scene=scene.name)
        #     #                 #'INVOKE_DEFAULT',

        #     #         step += 1
        #     #         if step>total:step = 0

        #     #         scene.render.use_single_layer=olduse_single_layer


        # # 初始化渲染列表
        # render_list = []
        # #global render_list
        # # 遍历所有场景
        # for scene in scenes:
        #     if scene.CPBR_Main_Props.cp_render_scene:
        #         # 遍历每个场景的视图层
        #         for layer in scene.view_layers:
        #             if layer.use:
        #                 if scene.CPBR_Main_Props.cp_use_scene_camera:
        #                     camera=scene.camera#用场景统一相机
        #                 else: 
        #                     # 获取相机名称
        #                     camera_name = layer["CPBatchRender Viewlayers render_camera"].name
        #                     # 从场景对象中获取相机对象
        #                     camera = bpy.data.scenes[scene.name].objects.get(camera_name)

        #                 if scene.CPBR_Main_Props.cp_use_scene_resolution:
        #                     res_x,res_y=scene.render.resolution_x,scene.render.resolution_y
        #                 else:
        #                     res_x,res_y=layer["CPBatchRender Viewlayers render_resolution"]
                            
        #                 if scene.CPBR_Main_Props.cp_use_scene_world:
        #                     world=scene.world
        #                 else:
        #                     world=layer["CPBatchRender Viewlayers render_world"]

        #                 if camera and world and res_x and res_y:
        #                     # 如果相机存在，则添加到渲染列表
        #                     #render_list.setdefault(scene.name, []).append({
        #                     # 如果相机存在，则添加到渲染列表
        #                     render_list.append({
        #                         'scene': scene,
        #                         'layer': layer,
        #                         'camera': camera,
        #                         'res_x': res_x,
        #                         'res_y': res_y,
        #                         'world': world,
        #                     })

        # # 打印渲染列表以验证结果
        # #print(render_list)
        # # # 如果渲染列表不为空，则设置场景、视图层和相机
        # if render_list:
        #     savescene=context.scene
        #         # #先检查所有场景的合成输出是否有
        #         # bad_scene = set()#集合
        #         # for entry in render_list:
        #         #     has_outnode=False
        #         #     has_layernote=False
        #         #     if bpy.data.scenes[entry['scene'].name].use_nodes:
        #         #         for node in bpy.data.scenes[entry['scene'].name].node_tree.nodes:
        #         #             if node.type=="R_LAYERS":
        #         #                 has_layernote=True
        #         #             if node.type == "OUTPUT_FILE" and node.mute==False and node.file_slots:#没有屏蔽并且有输出槽
        #         #                 # 检查该节点的输入端口是否有任意一个是有连接的
        #         #                 if any(input.is_linked for input in node.inputs):
        #         #                     has_outnode = True

        #         #     if has_outnode==False or has_layernote==False:
        #         #         #self.report({'ERROR'}, "合成里输出节点没有!")
        #         #         bad_scene.add(entry['scene'].name)#集合能避免重复添加
        #         # if bad_scene:
        #         #     self.report({'ERROR'}, f"{bad_scene}的合成树里要检查层节点/输出节点是否连接!")

        #     #检查所有场景的合成输出 上面的是简单版本，这个是详细报告具体 
        #     scene_problems = {}

        #     for entry in render_list:
        #         has_outnode = False
        #         has_layernote = False
        #         scene_name = entry['scene'].name

        #         problems = []

        #         if bpy.data.scenes[scene_name].use_nodes:
        #             for node in bpy.data.scenes[scene_name].node_tree.nodes:
        #                 if node.type == "R_LAYERS":
        #                     has_layernote = True
        #                 if node.type == "OUTPUT_FILE" and not node.mute and node.file_slots:
        #                     # 检查该节点的输入端口是否有任意一个是有连接的
        #                     if any(input.is_linked for input in node.inputs):
        #                         has_outnode = True

        #             if not has_layernote:
        #                 problems.append("Missing RenderLayers node")#缺失渲染层节点
        #             if not has_outnode:
        #                 problems.append("Missing connected and enabled output node")#缺少连接的并启用的输出节点 

        #         else:
        #             problems.append("Need use nodes in compositor")


        #         if problems:
        #             if scene_name in scene_problems:
        #                 scene_problems[scene_name].extend(problems)
        #                 scene_problems[scene_name] = list(set(scene_problems[scene_name]))
        #             else:
        #                 scene_problems[scene_name] = problems

        #     if scene_problems:#以下场景的合成树存在问题
        #         report_message = "Some issues with the composition tree in scenes：\n"
        #         for scene_name, problems in scene_problems.items():
        #             report_message += f"\n- {scene_name}: "
        #             report_message += ", ".join(problems)
                
        #         self.report({'ERROR'}, report_message)

        #         bugmes=report_message

        #         running = False
        #         renderscenename=""
        #         return {'FINISHED'}

        #     bpy.context.scene.CPBR_Main_Props.cp_batchrendering=True
        #     r = [i for i in bpy.data.images if i.name == 'Render Result']
        #     r = r[0]
        #     r.render_slots.active_index = 0
        #     #先检查渲染槽和列表数量一样才对
        #     #清空渲染槽名字
        #     for solt in r.render_slots:
        #         solt.name="Solt"#修改槽的名字
        #     step=0

        #     #鼠标显示进度
        #     wm = bpy.context.window_manager
        #     # progress from [0 - 1000]
        #     tot = len(render_list)
        #     wm.progress_begin(0, tot)
        #     # for i in range(tot):
        #     #     wm.progress_update(i)
        #     # wm.progress_end()

            
        #     for entry in render_list:
        #         i=step
        #         if step==0:
        #             i=tot/10#从10%开始显示
        #         wm.progress_update(i)
        #         r.render_slots.active_index = step#index if index<= total-1 else 0 #每个场景切换一个渲染槽就行了
                
        #         # # 设置场景
        #         # context.window.scene = entry['scene']
        #         # #bpy.data.scenes[entry['scene'].name].render.use_single_layer = True##关闭渲染活动视图层 这个没用，只有在视图里点击才有用后台用代码无用
        #         # # 设置视图层
        #         # context.window.view_layer = entry['layer']
        #         # ##把该场景里不是这个视图的层的其它视图层都取消渲染
        #         # for layer in entry['scene'].view_layers:
        #         #     if layer==entry['layer']:
        #         #         layer.use = True
        #         #     else:
        #         #         layer.use = False
                    

        #         # 设置场景相机
        #         bpy.data.scenes[entry['scene'].name].camera = entry['camera']

        #         bpy.data.scenes[entry['scene'].name].render.resolution_x = entry['res_x']
        #         bpy.data.scenes[entry['scene'].name].render.resolution_y = entry['res_y']

        #         bpy.data.scenes[entry['scene'].name].world = entry['world']

        #         # 可以在这里添加渲染逻辑或其他操作
        #         #print(r.render_slots[(int(r.render_slots.active_index))].name)
        #         r.render_slots[(int(r.render_slots.active_index))].name=entry['scene'].name + "-"+ entry['layer'].name#修改槽的名字
        #         bpy.context.view_layer.update()

        #         ##如果有启用合成就要把视图层节点里的bpy.data.scenes["sence2"].node_tree.nodes["Render Layers"].layer = 设置为对应的视图层才能保存成功，还要连接到输出节点
                
        #         if bpy.data.scenes[entry['scene'].name].use_nodes:
        #             for node in bpy.data.scenes[entry['scene'].name].node_tree.nodes:
        #                 if node.type=="R_LAYERS":
        #                     node.layer=entry['layer'].name
                        
        #         if wm.WM_CPBR_Main_Props.use_auto_blenderpath:#保存到blend文件同目录下
        #             path = Path(bpy.path.abspath('//'))  #保存到当前blender文件目录,此行定义的是base_path = path / (pr后面的path,//就代表blender文件路径
        #         else:#自定义目录
        #             path = Path(wm.WM_CPBR_Main_Props.directory)
        #         # 工程路径和blender文件名
        #         blendPath = bpy.context.blend_data.filepath
        #         blendName = bpy.path.basename(blendPath)
        #         #blendName = blendName.replace(" ", "")#替换所有空格
        #         #print("blendName",blendName)
        #         # 项目名称，'/'和'_'切换可以文件和场景名建立文件夹管理
        #         projectName = '未保存/'
        #         if  blendPath!= '':
        #             noblendname=os.path.splitext(blendName)[0]#去除.blend后缀的名字
        #             cleanblendName = noblendname.strip()#strip是Python中用于字符串处理的方法之一，去除字符串开头和结尾的空白字符（空格、制表符、换行符等
        #             #print("cleanblendName:::::::::",cleanblendName)
        #             projectName = cleanblendName + '/'        

        #         now = datetime.now()
        #         base_path = path / (projectName + entry['scene'].name  + '_'+ entry['layer'].name  + '_'+ now.strftime('%Y%m%d_%H-%M-%S'))#
                
        #         bpy.data.scenes[entry['scene'].name].render.filepath = str(base_path)
        #         if bpy.data.scenes[entry['scene'].name].use_nodes:
        #             for node in bpy.data.scenes[entry['scene'].name].node_tree.nodes:
        #                 if node.type == "OUTPUT_FILE":
        #                     node.base_path = str(base_path)
        #                     #node.base_path = str(base_path / node.name)

        #         #bpy.ops.render.render(use_viewport=True, write_still=True)#write_still是否保存属性保存面板里设置的保存
        #         bpy.ops.render.render(use_viewport=False, write_still=False, layer=entry['layer'].name, scene=entry['scene'].name)
        #         if wm.WM_CPBR_Main_Props.auto_saverendertext:
        #             renderfinishtime=datetime.now()
        #             auto_saverendertext(base_path,entry['scene'],entry['layer'],entry['camera'],entry['world'],entry['res_x'],entry['res_y'],now,renderfinishtime)



        #         step += 1
        #         if step>total:step = 0

        #         #print(f"渲染：{entry['scene'].name} /// {entry['layer'].name}")

        #     # bpy.app.handlers.render_complete.append(batchrender_blend_post_render_58683)
        #     # print(f"1渲染列表数量：{len(render_list)}")
        #     # r.render_slots.active_index = 0
        #     # #batchrender_blend_post_render_58683()
        #     # # 获取第一个键值对
        #     # first_entry = render_list[0]
            
        #     # acsolt = r.render_slots.active_index
        #     # # 处理第一个键值对
            
        #     # r.render_slots.active_index = acsolt + 1
        #     # # 设置场景
        #     # bpy.context.window.scene = first_entry['scene']
        #     # bpy.data.scenes[first_entry['scene'].name].render.use_single_layer = True  # 关闭渲染活动视图层
        #     # # 设置视图层
        #     # bpy.context.window.view_layer = first_entry['layer']
        #     # # 设置场景相机
        #     # bpy.data.scenes[first_entry['scene'].name].camera = first_entry['camera']
        #     # # 可以在这里添加渲染逻辑或其他操作
        #     # # print(r.render_slots[(int(r.render_slots.active_index))].name)
        #     # r.render_slots[(int(r.render_slots.active_index))].name = first_entry['scene'].name  # 修改槽的名字

        #     # # 删除 render_list 中的第一个项
        #     # render_list.pop(0)

        #     # bpy.ops.render.render(use_viewport=True, write_still=True)


        #     # print(f"2渲染列表数量：{len(render_list)}")    

        #     wm.progress_end()

        #     # # # 设置场景
        #     # context.window.scene = savescene

        # #render_list = {}
        # running = False
        # bpy.context.scene.CPBR_Main_Props.cp_batchrendering = False
        # #bpy.app.timers.register(update_ui)
        # renderscenename=""

        # return {'FINISHED'}

    #提前检查所有场景是否相同渲染器
    def invoke(self, context, event):
        scenes = bpy.data.scenes
        global renderscenename, bugmes
        bugmes = ''
        running = True

        # 检查是否已保存文件
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the file before render!")
            bugmes = 'Please save the file before render!'
            return {'CANCELLED'}  # 取消操作

        # 检查视图层相机属性的相机是否是场景里的相机
        reset_camera = []
        for scene in scenes:
            scenepro = scene.CPBR_Main_Props
            if scenepro.cp_render_scene:
                if not scenepro.cp_use_scene_camera:
                    for layer in scene.view_layers:
                        # 检查属性是否存在，不存在则创建
                        if "CPBatchRender Viewlayers render_camera" in layer:
                            if layer["CPBatchRender Viewlayers render_camera"]:
                                pass
                            else:
                                reset_camera.append(f"{scene.name}({layer.name}) no camera!\n")
                        else:
                            reset_camera.append(f"{scene.name}({layer.name}) no camera-property!\n")
                else:
                    if scene.camera is None:
                        reset_camera.append(f"{scene.name} no camera!\n")

                if not scenepro.cp_use_scene_world:
                    for layer in scene.view_layers:
                        if "CPBatchRender Viewlayers render_world" in layer:
                            if layer["CPBatchRender Viewlayers render_world"]:
                                pass
                            else:
                                reset_camera.append(f"{scene.name}({layer.name}) no world!\n")
                        else:
                            reset_camera.append(f"{scene.name}({layer.name}) no world-property!\n")
                else:
                    if scene.world is None:
                        reset_camera.append(f"{scene.name} no world!\n")

                if not scenepro.cp_use_scene_resolution:
                    for layer in scene.view_layers:
                        if "CPBatchRender Viewlayers render_resolution" not in layer:
                            reset_camera.append(f"{scene.name}({layer.name}) no render_resolution-property!\n")

        if reset_camera:
            self.report({'ERROR'}, f"\n{''.join(reset_camera)}")
            bugmes = '- '.join(reset_camera)
            return {'FINISHED'}

        # 记录当前场景和世界环境
        original_scene = bpy.context.scene
        original_world = original_scene.world

        running = True

        # 初始化渲染列表
        render_list = []
        # 遍历所有场景
        for scene in scenes:
            if scene.CPBR_Main_Props.cp_render_scene:
                # 遍历每个场景的视图层
                for layer in scene.view_layers:
                    if layer.use:
                        if scene.CPBR_Main_Props.cp_use_scene_camera:
                            camera = scene.camera  # 用场景统一相机
                        else:
                            # 获取相机名称
                            camera_name = layer["CPBatchRender Viewlayers render_camera"].name
                            # 从场景对象中获取相机对象
                            camera = bpy.data.scenes[scene.name].objects.get(camera_name)

                        if scene.CPBR_Main_Props.cp_use_scene_resolution:
                            res_x, res_y = scene.render.resolution_x, scene.render.resolution_y
                        else:
                            res_x, res_y = layer["CPBatchRender Viewlayers render_resolution"]

                        if scene.CPBR_Main_Props.cp_use_scene_world:
                            world = scene.world
                        else:
                            world = layer["CPBatchRender Viewlayers render_world"]

                        if camera and world and res_x and res_y:
                            # 如果相机存在，则添加到渲染列表
                            render_list.append({
                                'scene': scene,
                                'layer': layer,
                                'camera': camera,
                                'res_x': res_x,
                                'res_y': res_y,
                                'world': world,
                            })

        # 检查所有场景的合成输出
        scene_problems = {}
        render_engine = []
        # print(render_list)
        for entry in render_list:
            has_outnode = False
            has_layernote = False
            scene_name = entry['scene'].name

            problems = []

            if bpy.data.scenes[scene_name].use_nodes:
                for node in bpy.data.scenes[scene_name].node_tree.nodes:
                    if node.type == "R_LAYERS":
                        has_layernote = True
                    if node.type == "OUTPUT_FILE" and not node.mute and node.file_slots:
                        # 检查该节点的输入端口是否有任意一个是有连接的
                        if any(input.is_linked for input in node.inputs):
                            has_outnode = True

                if not has_layernote:
                    problems.append("Missing RenderLayers node")  # 缺失渲染层节点
                if not has_outnode:
                    problems.append("Missing connected and enabled output node")  # 缺少连接的并启用的输出节点

            else:
                problems.append("Need use nodes in compositor")

            if problems:
                if scene_name in scene_problems:
                    scene_problems[scene_name].extend(problems)
                    scene_problems[scene_name] = list(set(scene_problems[scene_name]))
                else:
                    scene_problems[scene_name] = problems

            # print(scene_name)
            # print(bpy.data.scenes[scene_name].render.engine)
            if bpy.data.scenes[scene_name].render.engine not in render_engine:
                render_engine.append(bpy.data.scenes[scene_name].render.engine)

        if scene_problems:  # 以下场景的合成树存在问题
            report_message = "Some issues with the composition tree in scenes：\n"
            for scene_name, problems in scene_problems.items():
                report_message += f"\n- {scene_name}: "
                report_message += ", ".join(problems)

            self.report({'ERROR'}, report_message)

            bugmes = report_message

            running = False
            renderscenename = ""
            return {'FINISHED'}

        self.render_list = render_list
        # print(render_engine)
        if len(render_engine)>1:
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=400)  #调整width参数来控制弹出面板的宽度
  
        if render_list:
            for window in bpy.context.window_manager.windows:
                # 获取当前窗口的上下文，以便安全地操作区域
                screen = window.screen
                for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        area.spaces[0].shading.type = 'SOLID'
            context.area.tag_redraw()
            # 自动保存文件
            bpy.ops.wm.save_mainfile()
            return self.execute(context)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        render_list = self.render_list
        shown_scenes = set()  # 用于记录已经显示过的场景名称
        r = layout.row(align=True)
        r.scale_y = 1.5
        r.alert = True
        r.alignment = 'CENTER'.upper()#'EXPAND', 'LEFT', 'CENTER', 'RIGHT'
        r.label(text="Use different engine for batch rendering?", icon='ERROR')
        layout.separator()
        for entry in render_list:
            scene_name = entry['scene'].name
            if scene_name not in shown_scenes:
                row = layout.row(align=True)
                row.label(text=scene_name, icon='SCENE_DATA')
                row.prop(bpy.data.scenes[scene_name].render, "engine",text="")
                row.prop(bpy.data.scenes[scene_name].cycles, "feature_set",text="")
                row.prop(bpy.data.scenes[scene_name].cycles, "device",text="")
                shown_scenes.add(scene_name)  # 将场景名称添加到集合中
        layout.separator()
        layout.separator()

    def execute(self, context):
        global renderscenename, bugmes
        bugmes = ''
        running = True

        render_list = self.render_list

        if render_list:
            savescene = context.scene

            bpy.context.scene.CPBR_Main_Props.cp_batchrendering = True
            r = [i for i in bpy.data.images if i.name == 'Render Result']
            r = r[0]
            r.render_slots.active_index = 0

            # 清空渲染槽名字
            for solt in r.render_slots:
                solt.name = "Solt"  # 修改槽的名字

            step = 0
            total = len(r.render_slots)

            # 鼠标显示进度
            wm = bpy.context.window_manager
            tot = len(render_list)
            wm.progress_begin(0, tot)

            for entry in render_list:
                i = step
                if step == 0:
                    i = tot / 10  # 从10%开始显示
                wm.progress_update(i)
                try:
                    r.render_slots.active_index = step # 每个场景切换一个渲染槽就行了
                except:
                    pass

                # 设置场景相机
                bpy.data.scenes[entry['scene'].name].camera = entry['camera']

                bpy.data.scenes[entry['scene'].name].render.resolution_x = entry['res_x']
                bpy.data.scenes[entry['scene'].name].render.resolution_y = entry['res_y']

                bpy.data.scenes[entry['scene'].name].world = entry['world']

                # 可以在这里添加渲染逻辑或其他操作
                # r.render_slots[(int(r.render_slots.active_index))].name = entry['scene'].name + "-" + entry['layer'].name  # 修改槽的名字
                bpy.context.view_layer.update()

                ## 如果有启用合成就要把视图层节点里的bpy.data.scenes["sence2"].node_tree.nodes["Render Layers"].layer = 设置为对应的视图层才能保存成功，还要连接到输出节点
                
                if bpy.data.scenes[entry['scene'].name].use_nodes:
                    for node in bpy.data.scenes[entry['scene'].name].node_tree.nodes:
                        if node.type == "R_LAYERS":
                            node.scene = bpy.data.scenes[entry['scene'].name]
                            node.layer = entry['layer'].name
                        
                if wm.WM_CPBR_Main_Props.use_auto_blenderpath:  # 保存到blend文件同目录下
                    path = Path(bpy.path.abspath('//'))  # 保存到当前blender文件目录,此行定义的是base_path = path / (pr后面的path, //就代表blender文件路径
                else:  # 自定义目录
                    path = Path(wm.WM_CPBR_Main_Props.directory)
                # 工程路径和blender文件名
                blendPath = bpy.context.blend_data.filepath
                blendName = bpy.path.basename(blendPath)
                #blendName = blendName.replace(" ", "")#替换所有空格
                #print("blendName",blendName)
                # 项目名称，'/'和'_'切换可以文件和场景名建立文件夹管理
                projectName = '未保存/'
                if  blendPath!= '':
                    noblendname=os.path.splitext(blendName)[0]#去除.blend后缀的名字
                    cleanblendName = noblendname.strip()#strip是Python中用于字符串处理的方法之一，去除字符串开头和结尾的空白字符（空格、制表符、换行符等
                    #print("cleanblendName:::::::::",cleanblendName)
                    projectName = cleanblendName + '/'        

                now = datetime.now()
                base_path = path / (projectName + entry['scene'].name  + '_'+ entry['layer'].name  + '_'+ now.strftime('%Y%m%d_%H-%M-%S'))#
                
                bpy.data.scenes[entry['scene'].name].render.filepath = str(base_path)
                if bpy.data.scenes[entry['scene'].name].use_nodes:
                    for node in bpy.data.scenes[entry['scene'].name].node_tree.nodes:
                        if node.type == "OUTPUT_FILE":
                            node.base_path = str(base_path)
                            #node.base_path = str(base_path / node.name)

                #bpy.ops.render.render(use_viewport=True, write_still=True)#write_still是否保存属性保存面板里设置的保存
                # print(entry['scene'].name)
                # for node in context.scene.node_tree.nodes:
                #     if node.type == "R_LAYERS":
                #         node.scene = bpy.data.scenes[entry['scene'].name]
                #         node.layer = entry['layer'].name

                bpy.ops.render.render(use_viewport=False, write_still=False, layer=entry['layer'].name, scene=entry['scene'].name)
                if wm.WM_CPBR_Main_Props.auto_saverendertext:
                    renderfinishtime=datetime.now()
                    auto_saverendertext(base_path,entry['scene'],entry['layer'],entry['camera'],entry['world'],entry['res_x'],entry['res_y'],now,renderfinishtime)



                step += 1
                if step>total:step = 0

                #print(f"渲染：{entry['scene'].name} /// {entry['layer'].name}")

            wm.progress_end()

        running = False
        bpy.context.scene.CPBR_Main_Props.cp_batchrendering = False
        renderscenename=""

        return {'FINISHED'}

# #保存渲染记录auto_saverendertext(base_path,entry['scene'],entry['layer'],entry['camera'],entry['world'],entry['res_x'],entry['res_y'])
def auto_saverendertext(filepath, scene, view_layer, camera, world, x, y, strattime, renderfinishtime):
    blendPath = bpy.context.blend_data.filepath
    blendName = bpy.path.basename(blendPath)
    new_filepath = os.path.dirname(filepath)
    blendname = os.path.splitext(bpy.path.basename(blendPath))[0]

    record_path = os.path.join(new_filepath, f'{blendname}_Render Record.txt')

    try:
        with open(record_path, mode='a') as file:
            lines = [
                '\n  \n ******************************************************',
                f'\n {str(strattime)}',
                f'Blender : {bpy.app.version} // {scene.render.engine}',
                f'File Name: {blendName}',
                f'Scenes: {scene.name} // ViewerLayer: {view_layer.name}',
                f'Camera: {camera.name}',
                f'World: {world.name}',
                f'Resolution: {x, y} ',
                f'Render time: {renderfinishtime - strattime}',
                '',
                'Color Space...................',
                f'Display Device : {scene.display_settings.display_device}',
                f'View Transform : {scene.view_settings.view_transform}',
                f'Look: {scene.view_settings.look}',
                f'Exposure: {scene.view_settings.exposure}',
                f'Gamma: {scene.view_settings.gamma}',
                
            ]

            if scene.render.engine == 'CYCLES':
                lines.extend([
                    f'',
                    f'Device: {scene.cycles.device}',
                    f'Sampling...................',
                    f'Adaptive Threshold: {scene.cycles.adaptive_threshold:.2f}',
                    f'Max Samples: {scene.cycles.samples}'
                ])
            elif scene.render.engine in ['BLENDER_EEVEE_NEXT','BLENDER_EEVEE']:
                lines.extend([
                    f'',
                    f'Sampling...................',
                    f'Max Samples: {scene.eevee.taa_render_samples}'
                ])

            file.write('\n'.join(lines))
    except Exception as e:
        print(f"Failed to write render record: {e}")

# import subprocess
# #渲染完后的handle
# @persistent
# def batchrender_blend_post_render_58683(dummy):
    # try:
    #     global render_list
    #     print(render_list)
    #     r = [i for i in bpy.data.images if i.name == 'Render Result']
    #     r = r[0]
    #     scenes = bpy.data.scenes
    #     step = 0
    #     total = len(r.render_slots)
    #     acsolt = r.render_slots.active_index

    #     if render_list:
    #         # 获取第一个键值对
    #         first_entry = render_list[0]
            
            
    #         r.render_slots.active_index = acsolt + 1
    #         # 设置场景
    #         bpy.context.window.scene = first_entry['scene']
    #         bpy.data.scenes[first_entry['scene'].name].render.use_single_layer = True  # 关闭渲染活动视图层
    #         # 设置视图层
    #         bpy.context.window.view_layer = first_entry['layer']
    #         # 设置场景相机
    #         bpy.data.scenes[first_entry['scene'].name].camera = first_entry['camera']
    #         # 可以在这里添加渲染逻辑或其他操作
    #         # print(r.render_slots[(int(r.render_slots.active_index))].name)
    #         r.render_slots[(int(r.render_slots.active_index))].name = first_entry['scene'].name  # 修改槽的名字

    #         # 删除 render_list 中的第一个项
    #         render_list.pop(0)

    #         bpy.ops.render.render(use_viewport=True, write_still=True)

    #     else:
    #         print("卸载hander")
    #         # 如果 autovisibility_blend_post_render 在 render_complete 处理器中
    #         bpy.app.handlers.render_complete.remove(batchrender_blend_post_render_58683)

    #     print(f"3渲染列表数量：{len(render_list)}")  
    # except Exception as err:
    #     print('-----', err, end=' | ')
    #     print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

#参考插件CamProj保存相机视图带缩略图 源自https://blenderartists.org/t/live-scene-capture-to-texture/1380153
import gpu
import numpy as np
class CPBR_OT_RenderViewport(Operator):
    bl_idname = "cpbr.render_viewport"
    bl_label = "Screenshot thumbnails for the viewlayer"
    bl_description = "Only Wireframe/Solid/Material Preview mode is supported, not render preview!"
    bl_options = {'UNDO'}

    scenename: StringProperty(name="",default="",options={'HIDDEN', 'SKIP_SAVE'})
    layername: StringProperty(name="",default="",options={'HIDDEN', 'SKIP_SAVE'})

    def get_viewlay_props(self, context,scene,layer):
        camera = world = None
        try:
            scenepro=scene.CPBR_Main_Props

            if scenepro.cp_use_scene_camera:
                if scene.camera:
                    camera=scene.camera
                else:
                    self.report({'ERROR'}, f"{scene.name} no camera!")
                    return False,camera,0,0,world
            else:
                if "CPBatchRender Viewlayers render_camera" in layer and layer["CPBatchRender Viewlayers render_camera"]:  
                    camera=scene.objects.get(layer["CPBatchRender Viewlayers render_camera"].name)
                    if not camera:
                        self.report({'ERROR'}, f"Viewlayer({layer.name}) no render_camera!")
                        return False,camera,0,0,world
                else:
                    self.report({'ERROR'}, f"Viewlayer({layer.name}) no render_camera!")
                    return False,camera,0,0,world

            x,y=scene.render.resolution_x,scene.render.resolution_y
            if not scenepro.cp_use_scene_resolution and "CPBatchRender Viewlayers render_resolution" in layer and layer["CPBatchRender Viewlayers render_resolution"]:
                x,y=layer["CPBatchRender Viewlayers render_resolution"]
            
            view = context.space_data
            
            if scenepro.cp_use_scene_world:
                if scene.world:
                    world=scene.world
                else:
                    if view.shading.type == 'MATERIAL' and view.shading.use_scene_world:#如果是eevee
                        self.report({'ERROR'}, f"{scene.name} no world!")
                        return False,camera,0,0,world
            else:
                if "CPBatchRender Viewlayers render_world" in layer and layer["CPBatchRender Viewlayers render_world"]:
                    world=layer["CPBatchRender Viewlayers render_world"]
                else:
                    if view.shading.type == 'MATERIAL' and view.shading.use_scene_world:#如果是eevee
                        self.report({'ERROR'}, f"Viewlayer({layer.name}) no render_world!")
                        return False,camera,0,0,world
        except Exception as err:
            print('-----', err, end=' | ')
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

        return True,camera,x,y,world

    def execute(self, context):
        update_viewlayercamera()#检查视图层相机属性的相机是否是场景里的相机

        scene = next((s for s in bpy.data.scenes if s.name == self.scenename), None)
        if not scene:
            return {"FINISHED"} 

        # 查找指定视图层
        layer = next((l for l in scene.view_layers if l.name == self.layername), None)
        if not layer:
            return {"FINISHED"} 

        isok,cam,x,y,world=self.get_viewlay_props(context,scene,layer)
        if not isok:
           return {"FINISHED"} 

        oldscene=context.window.scene
        oldlayer=context.window.view_layer
        context.window.scene = scene
        context.window.view_layer = layer
        scene.camera=cam
        scene.render.resolution_x,scene.render.resolution_y=x,y
        if world:
            scene.world=world


        self.set_viewlay_prop(context,None)#先检查是否有属性，并清空原图

        # x=int(layer.ResolutionX*(layer.ResolutionPercentage/100))
        # y=int(layer.ResolutionY*(layer.ResolutionPercentage/100))
        # cam = bpy.data.objects[layer.name]

        #这个是blender自带的命令是权重模式下视图菜单下的 #拍摄活动视区的快照 bpy.ops.render.opengl(animation=False, render_keyed_only=False, sequencer=False, write_still=False, view_context=True)

        offscreen = gpu.types.GPUOffScreen( x, y )
        vm = cam.matrix_world.inverted( )
        pm = cam.calc_matrix_camera( context.evaluated_depsgraph_get( ), x = x, y = y )
        offscreen.draw_view3d( context.scene, context.view_layer, context.space_data, context.region, vm, pm,do_color_management=True,draw_background=True)
        gpu.state.depth_mask_set( False )
        buffer = np.array( offscreen.texture_color.read(), dtype = 'float32' ).flatten( order = 'F' )
        buffer = np.divide( buffer, 255 ) 
        # gamma
        # buffer = buffer**0.4545
        
        name = "." + self.scenename + "-" + self.layername+ "_preview"
        image = bpy.data.images.new(
            name, width=x, height=y)
        image.pixels.foreach_set( buffer )
        image.pack()

        self.set_viewlay_prop(context,image)

        image = bpy.data.images.get(layer["CPBatchRender Viewlayers render_preview"].name)
        if image and image.preview is None:
            bpy.ops.wm.previews_clear(id_type={'IMAGE'})

        bpy.ops.cpbr.switch_scene_view_layer('INVOKE_DEFAULT', scenename=oldscene.name,viewlayername=oldlayer.name)

        return {"FINISHED"}

    # def 非简化但明白版本set_viewlay_prop(self, context,tex=None):
        # for scene in bpy.data.scenes:
        #     if scene.name==self.scenename: 
        #         for layer in scene.view_layers:
        #             if layer==self.layername:
        #                 # 检查属性是否存在，不存在则创建
        #                 if "CPBatchRender Viewlayers render_preview" in layer:
        #                     if layer["CPBatchRender Viewlayers render_preview"]:
        #                         pic=bpy.data.images.get(layer["CPBatchRender Viewlayers render_preview"].name)
        #                         if pic:
        #                             layer["CPBatchRender Viewlayers render_preview"] = None
        #                             bpy.data.images.remove(pic)
        #                     else:
        #                         if tex:#如果有新图片就设置为属性的图片
        #                             layer["CPBatchRender Viewlayers render_preview"] = tex
        #                 else:
        #                     #新建属性 
        #                     layer["CPBatchRender Viewlayers render_preview"] = None
                    

        #                 bpy.context.view_layer.update()
                        
        #                 ui = layer.id_properties_ui("CPBatchRender Viewlayers render_preview")
        #                 # 更新属性
        #                 ui.update(description=f"Viewlayers preview!")
        #                 ui.update(subtype='NONE')
        #                 ui.update(id_type='TEXTURE')

    def set_viewlay_prop(self, context, tex=None):
        # 查找指定场景
        scene = next((s for s in bpy.data.scenes if s.name == self.scenename), None)
        if not scene:
            return  # 未找到场景，直接返回

        # 查找指定视图层
        layer = next((l for l in scene.view_layers if l.name == self.layername), None)
        if not layer:
            return  # 未找到视图层，直接返回

        prop_key = "CPBatchRender Viewlayers render_preview"
        
        # 检查属性是否存在，不存在则创建
        if prop_key not in layer:
            layer[prop_key] = None
        
        # 处理属性值
        if tex:
            layer[prop_key] = tex
        else:
            if layer[prop_key]:
                pic = bpy.data.images.get(layer[prop_key].name)
                if pic:
                    layer[prop_key] = None
                    if pic.users==0:
                        bpy.data.images.remove(pic)
        

        bpy.context.view_layer.update()

        ui = layer.id_properties_ui(prop_key)
        # 更新属性
        if bpy.app.version >= (4, 2):
            ui.update(description="Viewlayers preview!")
            ui.update(subtype='NONE')
            ui.update(id_type='TEXTURE')
        else:
            ui.update(id_type='TEXTURE')
                        
def update_viewlayer_props():#检查所有场景每个视图层下是否有3个属性不用传递self
    scenes = bpy.data.scenes
    for scene in scenes:
        for vlayer in scene.view_layers:
            # 检查属性是否存在，不存在则创建
            if "CPBatchRender Viewlayers render_camera" not in vlayer:
                #vlayer["CPBatchRender Viewlayers render_camera"] = scene.camera

                vlayer["CPBatchRender Viewlayers render_camera"] = None
                if scene.camera:
                    vlayer["CPBatchRender Viewlayers render_camera"] = scene.camera

            vlayer.update()
            
            ui = vlayer.id_properties_ui("CPBatchRender Viewlayers render_camera")
            # # 更新属性
            if bpy.app.version >= (4, 2):
                ui.update(description="Viewlayers render_camera!")
                ui.update(subtype='NONE')#bpy.data.window_managers["WinMan"]. = 'DATA_BLOCK'bpy.data.window_managers["WinMan"]. = 'CAMERA'
                ui.update(id_type='OBJECT')#'CAMERA'
            else:
                ui.update(id_type='OBJECT') # 只有这个不会导致闪退，也就这个属性最重要
           
            # 检查属性是否存在，不存在则创建
            if "CPBatchRender Viewlayers render_resolution" not in vlayer:
                vlayer["CPBatchRender Viewlayers render_resolution"] = [scene.render.resolution_x,scene.render.resolution_y]
                #vlayer["CPBatchRender Viewlayers render_resolution"][1] = scene.render.resolution_y
            vlayer.update()
            
            ui = vlayer.id_properties_ui("CPBatchRender Viewlayers render_resolution")
            if bpy.app.version >= (4, 2):
                # 更新属性
                ui.update(description="Viewlayers render_resolution!")
                #ui.update(subtype='INT')
                ui.update(min=0)
                ui.update(max=999999)
            else:
                ui.update(min=0)
                ui.update(max=999999)
            

            if "CPBatchRender Viewlayers render_world" not in vlayer:
                vlayer["CPBatchRender Viewlayers render_world"] = None
                if scene.world:
                    vlayer["CPBatchRender Viewlayers render_world"] = scene.world

            vlayer.update()
            
            ui = vlayer.id_properties_ui("CPBatchRender Viewlayers render_world")
            # 更新属性
            if bpy.app.version >= (4, 2):
                ui.update(description="Viewlayers render_world!")
                ui.update(subtype='NONE')
                ui.update(id_type='WORLD')
            else:
                ui.update(id_type='WORLD')

    bpy.context.view_layer.update()

def update_viewlayercamera():#检查视图层相机属性的相机是否是场景里的相机
    pass #即使相机不在当前场景也能渲染
    # scenes = bpy.data.scenes
    # for scene in scenes:
    #     for layer in scene.view_layers:
    #         # 检查属性是否存在，不存在则创建
    #         if "CPBatchRender Viewlayers render_camera" in layer and layer["CPBatchRender Viewlayers render_camera"]:
    #             cameraname = layer["CPBatchRender Viewlayers render_camera"].name
    #             hascamera=scene.objects.get(cameraname)
    #             if not hascamera:
    #                 print(f"Camera({cameraname}) not in {scene.name}")
    #                 layer["CPBatchRender Viewlayers render_camera"] =  None

    # #清空多余的相机
    # for cam in bpy.data.cameras:
    #     if cam.users==0:
    #         bpy.data.cameras.remove(cam)


# https://blender.stackexchange.com/questions/143975/how-to-edit-a-custom-property-in-a-python-script/224284#224284

def update_cp_use_scene_camera(self, context):#检查视图层是否有自定义属性记录每个视图层的自定义相机
    scenes = bpy.data.scenes
    # c=bpy.context.scene
    for scene in scenes:
        # bpy.context.window.scene = scene
        for vlayer in scene.view_layers:
            # 检查属性是否存在，不存在则创建
            if "CPBatchRender Viewlayers render_camera" not in vlayer:
                #vlayer["CPBatchRender Viewlayers render_camera"] = scene.camera

                vlayer["CPBatchRender Viewlayers render_camera"] = None
                if scene.camera:
                    vlayer["CPBatchRender Viewlayers render_camera"] = scene.camera

            vlayer.update()# bpy.context.view_layer.update()
            
            ui = vlayer.id_properties_ui("CPBatchRender Viewlayers render_camera")
            # # 更新属性
            if bpy.app.version >= (4, 2):
                ui.update(description="Viewlayers render_camera!")
                ui.update(subtype='NONE')#bpy.data.window_managers["WinMan"]. = 'DATA_BLOCK'bpy.data.window_managers["WinMan"]. = 'CAMERA'
                ui.update(id_type='OBJECT')#'CAMERA'
                # # bpy.ops.wm.properties_edit(data_path="view_layer", property_name="CPBatchRender Viewlayers render_camera",
                #  # property_type='DATA_BLOCK', is_overridable_library=False, description="Viewlayers render_camera!", subtype='NONE', 
                #  # id_type='CAMERA', eval_string="<bpy_struct, Object(\"Camera\") at 0x0000021DF961C120>")
            else:
                # ui.update(subtype='NONE')这个会导致闪退
                ui.update(id_type='OBJECT') # 只有这个不会导致闪退，也就这个属性最重要
                # ui.update(description="Viewlayers render_camera!")这个会导致闪退
                

# blender 4.1里控制台里测试的可用的代码
# >>> ui = C.view_layer.id_properties_ui("CPBatchRender Viewlayers render_camera")
    # >>> ui.
    #        as_dict(
    #        clear(
    #        update(
    #        update_from(
    # >>> ui.update(
    # update( subtype=None, min=None, max=None, soft_min=None, soft_max=None, precision=None, step=None, default=None, id_type=None, items=None, description=None)
    # .. method:: update( subtype=None, min=None, max=None, soft_min=None, soft_max=None, precision=None, step=None, default=None, id_type=None, items=None, description=None)
    # Update the RNA information of the IDProperty used for interaction and
    # display in the user interface. The required types for many of the keyword
    # arguments depend on the type of the property.
    # >>> ui.update(id_type='OBJECT')

           
def update_cp_use_scene_resolution(self, context):# 检查视图层是否有自定义属性记录自定义分辨率
    scenes = bpy.data.scenes
    for scene in scenes:
        for vlayer in scene.view_layers:
            # 检查属性是否存在，不存在则创建
            if "CPBatchRender Viewlayers render_resolution" not in vlayer:
                vlayer["CPBatchRender Viewlayers render_resolution"] = [scene.render.resolution_x,scene.render.resolution_y]
                #vlayer["CPBatchRender Viewlayers render_resolution"][1] = scene.render.resolution_y
            vlayer.update()

            
            ui = vlayer.id_properties_ui("CPBatchRender Viewlayers render_resolution")
            if bpy.app.version >= (4, 2):
                # 更新属性
                ui.update(description="Viewlayers render_resolution!")
                #ui.update(subtype='INT')
                ui.update(min=0)
                ui.update(max=999999)
            else:
                ui.update(min=0)
                ui.update(max=999999)
                

def update_cp_use_scene_world(self, context):#检查视图层是否有自定义属性记录自定义世界环境
    scenes = bpy.data.scenes
    for scene in scenes:
        for vlayer in scene.view_layers:
            # 检查属性是否存在，不存在则创建
            if "CPBatchRender Viewlayers render_world" not in vlayer:
                vlayer["CPBatchRender Viewlayers render_world"] = None
                if scene.world:
                    vlayer["CPBatchRender Viewlayers render_world"] = scene.world

            vlayer.update()
            
            ui = vlayer.id_properties_ui("CPBatchRender Viewlayers render_world")
            # 更新属性
            if bpy.app.version >= (4, 2):
                ui.update(description="Viewlayers render_world!")
                ui.update(subtype='NONE')#bpy.data.window_managers["WinMan"]. = 'DATA_BLOCK'bpy.data.window_managers["WinMan"]. = 'CAMERA'
                ui.update(id_type='WORLD')
                # ValueError: IDPropertyUIManager.update: 'CAMERA1' not found in ('ACTION', 'ARMATURE', 'BRUSH', 'CACHEFILE', 'CAMERA', 'COLLECTION', 'CURVE', 'CURVES', 'FONT', 'GREASEPENCIL', 'GREASEPENCIL_V3', 'IMAGE', 'KEY', 'LATTICE', 'LIBRARY', 'LIGHT', 'LIGHT_PROBE', 'LINESTYLE', 'MASK', 'MATERIAL', 'MESH', 'META', 'MOVIECLIP', 'NODETREE', 'OBJECT', 'PAINTCURVE', 'PALETTE', 'PARTICLE', 'POINTCLOUD', 'SCENE', 'SCREEN', 'SOUND', 'SPEAKER', 'TEXT', 'TEXTURE', 'VOLUME', 'WINDOWMANAGER', 'WORKSPACE', 'WORLD')
            else:
                ui.update(id_type='WORLD')

           

def update_cp_render_scene(self, context):#检查所有场景每个视图层下是否有3个属性
    update_viewlayercamera()
    # update_cp_use_scene_camera(self, context)
    # update_cp_use_scene_resolution(self, context)
    # update_cp_use_scene_world(self, context)
    # bpy.context.view_layer.update()


# 添加一个标志变量来无限循环控制递归
_is_updating = False
def update_scenes_props(self, context):#设置一个场景里的保存路径后自动同步其它场景的设置
    pass
    # global _is_updating
    # if _is_updating:#避免下面修改其它场景属性后会递归调用，导致无限循环
    #     return
    
    # _is_updating = True
    # try:
    #     nowprop=context.scene.CPBR_Main_Props
    #     for scene in bpy.data.scenes:
    #         if scene != context.scene:
    #             # scene.CPBR_Main_Props.use_auto_blenderpath = nowprop.use_auto_blenderpath
    #             # scene.CPBR_Main_Props.directory=nowprop.directory
    #             # scene.CPBR_Main_Props.scale_preview=nowprop.scale_preview
    #             # scene.CPBR_Main_Props.show_all_preview=nowprop.show_all_preview 
    #             # scene.CPBR_Main_Props.auto_saverendertext=nowprop.auto_saverendertext
    # finally:
    #     _is_updating = False


# 所有场景属性汇总---------------------------------------------------- #
class Materialby_N_Colors_props(PropertyGroup):
    edit_selected_objects_colors_C1A81 :FloatVectorProperty(
        name='Color', description='Sets the property color of selected objects', 
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 
        get=get_active_object_color,
        set=set_edit_selected_objects_colors_C1A81,
        #update=update_edit_selected_objects_colors_C1A81
        )

    edit_same_color_as_active_object_B2B90 :FloatVectorProperty(
        name='Color',
        description='Edit color properties of objects with the same color property as the active object',
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=5, precision=2, 
        get=get_active_object_color,
        set=set_edit_same_color_as_active_object_B2B90,
        #update=update_active_color,
    )

    edit_selected_objects_float_C0000 :FloatProperty(
        name="Float",description="Sets the property float of selected objects",default=0.5, step=5, precision=2,  #min=0.0, max=1.0,
        get=get_active_object_float,
        set=set_edit_selected_objects_float_C0000,
        )
    
    edit_same_float_as_active_object__C0000 :FloatProperty(
        name="Float",description="Adjust the float properties of all objects that have the same float property value as the active object",default=0.5,step=3, precision=2, #min=0.0, max=1.0,
        get=get_active_object_float,
        set=set_edit_same_float_as_active_object__C0000,
        )


    ##批量渲染
        # 添加整数属性用于存储活动场景索引 改到WindowManager下，不然每个场景都不一样
        # cp_change_active_scene_index : IntProperty(name="Change Active Scene",get=get_ac_scene_list_index,
        #     set=set_ac_scene_list_index)

    cp_active_viewlayer_index : IntProperty(name="Change Active Scene")#,get=get_ac_scene_list_index,
        # set=set_ac_scene_list_index)

    zhedie:BoolProperty(name="",default=False)#列表里折叠

    cp_render_scene:BoolProperty(name="Render this scene in batch rendering",
            description="",
            default=True,
            update=update_cp_render_scene,
        )

    cp_use_scene_camera:BoolProperty(name="All viewlayers of the scene rendered by scene camera",
            description="",
            default=True,
            update=update_cp_use_scene_camera,
        )

    cp_use_scene_resolution:BoolProperty(name="All viewlayers of the scene rendered by scene resolution",
            description="",
            default=True,
            update=update_cp_use_scene_resolution,
        )

    cp_use_scene_world:BoolProperty(name="All viewlayers of the scene rendered by scene world",
            description="",
            default=True,
            update=update_cp_use_scene_world,
        )

    cp_batchrendering:BoolProperty(name="为的是阻止Auto-Filepath的自动设置渲染输出文件夹路径",
            description="",
            default=False,
        )
    #移动到WindowManager下
        # use_auto_blenderpath: BoolProperty(name="AutoblendPath",
        #                                           description="Save to the directory as blend file!",
        #                                           default=False,
        #                                           update=update_scenes_props)

        # auto_saverendertext: BoolProperty(name="Save render record",
        #                                           description="Save the rendering record to the txt file!",
        #                                           default=False,
        #                                           update=update_scenes_props)

        # directory: StringProperty(name="Batch render output paths",
        #                                     description="",
        #                                     default="C:/Blender-render",
        #                                     maxlen=4096,
        #                                     subtype="DIR_PATH",
        #                                     update=update_scenes_props
        #                                     )

        # scale_preview: FloatProperty(name="Thumbnails scale",description="Thumbnails scale",default=5.0, unit='NONE', min=1.0,update=update_scenes_props)
        # show_all_preview: BoolProperty(name="Show all thumbnails",description="",default=False,update=update_scenes_props)

    show_scene_preview: BoolProperty(name="Displays thumbnails of all view layers for that scene",description="",default=True)


class WM_Materialby_N_Colors_props(PropertyGroup):
    ##批量渲染
    # 添加整数属性用于存储活动场景索引 改到WindowManager下，不然每个场景都不一样
    cp_change_active_scene_index : IntProperty(name="Change Active Scene",get=get_ac_scene_list_index,
        set=set_ac_scene_list_index)

    use_auto_blenderpath: BoolProperty(name="AutoblendPath",
                                              description="Save to the directory as blend file!",
                                              default=False)

    auto_saverendertext: BoolProperty(name="Save render record",
                                              description="Save the rendering record to the txt file!",
                                              default=False)

    directory: StringProperty(name="Batch render output paths",
                                        description="",
                                        default="C:/Blender-render",
                                        maxlen=4096,
                                        subtype="DIR_PATH"
                                        )

    scale_preview: FloatProperty(name="Thumbnails scale",description="Thumbnails scale",default=5.0, unit='NONE', min=1.0)
    show_all_preview: BoolProperty(name="Show all thumbnails",description="",default=False)

# class Materialby_N_Colors_AddonPreferences_9F6AA(bpy.types.AddonPreferences):
    #     bl_idname = __package__

    #     #放场景属性里不对，应该放插件设置里
    #     scale_preview: FloatProperty(name="缩略图缩放",default=5.0, unit='NONE', min=1.0)
    #     show_preview: BoolProperty(name="显示全部缩略图",description="",default=False)

class TranslationHelper():
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except(ValueError):
            pass

    def unregister(self):
        bpy.app.translations.unregister(self.name)

zhdata = {
    # ----------------------------------------------------根据物体不同自动切换属性值---------------------------------------------------- #
    "Control materials by adding properties to objects/view layers,enabling the same material to automatically switch to different effects based on the object or view layer(scene).": 
    '通过给物体/视图层添加属性来控制材质,实现同一个材质根据物体或视图层(场景)自动切换不同的效果.',
    'Dynamic Material Switcher': '动态材质切换器',
    'Material by N-Objects': '根据物体切换材质',
    
    'Select all use [%s] objs': '"选中所有使用 [%s] 材质的物体"',
    'Edit prop for objs matching active obj\'s prop value': '设置与活动物体属性值相等的物体属性',
    'Edit selected obj\'s prop': '设置选中物的属性',
    'Add prop to objs using this material': '有使用该材质的物体缺失属性!',#有使用该材质的物体缺失属性
    'Add/Select Node': '添加/选中属性切换节点',
    'Material by N-Viewlayer(Scene)': '根据视图层(场景)切换材质',
    'Add node/Refresh node/Add property to viewlayer': '添加节点/刷新节点/给视图层添加属性',
    'There are multiple nodetrees with \"Viewlayer Group\" properties.they will all be automatically refreshed. Change properties of nodetrees that do not need automatic refreshing to \"Default\"': '有多个Viewlayer Group属性的节点树,它们都会被自动刷新,把不用自动刷新的节点树属性改为默认',

    'Sets the property color of selected objects': '设置所有选中物体(活动物体)的颜色属性',
    'Edit color properties of objects with the same color property as the active object': '调整所有与活动物体同色的物体颜色属性',

    'Sets the property float of selected objects': '设置所有选中物体(活动物体)的浮点属性',
    'Edit float properties of objects with the same float property as the active object': '调整所有与活动物体属性浮点值相等的物体浮点属性值',
    'Automatically add properties to each view layer in all scenes\nAdd nodes to editting tree\nRefresh properties after the view layer changes': '自动给所有场景的每个视图层添加属性\n给当前节点树添加节点\n视图层变化后刷新属性',
    'There are multiple node trees with \"Viewlayer Group\" properties in Blender! However, only one nodetree with this property can run the operation!': 'Blender里有多个Viewlayer Group属性的节点树！但只能有一个该属性的节点组才能运行操作!',
    'Select Objects with Same Attribute': '选择与活动对象属性颜色一样的物体',
    'Randomize Property': '随机化属性',
    'Randomize property on all selected objects': '随机化所有选中对象的属性',
    'Add property to all objects with this material\nAdd node': '添加一个属性节点/给所有使用该材质的物体添加属性', 

    # ----------------------------------------------------根据视图层不同自动切换属性值---------------------------------------------------- #
    'Automatically add properties to each view layer in all scenes\nAdd nodes to editting tree\nRefresh properties after the view layer changes': '自动为所有场景中的全部视图层添加属性,\n在编辑树中添加节点,\n在视图层更改后刷新属性', 
    'There are multiple node trees with \"Viewlayer Group\" properties in Blender! However, only one nodetree with this property can run the operation!': '在Blender中有多个带有“Viewlayer Group”属性的节点树！只能有一个节点树是“Viewlayer Group”属性才可以运行操作！',
    'Just one viewlayer.': '只有一个视图层运行不了!',

    # ----------------------------------------------------视图层批量渲染---------------------------------------------------- #
    'Screenshot preview': '截取预览图',
    'Viewlayers List:': '所有视图层列表:',
    'Save to BL file`s directory': '保存到BL文件目录下同名文件夹里',
    'Batch rendering is saved with the compositor\'s output node!': '批量渲染用合成器的输出节点保存!',
    'Only need one viewlayer node and one output node in compositor!': '每个场景合成器里只需一个视图层节点和输出节点!',
    'Other plugins that automatically set the path of the output node will affect the save path!': '其它能自动设置输出节点路径的插件会影响保存路径!',
    'Switch Scene and ViewLayer': '切换场景和视图层',
    'Batch Render': '批量渲染',
    'Batch renders the selected scene and its selected viewlayers': '批量渲染勾选的场景和其勾选的视图层',
    'Please save the file before render!': '要先保存Blend文件！',
    'Screenshot thumbnails for the viewlayer': '以当前着色模式为视图层截取缩略图',
    'Only Wireframe/Solid/Material Preview mode is supported, not render preview!': '不支持渲染模式下的截图，其它三种支持',
    
    'Open Save Folder': '打开渲染文件夹',
    'Use different engine for batch rendering?': '你确定要用不同的渲染器来批量渲染么!',
    'Render this scene in batch rendering': '是否在批量渲染中渲染该场景',
    'All viewlayers of the scene rendered by scene camera': '该场景的所有视图层统一使用场景相机渲染',
    'All viewlayers of the scene rendered by scene resolution': '该场景的所有视图层统一使用场景分辨率',
    'All viewlayers of the scene rendered by scene world': '该场景的所有视图层统一使用场景世界环境',
    'Save to the directory as blend file!': '保存到blender同目录下!',
    'Save render record': '保存渲染记录',
    'Save the rendering record to the txt file!': '保存渲染记录到txt文件里,txt在渲染保存的位置下',
    'Batch render output paths': '批量渲染输出路径',
    'Thumbnails scale': '缩略图尺寸',
    'Show all thumbnails': '显示全部缩略图',
    'Displays thumbnails of all view layers for that scene': '显示该场景的所有视图层缩略图',
}

CPBRender_zh_HANS = TranslationHelper('CPBRender_zh_HANS', zhdata, lang='zh_HANS')

classes = (
    NODE_OT_Add_Prop_Attributenode_285D0,
    MNC_OT_randomize_property,
    #SNA_OT_Operator001_D53F7,
    SNA_OT_SelectObjectsWithSameAttribute,
    SNA_PT_MATERIAL_BY_NCOLORS_85AF2,

    Materialby_N_Colors_props,##所有场景属性汇总

    # NODE_OT_Add_Prop_Node_To_Scene,
    # SNA_PT_MATERIAL_BY_NScene_85AF2,

    NODE_OT_Add_Prop_Node_To_Viewlayer,
    #SNA_PT_MATERIAL_BY_Nviewlayer_85AF2,

    CPBR_UL_viewlayer_list,
    CPBR_UL_scenes_list,
    CPBR_PT_UIListPanel,
    CPBR_OT_SwitchSceneViewLayer,
    CPBR_OT_BatchRender,
    CPBR_OT_RenderViewport,
    WM_Materialby_N_Colors_props,
    #Materialby_N_Colors_AddonPreferences_9F6AA,
    
)
  

def register():
    if bpy.app.version < (4, 0, 0):
        print('Only Blender 4.0 and later versions are supported')
        return
    for cls in classes:
        bpy.utils.register_class(cls)

    ##注意这个要在所有class注册后，也就是它的type注册后再注册这个 所有场景属性汇总
    bpy.types.Scene.CPBR_Main_Props = bpy.props.PointerProperty(name = "CPBR main prop",type=Materialby_N_Colors_props)

    bpy.types.NodeTree.Matby_N_Colors_type = EnumProperty( #先留着备用,这个属性可以在模板bl文件里直接先给到节点树
        items=[
            ('Default', 'Default', ''),
            #('Scene Prop', 'Scene Prop Group', ''),
            ('Viewlayer Prop', 'Viewlayer Group', ''),    
        ],
        name="CPBR NodeTree Type",
        description="Do not modify this property manually, it is automatically generated",
        default="Default",
        )

    bpy.types.WindowManager.WM_CPBR_Main_Props = bpy.props.PointerProperty(name='New Property', description='', type=WM_Materialby_N_Colors_props)

    #bpy.app.translations.register(__name__, langs)
    CPBRender_zh_HANS.register()

def unregister():
    for cls in reversed(classes):#自定义工具图标
        bpy.utils.unregister_class(cls)#先注销这个

    del bpy.types.Scene.CPBR_Main_Props
    del bpy.types.NodeTree.Matby_N_Colors_type
    #bpy.app.translations.unregister(__name__)

    del bpy.types.WindowManager.WM_CPBR_Main_Props

    CPBRender_zh_HANS.unregister()

    
if __name__ == "__main__":
    register()