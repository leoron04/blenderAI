# BlenderAI v2.1.0 – Verification Checklist (18 moduli)

Usa questa checklist prima di ogni rilascio per garantire stabilità, sicurezza e copertura completa. Tutti i punti devono essere verificati sia in locale sia in CI (pytest+coverage).

## Gate globali
- [ ] `python test_runner.py` completato con esito positivo e coverage >= 90%.
- [ ] Lint/formatting eseguiti dove applicabile (flake8/black).
- [ ] Nessuna chiave/API sensibile presente in log, file o variabili di esempio.
- [ ] `BLENDERAI_DOCS_DIR` puntato a una directory valida (seed o mock) per test offline.

## Moduli core (18)
- [ ] **agent.py** – Percorsi cache/semantic cache isolati, audit log funzionante, path RAG mockato in test.
- [ ] **ai_providers.py** – Catena provider costruita solo quando la chiave è presente; errori di rete gestiti.
- [ ] **animation_generator.py** – Applicazione keyframe valida, controlli su oggetto/camera, fallback di report.
- [ ] **asset_manager.py** – Lettura/scrittura indice su path temporaneo; ricerca semantica restituisce <=10 risultati.
- [ ] **cache.py** – Gestione safe del path cache, resilienza a JSON corrotto.
- [ ] **collaboration.py** – Hub WebSocket avviabile/fermabile senza leak thread; broadcast gestisce 0 client.
- [ ] **config.py** – Selezione modello coerente con chiavi disponibili; valori env rispettati.
- [ ] **docs_embeddings.py** – Chunking deterministico, embedding fallback offline attivo, persistenza su storage_dir di test.
- [ ] **blender_docs_manager.py** – Ingestion mockata nei test, manifest aggiornato, diff_versions restituisce added/removed/unchanged.
- [ ] **rag_system.py** – `context_as_text` include prompt template e versione target; `update_versions` ricostruisce indici.
- [ ] **scene_analyzer.py** – Conteggi oggetti/materiali corretti con mock `bpy`; fingerprint stabile.
- [ ] **semantic_cache.py** – Normalizzazione embedding, limite 50 voci, preferenze persistite.
- [ ] **operators.py** – Ogni operator gestisce report/ritorni Blender (`FINISHED`/`CANCELLED`); JSON pesi ensemble validato.
- [ ] **ui.py** – Pannelli disegnano senza eccezioni in mock `bpy`; toggles ensemble/semantic cache coerenti.
- [ ] **enterprise.py** – Rate limiter rispettato, export JSON/YAML su path temporaneo, audit log non corrotto.
- [ ] **render_optimizer.py** – Calcoli di performance non alzano eccezioni con scena mock, messaggi utente chiari.
- [ ] **performance_monitor.py** – Statistiche aggregate senza accesso a hardware specifico; no crash se dati mancanti.
- [ ] **visualization.py** – Funzioni di rendering/preview restituiscono stringhe/struct attese; nessuna dipendenza UI mancante.

## Rilascio finale
- [ ] Workflow GitHub Actions `tests` verde su push.
- [ ] Note di rilascio aggiornate con eventuali variazioni di test/CI.
- [ ] Archivi/artefatti sensibili rimossi prima del tag.
