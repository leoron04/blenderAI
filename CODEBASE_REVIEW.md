# BlenderAI Codebase Review & Roadmap

This document outlines the architectural review, identified improvements, and future roadmap for the **BlenderAI** addon.

## 🌟 Strengths
1. **Modular Architecture**: The codebase is well organized into modules (`ui.py`, `operators.py`, `agent.py`, `scene_analyzer.py`), allowing for easy testing and scalability.
2. **Multi-Provider & Fallback System**: The system in `ai_providers.py` handles Claude, GPT-4, and Gemini with an ensemble/fallback mechanism that makes it robust.
3. **Integrated RAG System**: Including vector embeddings of Blender's official documentation (`blender_docs_manager.py` and `rag_system.py`) drastically reduces AI hallucinations regarding API usage (especially useful for Blender's frequently changing API).
4. **Caching & Optimization**: Using a semantic cache and ensemble voting reduces token costs and improves response quality over time.

## 🛠️ Architectural Improvements (Implemented & Planned)
1. **Test Suite Fixes (Implemented)**:
   - Mocking objects, armatures, and context layouts (`tests/conftest.py` and `tests/test_ui.py`) has been fixed to ensure tests pass in non-Blender CI environments.
2. **Cross-Platform Paths (Implemented)**:
   - Hardcoded paths like `~/.config/blender_ai/` have been refactored. We now use a central `utils.get_config_dir()` which utilizes Blender's native `bpy.utils.user_resource('CONFIG')`. This guarantees the addon works perfectly on Windows (`AppData\Roaming\...`), macOS, and Linux out-of-the-box.
3. **Async Network Requests (Planned)**:
   - *Current issue*: `requests.post()` is synchronous, causing the entire Blender UI to freeze while waiting for an AI response.
   - *Solution*: Use Python threads or `asyncio` coupled with a modal timer operator (`modal()`) to run network requests in the background, updating the UI safely when the response is ready.
4. **Security `exec()` (Planned)**:
   - AI-generated code is executed via `exec()`. To improve security, we should implement a strict AST parser (`ast.parse`) in `security_hardening.py` to block unauthorized module imports (e.g., `os`, `sys`, `subprocess`) before execution.

## 🚀 New Features Roadmap
1. **Vision Capabilities (Screenshot Context)**:
   - Exploit vision-capable models (GPT-4o, Claude 3.5 Sonnet) by using `bpy.ops.screen.screenshot` to capture the 3D viewport. The image can be sent alongside the prompt to ask context-aware questions (e.g., *"How can I improve this lighting?"*).
2. **Real Auto-Rigging**:
   - Integrate the currently stubbed `BLENDER_AI_OT_auto_rig` with Rigify or create a real bone mapping for humanoid meshes automatically.
3. **Native Undo System**:
   - When the agent executes a script, group all operations into a single undo step using `bpy.ops.ed.undo_push(message="AI Generation")`. This allows users to press `Ctrl+Z` to safely revert unwanted AI changes.
4. **Node Graph Optimization**:
   - Provide visual analysis for Geometry Nodes and Shader Nodes, suggesting structural optimizations, removal of disconnected nodes, or mathematical simplifications.

---
*Created during an automated codebase audit.*
