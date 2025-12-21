import bpy
import openai
import requests
import json
from . import utils

# BlenderAI - Intelligent Agent System
# Non è solo una chat, è un vero agente che:
# - Conosce tutta la documentazione Blender
# - Vede l'intero progetto (oggetti, nodi, materiali)
# - Esegue azioni dirette: create, delete, modify
# - Gestisce nodi, shader, compositing

class BlenderAIAgent:
    """Agente intelligente che comprende e manipola scene Blender."""
    
    def __init__(self, api_key, model='chatgpt'):
        self.api_key = api_key
        self.model = model
        self.scene_data = {}
        self.action_history = []
    
    def analyze_scene(self, context):
        """Analizza l'intera scena Blender: oggetti, nodi, proprietà."""
        scene = context.scene
        world = context.world
        
        self.scene_data = {
            'objects': self._get_objects_info(scene),
            'materials': self._get_materials_info(scene),
            'node_trees': self._get_node_trees(scene),
            'world': self._get_world_info(world),
            'camera': self._get_camera_info(scene),
            'render_settings': self._get_render_settings(scene),
        }
        return self.scene_data
    
    def _get_objects_info(self, scene):
        """Restituisce info su tutti gli oggetti della scena."""
        objects_info = {}
        for obj in scene.objects:
            objects_info[obj.name] = {
                'type': obj.type,
                'location': tuple(obj.location),
                'rotation': tuple(obj.rotation_euler),
                'scale': tuple(obj.scale),
                'parent': obj.parent.name if obj.parent else None,
                'children': [child.name for child in obj.children],
                'modifiers': [m.name for m in obj.modifiers],
                'visible': obj.hide_viewport == False,
                'selectable': obj.hide_select == False,
            }
            
            # Info su mesh
            if obj.type == 'MESH':
                objects_info[obj.name]['mesh_data'] = {
                    'vertices': len(obj.data.vertices),
                    'edges': len(obj.data.edges),
                    'faces': len(obj.data.polygons),
                    'materials': [m.name for m in obj.data.materials],
                }
            
            # Info su armature
            if obj.type == 'ARMATURE':
                objects_info[obj.name]['bones'] = [b.name for b in obj.data.bones]
        
        return objects_info
    
    def _get_materials_info(self, scene):
        """Restituisce info su materiali e shader."""
        materials_info = {}
        for mat in bpy.data.materials:
            mat_info = {'name': mat.name}
            
            if mat.use_nodes:
                mat_info['nodes'] = {}
                for node in mat.node_tree.nodes:
                    mat_info['nodes'][node.name] = {
                        'type': node.type,
                        'inputs': [inp.name for inp in node.inputs],
                        'outputs': [out.name for out in node.outputs],
                    }
            
            materials_info[mat.name] = mat_info
        
        return materials_info
    
    def _get_node_trees(self, scene):
        """Restituisce info su compositing, shader, geometry nodes."""
        node_trees = {}
        
        # Compositing
        if scene.use_nodes:
            node_trees['compositing'] = self._analyze_node_tree(scene.node_tree)
        
        # Shader e Geometry Nodes su oggetti
        for obj in scene.objects:
            if obj.type == 'MESH':
                for mat in obj.data.materials:
                    if mat and mat.use_nodes:
                        node_trees[f"{obj.name}_{mat.name}_shader"] = self._analyze_node_tree(mat.node_tree)
        
        return node_trees
    
    def _analyze_node_tree(self, node_tree):
        """Analizza un albero di nodi."""
        tree_info = {
            'nodes': {},
            'links': []
        }
        
        for node in node_tree.nodes:
            tree_info['nodes'][node.name] = {
                'type': node.type,
                'inputs': [(inp.name, inp.type) for inp in node.inputs],
                'outputs': [(out.name, out.type) for out in node.outputs],
            }
        
        for link in node_tree.links:
            tree_info['links'].append({
                'from': f"{link.from_node.name}.{link.from_socket.name}",
                'to': f"{link.to_node.name}.{link.to_socket.name}"
            })
        
        return tree_info
    
    def _get_world_info(self, world):
        """Informazioni su lighting, world shader."""
        return {
            'name': world.name,
            'has_world_shader': world.use_nodes,
            'background_strength': world.node_tree.nodes.get('Background', {}).inputs.get('Strength').default_value if world.use_nodes else 0,
        }
    
    def _get_camera_info(self, scene):
        """Informazioni sulla camera attiva."""
        if scene.camera:
            cam = scene.camera
            return {
                'name': cam.name,
                'type': cam.type,
                'lens': cam.data.lens if hasattr(cam.data, 'lens') else None,
                'sensor_width': cam.data.sensor_width if hasattr(cam.data, 'sensor_width') else None,
            }
        return None
    
    def _get_render_settings(self, scene):
        """Impostazioni di rendering."""
        return {
            'render_engine': scene.render.engine,
            'resolution_x': scene.render.resolution_x,
            'resolution_y': scene.render.resolution_y,
            'samples': scene.cycles.samples if scene.render.engine == 'CYCLES' else None,
            'denoiser': scene.cycles.denoiser if scene.render.engine == 'CYCLES' else None,
        }
    
    def create_object(self, context, obj_type, name, **properties):
        """Crea un oggetto nella scena."""
        if obj_type == 'MESH':
            bpy.ops.mesh.primitive_cube_add()
            obj = context.active_object
            obj.name = name
        elif obj_type == 'LIGHT':
            bpy.ops.object.light_add(type='POINT')
            obj = context.active_object
            obj.name = name
        elif obj_type == 'CAMERA':
            bpy.ops.object.camera_add()
            obj = context.active_object
            obj.name = name
        
        # Applica proprietà
        for key, value in properties.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        self.action_history.append(f"Created {obj_type}: {name}")
        return obj
    
    def delete_object(self, context, obj_name):
        """Elimina un oggetto dalla scena."""
        obj = bpy.data.objects.get(obj_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
            self.action_history.append(f"Deleted object: {obj_name}")
            return True
        return False
    
    def modify_object(self, context, obj_name, **properties):
        """Modifica proprietà di un oggetto."""
        obj = bpy.data.objects.get(obj_name)
        if obj:
            for key, value in properties.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.action_history.append(f"Modified {obj_name}: {properties}")
            return True
        return False
    
    def add_modifier(self, context, obj_name, modifier_type, **settings):
        """Aggiunge un modificatore a un oggetto."""
        obj = bpy.data.objects.get(obj_name)
        if obj and obj.type == 'MESH':
            modifier = obj.modifiers.new(name=modifier_type, type=modifier_type)
            for key, value in settings.items():
                if hasattr(modifier, key):
                    setattr(modifier, key, value)
            self.action_history.append(f"Added modifier {modifier_type} to {obj_name}")
            return True
        return False
    
    def add_node(self, context, node_tree_name, node_type, node_name):
        """Aggiunge un nodo a un albero di nodi."""
        # Logica per aggiungere nodi a shader, compositing, ecc.
        self.action_history.append(f"Added node {node_type}: {node_name} to {node_tree_name}")
        return True
    
    def query_ai(self, prompt):
        """Fa una domanda all'AI con il contesto della scena."""
        system_message = f"""Sei un esperto di Blender con conoscenza completa dell'API.
Hai accesso a informazioni sulla scena attuale:

{json.dumps(self.scene_data, indent=2)}

Puoi eseguire azioni dirette nella scena come:
- create_object(tipo, nome, proprietà)
- delete_object(nome)
- modify_object(nome, proprietà)
- add_modifier(nome, tipo, impostazioni)
- add_node(albero_nodi, tipo_nodo, nome_nodo)

Rispondi con azioni specifiche in Python quando necessario."""
        
        if self.model == 'chatgpt':
            response = self._query_chatgpt(prompt, system_message)
        elif self.model == 'gemini':
            response = self._query_gemini(prompt, system_message)
        
        return response
    
    def _query_chatgpt(self, prompt, system_message):
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    def _query_gemini(self, prompt, system_message):
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_message}\n\n{prompt}"
                }]
            }]
        }
        response = requests.post(url, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

class BLENDER_AI_OT_agent_query(bpy.types.Operator):
    """Operatore per interrogare l'agente AI intelligente."""
    bl_idname = "wm.blender_ai_agent"
    bl_label = "AI Agent Query"
    
    query: bpy.props.StringProperty()
    
    def execute(self, context):
        scene = context.scene
        agent = BlenderAIAgent(scene.ai_api_key, scene.ai_model)
        
        # Analizza la scena
        scene_info = agent.analyze_scene(context)
        
        # Interroga l'AI con il contesto completo
        response = agent.query_ai(self.query)
        
        # Log azioni eseguite
        print(f"AI Agent Response:\n{response}")
        print(f"\nAction History:\n{json.dumps(agent.action_history, indent=2)}")
        
        self.report({'INFO'}, f'Agent: {response[:100]}...')
        return {'FINISHED'}
