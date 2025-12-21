# BlenderAI Documentation Cache

Questa cartella contiene gli artefatti strutturati dell’ingestione della documentazione Blender (manuale, API `bpy`, guida sviluppo add-on) per tutte le versioni supportate (3.6+). I file vengono generati da `blender_docs_manager.py` e arricchiti con embedding da `docs_embeddings.py`.

Struttura tipica:

- `raw/<version>/` – HTML scaricati (opzionale, solo per debug).
- `parsed/<version>.json` – entry normalizzate (classi, funzioni, proprietà, esempi).
- `embeddings/<version>.npy` – matrice embedding per ricerca semantica.
- `manifest.json` – indice aggiornamenti/versioni disponibili.

Non modificare manualmente: usare gli script di ingestione/aggiornamento o il workflow CI `.github/workflows/update-blender-docs.yml`.
