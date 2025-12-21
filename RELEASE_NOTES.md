# BlenderAI v1.1.0 – Release Notes

## Upgrade path (da v1.0.0)
1. Rimuovi eventuali vecchie cartelle addon con suffissi (`blenderAI-1`, `blenderAI-main`, ecc.).
2. Consigliato: clona direttamente il repository nella cartella addons (vedi `setup_git_clone_guide.md`).
3. In alternativa, reinstalla da ZIP ma rinomina la cartella finale in `blenderAI`.
4. Avvia Blender, abilita l’addon e, se necessario, imposta `BLENDERAI_DEBUG=1` per log di import.

## Breaking changes
- Nessuna: release compatibile con v1.0.0.

## Migrazione per utenti git clone
1. `git pull origin main` dentro la cartella `blenderAI`.
2. Riavvia Blender e verifica in Preferences → Add-ons che BlenderAI sia attivo.
3. Se compaiono errori, esegui `python diagnose_import.py` e consulta `~/.config/blenderai_debug.log`.

## Known limitations
- Ambiente di test automatico non disponibile per bpy: eseguire verifiche direttamente in Blender.
- Import di dipendenze pip aggiuntive non gestito dal pacchetto ZIP; usare git clone o installare nel Python di Blender.

## Roadmap breve
- Miglioramento copertura type hints su tutti i moduli bpy.
- Hook di integrazione per screenshot automatici dei pannelli.
- Pipeline CI per lint/typecheck con ambiente Blender headless.
