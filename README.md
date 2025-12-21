# BlenderAI - Super Intelligent Blender Addon

**Badge:** Production Ready | Well Documented | Type Safe

An advanced AI-powered Blender addon that integrates with multiple AI models (ChatGPT, Gemini, etc.) to provide intelligent assistance for 3D modeling, animation, and VFX workflows.

## Versione

Current: **1.1.0**

## Features

- **Intelligent Agent System**: analisi completa della scena (oggetti, materiali, luci, camera, modifiers, nodi) e suggerimenti automatici.
- **Multi-provider con fallback**: supporto per Claude ➜ GPT-4 ➜ Gemini con priorità configurabile e cache locale (~/.config/blender_ai/cache).
- **Pannelli avanzati**: Scene Inspector, AI Suggestions, Code Generator con preview side-by-side (script + descrizione).
- **Operatori autonomi (stub sicuri)**: auto-material, auto-light (3-point/key), auto-geometry, auto-rig placeholder con hook futuro.
- **Preview & Safety**: validazione minima, preview codice prima di applicare, logging sintetico redatto.

## Installation

1. Download or clone this repository
2. Copy the `blender_ai` folder to your Blender addons directory:
   - Windows: `%APPDATA%\Blender Foundation\Blender\version\scripts\addons`
   - macOS: `~/Library/Application Support/Blender/version/scripts/addons`
   - Linux: `~/.config/blender/version/scripts/addons`
3. Open Blender and enable the addon in Edit > Preferences > Add-ons
4. Configura le API key nelle preferenze del pannello BlenderAI:
   - OpenAI, Anthropic (Claude), Google Gemini
   - Imposta temperature, modello e priorità fallback

## Configuration

First time setup requires API keys:
- Add your API keys in the addon preferences
- Supports OpenAI (ChatGPT), Google Gemini, and other models

## Usage

1. Apri il pannello BlenderAI in 3D View.
2. Premi **Analyze Scene** per popolare lo Scene Inspector.
3. Inserisci un prompt in **AI Suggestions** e genera proposte: vengono mostrate con provider, modello e info cache.
4. Esamina la preview nel pannello **Code Generator** (script a sinistra, descrizione a destra) prima di applicare.
5. Usa gli operatori autonomi (stub sicuri) per materiale, luci, rig placeholder, geometria procedurale.

## Quick Links
- [Install Guide](INSTALL_GUIDE.md)
- [Install Fix Guide](INSTALL_FIX_GUIDE.md)
- [Setup via Git Clone](setup_git_clone_guide.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Error Handling Guide](ERROR_HANDLING_GUIDE.md)
- [Code Style Guide](CODE_STYLE_GUIDE.md)
- [Release Notes](RELEASE_NOTES.md)

## Requirements

- Blender 3.6+
- Python 3.10+
- API key da almeno un provider supportato (Claude, GPT-4, Gemini)

## License

MIT License

## Author

leoron04
