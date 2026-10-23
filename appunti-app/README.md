# Appunti

Piccola web app per consultare, scrivere e generare appunti. Nessuna dipendenza oltre a Node 20+.

Gli appunti sono file Markdown in `notes/` (con un'intestazione `title` / `subject` / `updated`).
Qualsiasi file `.md` aggiunto lì compare subito nell'app, quindi gli appunti che chiedi a Claude
in chat vengono scritti direttamente in `notes/` e li trovi nell'elenco.

## Avvio

```bash
cd appunti-app
npm start            # http://localhost:3000
```

## Variabili d'ambiente

| Variabile | Descrizione |
|---|---|
| `PORT` | Porta del server (default `3000`) |
| `NOTES_DIR` | Cartella degli appunti (default `./notes`) |
| `ANTHROPIC_API_KEY` | Abilita "Genera con l'AI" nell'app; la chiave resta solo sul server |
| `ANTHROPIC_MODEL` | Modello usato per la generazione (default `claude-sonnet-5-5`) |
| `APP_TOKEN` | Se impostato, l'app chiede questa password (consigliato se la pubblichi online) |

## Funzioni

- Elenco con ricerca e filtro per materia
- Lettura con rendering Markdown (titoli, elenchi, tabelle, codice, citazioni)
- Creazione, modifica ed eliminazione
- Generazione di appunti con l'AI a partire da una richiesta

Se pubblichi l'app online imposta sempre `APP_TOKEN`: senza, chiunque può modificare gli appunti
e usare la tua chiave API.
