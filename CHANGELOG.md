# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Intelligent Agent v2: analisi scena avanzata, cache locale e fallback multi-provider (Claude > GPT-4 > Gemini).
- Nuovi pannelli UI (Scene Inspector, AI Suggestions, Code Generator) con preview side-by-side codice + descrizione.
- Operatori autonomi sicuri (stub) per materiali, illuminazione, geometria e auto-rig placeholder.
- Logging e configurazione estesa (API keys multiple, temperature, modello prioritario).

## [1.0.0] - 2025-12-21

### Added
- **BlenderAI Agent System**: Complete intelligent agent for Blender scene analysis
- **Scene Analysis**: Full project introspection (objects, materials, nodes, shaders)
- **Autonomous Actions**: Create, delete, modify objects and add modifiers
- **Node Management**: Shader, compositor, and geometry nodes manipulation
- **AI Integration**: ChatGPT (GPT-4) and Google Gemini support
- **Action History**: Track all modifications made by the agent
- **UI Panel**: Blender 3D View panel for agent interaction
- **Configuration System**: Environment-based API key management
- **Documentation**: Complete README, contributing guidelines, and examples
- **MIT License**: Open source licensing

### Features
- Real-time scene analysis with complete data extraction
- Multi-model AI support (ChatGPT, Gemini)
- Direct scene manipulation through Python API
- Material and shader node analysis
- Render settings introspection
- Camera and world lighting information
- Comprehensive error handling and logging

### Technical Details
- Python 3.10+ compatible
- Blender 3.0+ addon format
- Modular code architecture
- Extensive API documentation
- Production-ready code quality

## Planned Features

### v1.1.0
- Advanced node generation with automatic connections
- Material preview system
- Animation assistant
- VFX template library
- Performance optimization

### v1.2.0
- Multi-language support
- Custom model integration
- Batch operations
- Scene versioning
- Collaborative features

### v2.0.0
- WebUI interface
- API server deployment
- Cloud integration
- Advanced ML models
- Real-time rendering preview
