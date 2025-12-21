# TROUBLESHOOTING BlenderAI

## Errore “No module named blenderAI-1” o simili
1. **Soluzione raccomandata**: clona il repo direttamente nella cartella addons (vedi `setup_git_clone_guide.md`). Assicurati che il nome cartella sia esattamente `blenderAI`.
2. Se usi ZIP, scompatta e rinomina la cartella in `blenderAI` (senza suffissi). Evita percorsi con spazi o caratteri speciali.
3. Esegui `python diagnose_import.py` dalla cartella dell’addon; controlla il log `~/.config/blenderai_debug.log` per i percorsi cercati.
4. Se ancora fallisce, imposta `BLENDERAI_DEBUG=1` nelle variabili d’ambiente e riavvia Blender per log dettagliati durante il load.

## Come pulire la cache addon di Blender
1. Chiudi Blender.
2. Rimuovi eventuali cartelle duplicate in:
   - Windows: `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons`
   - Linux: `~/.config/blender/<version>/scripts/addons`
3. Elimina eventuali file `.pyc` e cartelle `__pycache__` dentro `blenderAI`.
4. Riavvia Blender e reinstalla/riabilita l’addon.

## Altri errori comuni
- **Addon non appare in lista**: verifica che esista `__init__.py` dentro `blenderAI`; controlla i log con `BLENDERAI_DEBUG=1`.
- **Percorsi non trovati**: controlla `sys.path` nel log `blenderai_debug.log`; aggiungi manualmente il percorso addon in Blender Python se necessario.
- **Import di dipendenze esterne**: Blender non gestisce dipendenze pip da ZIP. Usa git clone o installa i pacchetti nel Python di Blender se indispensabile.
