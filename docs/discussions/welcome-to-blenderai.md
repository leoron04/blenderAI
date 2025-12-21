# Welcome to BlenderAI - Intelligent AI Assistant for Blender!

Benvenuti nella community BlenderAI! Qui trovi una panoramica rapida, link utili e come chiedere aiuto.

## Overview rapido
- **Assistente AI multi-provider**: ChatGPT, Claude, Gemini con fallback e cache locale.
- **Scene intelligence**: analisi di oggetti, materiali, luci, camera, nodi e suggerimenti contestuali.
- **Operatori autonomi**: auto-material, auto-light (3-point/key), auto-geometry, rig placeholder.
- **Code Generator con preview**: script + descrizione side-by-side prima di applicare.
- **Blender Knowledge Base v2.1**: RAG su documentazione ufficiale (3.6–4.3) e API `bpy`.

## Quick start
1. Installa l’addon seguendo [INSTALL_GUIDE.md](../../INSTALL_GUIDE.md) o [QUICK_INSTALL.md](../../QUICK_INSTALL.md).
2. Configura le API key nel pannello BlenderAI (OpenAI/Claude/Gemini) e l’ordine di fallback.
3. Apri il pannello **BlenderAI** in 3D View e avvia **Analyze Scene** per popolare lo Scene Inspector.
4. Prova il pannello **AI Suggestions** con un prompt semplice e verifica la preview nel **Code Generator**.
5. Attiva un operatore autonomo (es. auto-light) su una scena di test per validare la pipeline.

## Link utili
- [Troubleshooting](../../TROUBLESHOOTING.md)
- [Error Handling Guide](../../ERROR_HANDLING_GUIDE.md)
- [Code Style Guide](../../CODE_STYLE_GUIDE.md)
- [Release Notes](../../RELEASE_NOTES.md)

## Come chiedere aiuto
- **Q&A**: domande d’uso, configurazione, best practice. Usa il template **How-To Question**.
- **Bug**: problemi riproducibili non bloccanti ➜ template **Bug Report** (Discussion). Per bug bloccanti apri anche una Issue con il template bug.
- **Feature Request**: idee e miglioramenti ➜ template dedicato.

## Mantieni il thread aggiornato
- Marca la risposta corretta come “Answer”.
- Se pubblichi log/traceback, includi versione Blender, versione addon, OS e GPU.
- Quando il problema è risolto, aggiungi un breve riepilogo della soluzione.
