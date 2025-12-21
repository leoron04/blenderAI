# Setup con Git Clone (soluzione consigliata)

Se l’installazione via ZIP continua a dare errori (`No module named blenderAI-1`), usa direttamente il clone Git nella cartella addons per evitare rinomine/suffissi.

## Passaggi comuni
1. Chiudi Blender.
2. Apri un terminale nella cartella addons di Blender.
   - Windows: `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons`
   - Linux: `~/.config/blender/<version>/scripts/addons`

## Clone diretto
```bash
# Linux/macOS
cd ~/.config/blender/4.0/scripts/addons
git clone https://github.com/leoron04/blenderAI.git blenderAI

# Windows (PowerShell)
cd "$Env:APPDATA\\Blender Foundation\\Blender\\4.0\\scripts\\addons"
git clone https://github.com/leoron04/blenderAI.git blenderAI
```

## Verifica
1. Controlla che la cartella sia esattamente `blenderAI` e contenga `__init__.py`.
2. (Opzionale) Lancia `python diagnose_import.py` dalla cartella `blenderAI` per validare l’import.
3. Apri Blender → Preferences → Add-ons → cerca “BlenderAI” → abilita.

## Screenshot di successo
- Attiva l’addon e verifica che compaia nella lista con status “Enabled”. Se manca, riapri il pannello Add-ons e ricarica; in caso di problemi, esegui di nuovo `diagnose_import.py` e controlla il log `~/.config/blenderai_debug.log`.
