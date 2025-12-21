import bpy

class BLENDER_AI_PT_panel(bpy.types.Panel):
    bl_label = "BlenderAI Assistant"
    bl_idname = "BLENDER_AI_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BlenderAI"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # API Configuration
        layout.label(text="API Configuration", icon='PREFERENCES')
        layout.prop(scene, "ai_model", text="Model")
        layout.prop(scene, "ai_api_key", text="API Key")
        
        # Chat Input
        layout.label(text="Chat with AI", icon='COMMENT')
        row = layout.row()
        row.prop(scene, "ai_api_key", text="")
        
        layout.label(text="Ask anything about:")
        layout.label(text="- 3D Modeling", icon='CUBE')
        layout.label(text="- Animation", icon='ANIM')
        layout.label(text="- VFX & Compositing", icon='NODETREE')
        
        # Quick Commands
        layout.label(text="Quick Commands")
        layout.operator("wm.blender_ai_chat")
        layout.operator("wm.blender_ai_apply")
        
        # History
        layout.label(text="Chat History")
        for item in scene.ai_history:
            layout.label(text=item.name, icon='TEXT')
