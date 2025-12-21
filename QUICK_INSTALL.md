# 🚀 BlenderAI - GUIDA RAPIDA ALL'INSTALLAZIONE

## ⚡ Installazione in 2 minuti

### Step 1: Scarica il file
1. Vai su: https://github.com/leoron04/blenderAI/releases
2. Clicca su "BlenderAI v1.0.0 - Phase 2 Complete"
3. Scarica il file ZIP ("Source code (zip)")

### Step 2: Estrai e rinomina LA CARTELLA ADDON

⚠️ **ATTENZIONE - QUESTO È IMPORTANTE!**

Dopo aver estratto lo ZIP:
1. Apri la cartella estratta
2. **VEDI UNA CARTELLA CHIAMATA:**
   - `blenderAI-main` OPPURE
   - `blenderAI-1` OPPURE
   - Simile a questa

3. **RINOMINALA IN: `blenderAI`** (senza suffissi, senza trattini)

**Risultato finale:** Una cartella chiamata `blenderAI` contenente:
- `__init__.py`
- `ui.py`
- `operators.py`
- `config.py`
- ecc... (gli altri file Python)

### Step 3: Copia nella cartella addons di Blender

#### Windows:
```
C:\Users\[TUOUSERNAME]\AppData\Roaming\Blender Foundation\Blender\[VERSIONE]\scripts\addons\
```
Es: `C:\Users\Marco\AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons\`

#### Mac:
```
~/Library/Application Support/Blender/[VERSIONE]/scripts/addons/
```

#### Linux:
```
~/.config/blender/[VERSIONE]/scripts/addons/
```

**Copia la cartella `blenderAI` in uno di questi percorsi!**

### Step 4: Abilita in Blender
1. Apri Blender
2. Vai a: **Edit → Preferences → Add-ons**
3. Cerca: "BlenderAI" o "Intelligent Assistant"
4. Attiva la casella ✓
5. Vedrai il pannello BlenderAI nel 3D View (categoria: "BlenderAI")

### Step 5: Configura le API keys
1. Nel pannello BlenderAI
2. Espandi la sezione "⚙️ Config"
3. Inserisci le tue chiavi API:
   - **OpenAI Key** (per ChatGPT)
   - **Claude Key** (per Anthropic)
   - **Gemini Key** (per Google)
4. Almeno UNA è obbligatoria

---

## ❌ ERRORE: "No module named 'blenderAI-1'" ?

**Soluzione:** La cartella addon deve chiamarsi esattamente `blenderAI` (senza altri caratteri).

**Come controllare:**
1. Vai alla cartella addons di Blender
2. Guarda i nomi delle cartelle
3. Se vedi `blenderAI-main`, `blenderAI-1`, ecc:
   - Rinomina in `blenderAI`
   - Riavvia Blender

---

## ✅ Verificazione

Quando tutto è corretto, dovresti vedere:
- ✓ Blender non ha errori nel log
- ✓ Pannello "🤖 BlenderAI Agent" nella 3D View
- ✓ Pannelli sottocategorie: Scene Inspector, Code Generator, ecc
- ✓ Nessun messaggio di errore rosso in fondo

---

## 🆘 Problemi?

**Se vedi errori:**
1. Controlla il **nome della cartella addon** (deve essere `blenderAI`)
2. Controlla il **percorso** (giusto sistema operativo?)
3. **Riavvia Blender** completamente
4. Vai a Preferences e disabilita/abilita di nuovo l'addon

**Se ancora non funziona:**
- Apri la console di Blender (Window → Toggle System Console su Windows)
- Guarda il messaggio di errore rosso specifico
- Apri una Issue su GitHub: https://github.com/leoron04/blenderAI/issues

---

## 🎉 Pronto!

Ora puoi usare BlenderAI per:
- Analizzare la scena con l'AI
- Generare animazioni
- Ottimizzare render
- E molto altro!

**Buon lavoro!**
