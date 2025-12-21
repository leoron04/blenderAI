# Contributi a BlenderAI

Grazie per il tuo interesse! Questa guida spiega come preparare l’ambiente, sviluppare in modo coerente e inviare PR di qualità.

## Requisiti
- Python 3.10+
- Blender 3.6+ (consigliata la versione usata nelle release notes correnti)
- `pip` e `virtualenv` o strumento equivalente

## Setup ambiente di sviluppo
1. **Fork** del repository su GitHub.
2. **Clona** il fork:  
   ```bash
   git clone https://github.com/<tuo-utente>/blenderAI.git
   cd blenderAI
   ```
3. **Crea un branch** descrittivo: `git checkout -b feature/nome-breve` o `fix/bug-rilevante`.
4. **Crea un virtualenv** e installa le dipendenze:  
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
5. **Configura le chiavi** e i file necessari (vedi `INSTALL_GUIDE.md` e `.env.example` se applicabile).

## Standard di codice
- Segui **PEP 8** e le note aggiuntive in `CODE_STYLE_GUIDE.md`.
- Aggiungi **docstring** e **type hints** ove possibile.
- Evita regressioni di performance; preferisci funzioni pure e testabili.
- Log chiari ed error handling esplicito (no swallow di eccezioni).

## Test e qualità
- Esegui i test rilevanti (es. `pytest` o `python -m pytest`).
- Se tocchi codice critico, aggiungi/aggiorna test in `tests/`.
- Aggiorna documentazione e esempi se il comportamento cambia.

## Commit e branch
- Usa **Conventional Commits** (es. `feat(core): ...`, `fix(rag): ...`, `docs(community): ...`).
- Mantieni commit piccoli e atomici; rebase interattivo prima della PR è benvenuto.

## Come aprire una Pull Request
1. Assicurati che i test passino e che la formattazione rispetti gli standard.
2. Scrivi una descrizione chiara: contesto, soluzione proposta, eventuali alternative.
3. Collega issue o discussione di riferimento (`Fixes #123` quando applicabile).
4. Richiedi review pingando i maintainer se necessario.
5. Rispondi al feedback con ulteriori commit o commenti; evita force push aggressivi durante la review.

## Template e issue tracking
- **Bug bloccanti**: apri una Issue con il template `Bug Report` (fornisci file di test).
- **Domande/how-to**: usa Discussions categoria **Q&A** con il template dedicato.
- **Feature request**: Discussions categoria **General** con template dedicato; crea Issue solo quando la richiesta è accettata.

## Sicurezza
- Non condividere chiavi o segreti nei log o nei file di config.
- Per vulnerabilità, usa canali privati o segnala via Issue privata (senza dettagli pubblici).

Grazie per contribuire a rendere BlenderAI migliore! 🙌
