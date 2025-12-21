# Error Handling Guide

## Principi
- Messaggi chiari, azione suggerita.
- Preferire eccezioni specifiche.
- Loggare nel logger `blenderAI` o `blenderAI.import` per diagnosi.

## Errori comuni e fix
- `No module named blenderAI-1`: cartella errata → rinomina in `blenderAI` o usa git clone (vedi setup_git_clone_guide.md).
- Import fallisce in Blender: attiva `BLENDERAI_DEBUG=1`, esegui `diagnose_import.py`, controlla `~/.config/blenderai_debug.log`.
- API key mancante: inserire chiave in preferenze, validare formato (`utils.validate_api_key`).
- Nessun keyframe applicato (Animation): assicurarsi di avere oggetto selezionato o camera per ORBIT.
- Cache corrotta: elimina file in `~/.config/blender_ai/cache`.

## Codici di errore suggeriti
- `E001` Import/nome cartella errato.
- `E002` API key mancante/invalid.
- `E003` Nessun oggetto selezionato / tipo errato.
- `E004` Cache non leggibile o corrotta.
- `E005` Operazione non supportata nel contesto corrente.
