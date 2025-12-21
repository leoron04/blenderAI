# BlenderAI – Guida Rapida per correggere l’errore `No module named blenderAI-1`

Se Blender segnala `No module named blenderAI-1` o nomi simili, significa che la cartella dell’addon non ha il nome corretto. L’addon **deve** risiedere in una cartella chiamata esattamente `blenderAI` (senza suffissi `-master`, `-1`, numeri o versioni).

## Passi rapidi (tutti i sistemi operativi)

1. **Chiudi Blender**.
2. Apri il file manager e vai alla cartella Addons:
   - Windows: `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons`
   - Linux: `~/.config/blender/<version>/scripts/addons`
3. Trova la cartella con nome `blenderAI-master`, `blenderAI-1`, `blenderAI-main` o simile.
4. **Rinomina** la cartella in `blenderAI` (solo questo nome, minuscolo/maiuscolo come indicato).
5. Riavvia Blender e riabilita l’addon se richiesto.

## Verifica veloce da terminale

Esegui dalla cartella che contiene l’addon:

```bash
python debug_installer.py
python diagnose_import.py  # per tracciare percorsi sys.path e find_spec
```

Lo script controlla:
- Nome cartella effettivo vs. richiesto (`blenderAI`).
- Percorsi add-on configurati di Blender (se `bpy` è disponibile).
- Scrive anche un log dettagliato in `~/.config/blenderai_debug.log` con il punto esatto di fallimento dell'import.

Se lo script mostra un “WARN” sul nome cartella, rinominala come descritto sopra e rilancia Blender.
