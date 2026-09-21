# ENGI AI — app (V1 MVP)

App mobile (Expo / React Native + TypeScript) per lo studio universitario di ingegneria,
scaffoldata a partire dalla specifica in [`../docs/APP_MAP.md`](../docs/APP_MAP.md).

Questa è la **V1 — MVP** (vedi sezione 25 della mappa): account, materie, argomenti,
AI Tutor, scanner esercizi via fotocamera, esercizi, caricamento materiali (PDF/immagini)
e dashboard progressi. Le sezioni di V2/V3 (piano di studio AI, flashcard, simulazioni
d'esame, strumenti avanzati) sono presenti in navigazione come placeholder "in arrivo".

## Stack

- **Expo Router** (React Native + TypeScript) — file-based routing, tab bar a 5 sezioni.
- **Supabase** — auth (email/password), Postgres con Row Level Security, Storage per i
  materiali caricati, una Edge Function (`ai-tutor`) come backend del Tutor AI.
- **Claude (Anthropic API)** — richiamato solo lato server dalla Edge Function, mai dal
  client (la chiave API non è mai esposta al bundle mobile).

Le schermate di navigazione (Materie → Capitoli → Argomenti, Esercizi, Progressi) usano
dati demo (`data/mock.ts`) così l'app è esplorabile subito; Auth, Materiali e Tutor AI
sono invece collegati per davvero a Supabase.

## Setup

### 1. Dipendenze

```bash
npm install
```

### 2. Progetto Supabase

1. Crea un progetto su [supabase.com](https://supabase.com).
2. Applica lo schema in `supabase/migrations/0001_init.sql` (SQL editor della dashboard,
   oppure `supabase db push` con la Supabase CLI collegata al progetto).
3. Copia `.env.example` in `.env` e compila:
   ```
   EXPO_PUBLIC_SUPABASE_URL=...
   EXPO_PUBLIC_SUPABASE_ANON_KEY=...
   ```

### 3. Edge Function del Tutor AI

```bash
supabase functions deploy ai-tutor
supabase secrets set ANTHROPIC_API_KEY=sk-ant-...
```

La funzione (`supabase/functions/ai-tutor/index.ts`) gestisce sia la chat del Tutor AI
(modalità Spiegami/Fammi esercitare/Aiutami/Controlla/Interrogami, con l'opzione
"non darmi la soluzione") sia il riconoscimento dell'esercizio fotografato dallo scanner.

### 4. Avvio

```bash
npm run start   # poi premi "i" (iOS), "a" (Android) o "w" (web) — richiede Expo Go o un simulatore
npm run typecheck
```

Senza `.env` configurato l'app si avvia comunque (bypassando l'auth) per esplorare le
schermate demo; Materiali e Tutor AI mostrano un avviso finché Supabase non è collegato.

## Struttura

```
app/
  (auth)/            login, signup
  (tabs)/            Home, Studio, AI, Progressi, Profilo
    studio/          materie, esercizi, materiali, piano*, strumenti*, esami*  (*V2/V3)
  scanner.tsx         scansione esercizio via fotocamera (modale)
components/           Card, ProgressBar, ChapterStatusBadge, ComingSoon
context/AuthContext.tsx
lib/                  client Supabase, tema
data/mock.ts           dati demo di materie/capitoli/argomenti
types/database.ts       tipi TypeScript dello schema Supabase
supabase/
  migrations/0001_init.sql
  functions/ai-tutor/   Edge Function del Tutor AI (Deno)
```

## Prossimi passi (V2)

Calendario, Piano di studio AI, Flashcard con ripasso programmato, Simulazioni d'esame
cronometrate con analisi degli errori, notifiche mirate — vedi `../docs/APP_MAP.md`.
