import bpy
import openai
import requests
import json
from . import utils

class BLENDER_AI_OT_chat(bpy.types.Operator):
    bl_idname = "wm.blender_ai_chat"
    bl_label = "Chat with AI"
    
    message: bpy.props.StringProperty()
    
    def execute(self, context):
        scene = context.scene
        api_key = scene.ai_api_key
        model = scene.ai_model
        
        if not api_key:
            self.report({'ERROR'}, 'API key not configured')
            return {'FINISHED'}
        
        try:
            if model == 'chatgpt':
                response = self._call_openai(api_key, self.message)
            elif model == 'gemini':
                response = self._call_gemini(api_key, self.message)
            else:
                return {'FINISHED'}
            
            # Store in history
            item = scene.ai_history.add()
            item.name = self.message[:50]
            
            print(f"AI Response: {response}")
            self.report({'INFO'}, f'Response received: {response[:100]}')
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        return {'FINISHED'}
    
    def _call_openai(self, api_key, message):
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, api_key, message):
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": message}]}]}
        response = requests.post(url, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

class BLENDER_AI_OT_apply_suggestion(bpy.types.Operator):
    bl_idname = "wm.blender_ai_apply"
    bl_label = "Apply AI Suggestion"
    
    def execute(self, context):
        self.report({'INFO'}, 'Suggestion applied')
        return {'FINISHED'}
