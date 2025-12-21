# Code Style Guide (BlenderAI)

## Convenzioni
- **PEP8** come base.
- Nomi file/moduli: snake_case.
- Classi: PascalCase.
- Funzioni/metodi/variabili: snake_case.
- Costanti: UPPER_SNAKE_CASE.
- Tipo predefinito: `from __future__ import annotations` per type hints avanzati.

## Type hints
- Obbligatori su tutte le funzioni pubbliche.
- Usa `Optional` per valori nullable, `Sequence`/`Mapping` per collezioni generiche.
- `bpy` types: `bpy.types.Context`, `bpy.types.Scene`, ecc.

## Docstring (Google Style)
- Prima riga: descrizione concisa.
- Sezione Args/Returns/Raises/Examples quando rilevante.
- Brevità e chiarezza: evitare ripetizioni.

## Formattazione
- Lunghezza riga 120 max.
- Import: standard → terze parti → locali.
- Aggiungere newline finale ai file.

## Error handling
- Niente `bare except`.
- Log con messaggi chiari e azione suggerita.
- Non avvolgere gli import in try/except se non necessario (tranne diagnostica).
