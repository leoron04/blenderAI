# BlenderAI Security Guidelines (v2.2.0)

Questa guida riassume le pratiche minime di hardening per BlenderAI.

## Gestione segreti
- **Solo variabili d'ambiente**: configura `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`. Non commitare mai chiavi nei file blend o nelle preferenze.
- **Validazione**: chiavi devono rispettare il pattern alfanumerico (min. 12 caratteri). Errori vengono troncati e mai riportati con la chiave completa.
- **Logging sicuro**: usa `utils.log_message(..., secrets=[...])` o `security_hardening.ensure_safe_message` per redigere errori contenenti valori sensibili.

## Chiamate rete
- Ogni richiesta HTTP deve avere `timeout` esplicito e gestione `RequestException`/`Timeout`.
- Applica **rate limiting per-provider** con finestre configurabili (default 60 req/min).
- Non includere payload o header sensibili nei messaggi d'errore.

## Validazione input
- Sanitizza sempre input utente (UI, operatori, API) con `security_hardening.sanitize_user_input` e `validate_port`.
- Imposta lunghezze massime e rimuovi caratteri di controllo.
- Rifiuta richieste senza prompt valido o con parametri non numerici.

## Protezione runtime
- Abilita audit log e RBAC (ruoli: admin/creator/viewer) prima di esportare o applicare script.
- Mantieni cache e export privati sotto `~/.config/blender_ai/`.

## Tooling consigliato
- **Bandit**: `bandit -q -r .` per l'analisi statica di sicurezza.
- **Safety**: `safety check` per CVE note sulle dipendenze.
- **git-secrets**: verifica che nessuna chiave sia stata accidentalmente aggiunta alla history.
