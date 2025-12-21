# Changelog

## v2.2.0

### 🔐 Security & Hardening
- Nuovi guardrail di sicurezza (`security_hardening.py`) con sanificazione input, masking segreti, rate limiting per provider e validazione environment.
- Provider AI con timeout espliciti, gestione errori senza esporre chiavi e limiti configurabili.
- Validazione variabili d'ambiente in `config.py` e input UI/Operatori sanificati.
- Linee guida aggiornate in `SECURITY_GUIDELINES.md` e requisiti di sicurezza (Bandit, Safety).
- Suite test ampliata (`tests/test_security.py`) per controlli su segreti, rate limit e validazione env.

## v1.1.0

### ✨ New Features
- Phase 2 completata con integrazioni (node graph, asset manager, render optimizer, performance dashboard, animation generator).
- Type hints estesi e docstring su operatori/UI per maggiore safety.

## v1.2.0 (in progress)

### ✨ New Features
- Ensemble multi-modello (Claude + GPT-4 + Gemini) con voting pesato e fallback automatico.
- Cache semantica con embedding leggeri, apprendimento preferenze utente e riuso suggerimenti affini.
- Collaborazione realtime via WebSocket con broadcast suggerimenti e commenti condivisi.
- Visualizzazioni avanzate: overlay 3D, preview keyframe live e heatmap nodi ottimizzazioni.
- Suite enterprise: audit log, rate limiting/quote per utente, RBAC, dashboard analytics e export JSON/YAML.

### 🔧 Improvements
- Guide aggiornate per installazione, debug, git clone, stile e gestione errori.
- Logging di diagnosi import/registrazione addon.

### 🐛 Bug Fixes
- Script diagnostici per errori di import (`diagnose_import.py`, `debug_installer.py`), naming cartella e log centralizzato.

### 📚 Documentation
- Nuove guide: INSTALL_FIX_GUIDE, TROUBLESHOOTING, setup_git_clone_guide, CODE_STYLE_GUIDE, ERROR_HANDLING_GUIDE, release notes.
