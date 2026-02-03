"""Advanced Node Graph Integration with AI optimization."""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import bpy
import json
from pathlib import Path

class NodeGraphAnalyzer:
    """Analyze and optimize node graphs with AI."""
    
    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene
        self.materials = [m for m in bpy.data.materials if m.use_nodes]
        self.cache_dir = Path.home() / ".config" / "blender_ai" / "node_graphs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_material_nodes(self, material: bpy.types.Material) -> Dict[str, Any]:
        """Deep analysis of material node graph."""
        if not material.use_nodes or not material.node_tree:
            return {"error": "Material has no node tree"}
        
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        node_types = {}
        for node in nodes:
            node_type = node.bl_idname
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Performance metrics
        heavy_nodes = {}
        for node in nodes:
            if 'Texture' in node.bl_idname or 'Image' in node.bl_idname:
                heavy_nodes[node.name] = node.bl_idname
        
        return {
            "name": material.name,
            "total_nodes": len(nodes),
            "total_links": len(links),
            "node_types": node_types,
            "heavy_nodes": heavy_nodes,
            "orphaned_nodes": self._find_orphaned_nodes(nodes, links),
            "complexity_score": self._calculate_complexity(nodes, links),
        }
    
    def _find_orphaned_nodes(self, nodes, links) -> List[str]:
        """Find nodes with no connections."""
        connected = set()
        for link in links:
            connected.add(link.from_node.name)
            connected.add(link.to_node.name)
        
        return [n.name for n in nodes if n.name not in connected and n.bl_idname != 'NodeGroupInput' and n.bl_idname != 'NodeGroupOutput']
    
    def _calculate_complexity(self, nodes, links) -> float:
        """Calculate node graph complexity score (0-100)."""
        if not nodes:
            return 0.0
        
        node_count_score = min(100, (len(nodes) / 50) * 100)
        link_density = len(links) / max(len(nodes), 1)
        density_score = min(100, (link_density / 3) * 100)
        
        return (node_count_score + density_score) / 2
    
    def generate_optimization_suggestions(self, analysis: Dict) -> List[str]:
        """Generate AI optimization suggestions based on analysis."""
        suggestions = []
        
        if analysis.get("total_nodes", 0) > 50:
            suggestions.append("Consider using node groups to organize complex shader logic.")
        
        if analysis.get("orphaned_nodes"):
            suggestions.append(f"Found {len(analysis['orphaned_nodes'])} orphaned nodes - consider removing them.")
        
        if len(analysis.get("heavy_nodes", {})) > 3:
            suggestions.append("High number of texture nodes detected - consider baking or using displacement maps.")
        
        complexity = analysis.get("complexity_score", 0)
        if complexity > 70:
            suggestions.append("Graph complexity is high - consider optimization for better performance.")
        
        if not suggestions:
            suggestions.append("Node graph is well-optimized.")
        
        return suggestions
    
    def build_full_analysis(self) -> Dict[str, Any]:
        """Build complete node graph analysis for all materials."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_materials": len(self.materials),
            "materials": {},
            "overall_suggestions": []
        }
        
        for material in self.materials:
            mat_analysis = self.analyze_material_nodes(material)
            if "error" not in mat_analysis:
                analysis["materials"][material.name] = mat_analysis
                suggestions = self.generate_optimization_suggestions(mat_analysis)
                analysis["materials"][material.name]["suggestions"] = suggestions
        
        return analysis
    
    def cache_analysis(self, analysis: Dict) -> Path:
        """Cache analysis results."""
        cache_file = self.cache_dir / "latest_analysis.json"
        with open(cache_file, "w") as f:
            json.dump(analysis, f, indent=2)
        return cache_file


class BLENDER_AI_OT_analyze_node_graph(bpy.types.Operator):
    """Deep analysis of scene node graphs."""
    bl_idname = "blender_ai.analyze_node_graph"
    bl_label = "Analyze Node Graph"
    
    def execute(self, context):
        scene = context.scene
        analyzer = NodeGraphAnalyzer(scene)
        analysis = analyzer.build_full_analysis()
        
        # Store analysis in scene
        scene["node_graph_analysis"] = analysis
        
        # Cache for later use
        analyzer.cache_analysis(analysis)
        
        msg = f"Analyzed {analysis['total_materials']} materials with node graphs."
        self.report({"INFO"}, msg)
        return {"FINISHED"}


class BLENDER_AI_PT_advanced_node_graph(bpy.types.Panel):
    """Advanced Node Graph Integration Panel."""
    bl_label = "🧮 Advanced Node Graph"
    bl_idname = "BLENDER_AI_PT_advanced_node_graph"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Analysis button
        layout.operator(BLENDER_AI_OT_analyze_node_graph.bl_idname, icon="NODE_MATERIAL")
        
        # Results display
        if "node_graph_analysis" in scene:
            analysis = scene["node_graph_analysis"]
            box = layout.box()
            box.label(text=f"Materials Analyzed: {analysis.get('total_materials', 0)}", icon="INFO")
            
            for mat_name, mat_data in analysis.get("materials", {}).items():
                mat_box = layout.box()
                mat_box.label(text=mat_name, icon="MATERIAL")
                mat_box.label(text=f"Nodes: {mat_data.get('total_nodes', 0)} | Links: {mat_data.get('total_links', 0)}")
                mat_box.label(text=f"Complexity: {mat_data.get('complexity_score', 0):.1f}/100")
                
                for suggestion in mat_data.get("suggestions", [])[:2]:  # Show top 2
                    mat_box.label(text=f"• {suggestion}", icon="QUESTION")


classes = (
    BLENDER_AI_OT_analyze_node_graph,
    BLENDER_AI_PT_advanced_node_graph,
)
