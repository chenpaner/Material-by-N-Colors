
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


import bpy
import math
import random
from bpy.app.handlers import persistent

##插件PowerProps值得参考

#todo 在顶部放一个活动物体的所有自定义属性的枚举，然后设置这个名的属性，这样可以为一个物体有多个材质solt都要用不同颜色的属性新建多个自定义属性

class NODE_OT_Add_Prop_Attributenode_285D0(bpy.types.Operator):
    bl_idname = "node.add_prop_and_attributenode_285d0"
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
                obj["CP Custom colors"]= bpy.context.scene.edit_selected_objects_colors_C1A81#(1.0, 1.0, 1.0, 1.0)
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
                obj["CP Custom float"]= bpy.context.scene.edit_selected_objects_float_C0000
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

        
        return {"FINISHED"}

#todo 按某个色库里的颜色随机化颜色值
class MNC_OT_randomize_property(bpy.types.Operator):
    bl_idname = 'mnc.randomize_property'
    bl_label = 'Randomize Property'
    bl_description = 'Randomize property on all selected objects\n随机化所有选中对象的属性'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    prop_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    seed: bpy.props.IntProperty(name='Seed', description='Seed for the random number generator')

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
                    r = round(rand.uniform(min_val, max_val), 2)
                    g = round(rand.uniform(min_val, max_val), 2)
                    b = round(rand.uniform(min_val, max_val), 2)
                    a = 1.0  # 设为固定值，若需要随机化可以解除注释
                    #print(r, g, b, a)
                    obj[self.prop_name]=(r, g, b, a)
                    obj.data.update()

                elif self.prop_name == "CP Custom float":
                    f = round(rand.uniform(min_val, max_val), 2)
                    #print(f)
                    obj[self.prop_name]= f
                    obj.data.update()

        return {'FINISHED'}

# class SNA_OT_Operator001_D53F7(bpy.types.Operator):
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

class SNA_OT_SelectObjectsWithSameAttribute(bpy.types.Operator):
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
        # 检查是否存在节点树以及其他必要条件
        if data and data.tree_type == "ShaderNodeTree" and data.edit_tree:
            # 检查当前节点树是否不同于世界节点树
            if data.node_tree and data.node_tree != world.node_tree:
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
            row_3835D.prop(bpy.context.scene, 'edit_same_color_as_active_object_B2B90', text='', icon_value=0, emboss=True)
            #row_3835D.label(text='选择和活动物体一样材质，并且属性的颜色一样的物体', icon_value=256)
            row_3835D.operator('sna.select_same_attribute', text='', icon_value=256, emboss=True, depress=False)

            co.prop(bpy.context.scene, 'edit_same_float_as_active_object__C0000', text='Float', icon_value=0, emboss=True)

            box_CCCCC = layout.box()
            col=box_CCCCC.column(align=True, heading='', heading_ctxt='', translate=True)
            col.label(text='设置所有选中物体(活动物体)属性', icon="STICKY_UVS_LOC")
            row_D = col.row(heading='', align=False)
            row_D.prop(bpy.context.scene, 'edit_selected_objects_colors_C1A81', text='', icon_value=0, emboss=True)
            op=row_D.operator('mnc.randomize_property', text='', icon="MOD_NOISE", emboss=True, depress=False)
            op.prop_name="CP Custom colors"

            row_E = col.row(heading='', align=False)
            row_E.prop(bpy.context.scene, 'edit_selected_objects_float_C0000', text='Float', icon_value=0, emboss=True)
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

        row.operator('node.add_prop_and_attributenode_285d0', text=tex, icon=icon, emboss=True, depress=False)
        #少个选中所有使用该材质的物体操作符
 
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

def register():
    bpy.types.Scene.edit_selected_objects_colors_C1A81 = bpy.props.FloatVectorProperty(
        name='Sets the property color of all selected objects', description='设置所有选中物体(活动物体)的属性颜色', 
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=2, 
        get=get_active_object_color,
        set=set_edit_selected_objects_colors_C1A81,
        #update=update_edit_selected_objects_colors_C1A81
        )

    bpy.types.Scene.edit_same_color_as_active_object_B2B90 = bpy.props.FloatVectorProperty(
        name='Also adjust the attribute color of the same attribute color as the active object',
        description='调整与活动物体同色的物体属性颜色',
        size=4, default=(1.0, 1.0, 1.0, 1.0), subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=5, precision=2, 
        get=get_active_object_color,
        set=set_edit_same_color_as_active_object_B2B90,
        #update=update_active_color,
    )

    bpy.types.Scene.edit_selected_objects_float_C0000 = bpy.props.FloatProperty(
        name="Float",description="Edit selected objects float",default=0.5,min=0.0, max=1.0, step=5, precision=2,
        get=get_active_object_float,
        set=set_edit_selected_objects_float_C0000,
        )
    
    bpy.types.Scene.edit_same_float_as_active_object__C0000 = bpy.props.FloatProperty(
        name="Float",description="Edit same float as active object",default=0.5,min=0.0, max=1.0, step=3, precision=2,
        get=get_active_object_float,
        set=set_edit_same_float_as_active_object__C0000,
        )

    #bpy.app.handlers.depsgraph_update_post.append(get_edit_same_color_as_active_object_B2B90)#多余了用get了

    #bpy.types.Scene.shoud_refresh_color = bpy.props.BoolProperty(name = "", description = "", default = False)

    bpy.utils.register_class(NODE_OT_Add_Prop_Attributenode_285D0)
    bpy.utils.register_class(MNC_OT_randomize_property)
    #bpy.utils.register_class(SNA_OT_Operator001_D53F7)
    bpy.utils.register_class(SNA_OT_SelectObjectsWithSameAttribute)

    bpy.utils.register_class(SNA_PT_MATERIAL_BY_NCOLORS_85AF2)


def unregister():
    del bpy.types.Scene.edit_selected_objects_colors_C1A81
    del bpy.types.Scene.edit_same_color_as_active_object_B2B90
    del bpy.types.Scene.edit_selected_objects_float_C0000
    del bpy.types.Scene.edit_same_float_as_active_object__C0000
    #bpy.app.handlers.depsgraph_update_post.remove(get_edit_same_color_as_active_object_B2B90)

    #del bpy.types.Scene.shoud_refresh_color
    bpy.utils.unregister_class(NODE_OT_Add_Prop_Attributenode_285D0)
    bpy.utils.unregister_class(MNC_OT_randomize_property)
    bpy.utils.unregister_class(SNA_OT_SelectObjectsWithSameAttribute)

    bpy.utils.unregister_class(SNA_PT_MATERIAL_BY_NCOLORS_85AF2)

if __name__ == "__main__":
    register()