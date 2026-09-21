# 🧠 ENGI AI — Mappa Completa dell'App (v1)

> Nome provvisorio: **ENGI AI** — il tuo ambiente di studio intelligente per Ingegneria.
>
> Questo documento è la specifica funzionale/prodotto dell'app, così come definita dal
> fondatore. Non descrive un semplice chatbot: unisce università + materiali + AI +
> esercizi + calendario + progressi in un unico ambiente di studio.

---

## 🏠 1. Home

Schermata che lo studente vede appena apre l'app.

**Header**
- 👋 Ciao, Ibra
- Corso: Ingegneria Meccanica
- Anno: 1° anno
- Università: Politecnico di Milano

**Sezione "Continua a studiare"**

```
📐 Analisi Matematica 1
Integrali indefiniti
Continua →
```

**Sezione "Oggi"**
- 📚 2h 30m da studiare
- 📝 15 esercizi
- 🎯 Obiettivo giornaliero: 70%

**Prossimo esame**

```
Analisi Matematica 1
18 gennaio 2027
⏱️ 119 giorni
```

**AI** — un grande pulsante: `🤖 Chiedi a ENGI`

---

## 📚 2. Le mie materie

Lista degli insegnamenti, ciascuno con indicatore di progresso.

- 📐 Analisi Matematica 1
- 📏 Geometria
- ⚛️ Fisica
- 🧪 Chimica
- 💻 Informatica
- ⚙️ Fondamenti di ingegneria

Ogni materia mostra: `Progresso: 64%`

---

## 📖 3. Pagina della materia

Esempio — **Analisi Matematica 1**, progresso 64%.

**Capitoli**
1. Insiemi e funzioni ✅
2. Limiti ✅
3. Continuità 🟢
4. Derivate 🟡
5. Integrali 🔴
6. Serie 🔴
7. Equazioni differenziali ⚪

**Legenda**
- 🟢 Buona preparazione
- 🟡 Da ripassare
- 🔴 Debole
- ⚪ Non ancora studiato

---

## 📑 4. Argomento

Esempio — **Integrali**. Ogni argomento è diviso in:

- 📖 **Teoria** — spiegazione dell'argomento
- 📐 **Formule** — formule principali
- 💡 **Esempi** — esempi svolti
- ✏️ **Esercizi** — allenamento
- 🤖 **Tutor AI** — "Spiegami gli integrali per principianti."

---

## 🤖 5. AI Tutor

Parte centrale dell'app. Non un chatbot generico: l'AI conosce corso di laurea,
materia, argomento, livello dello studente, materiali caricati ed errori precedenti.

**Modalità**
- **Spiegami** — "Spiegami le derivate."
- **Fammi esercitare** — "Dammi un esercizio sulle derivate."
- **Aiutami** — "Non riesco a risolvere questo esercizio."
- **Controlla** — "Ho fatto questo procedimento. Dove sbaglio?"
- **Interrogami** — "Fammi domande sulla teoria."

**Non darmi la soluzione** *(importante)* — l'AI dà solo piccoli suggerimenti
progressivi fino a quando lo studente non arriva da solo alla soluzione.

---

## 📷 6. Scanner esercizi

Pulsante: `📷 Scansiona esercizio`

Lo studente fotografa: libro, foglio, lavagna, compito, PDF. L'AI riconosce
il problema (es. "Equazione differenziale del primo ordine") e chiede:

```
Cosa vuoi fare?
🔵 Spiegazione
🟢 Risolvere insieme
🟡 Solo suggerimento
🔴 Soluzione completa
```

---

## ✏️ 7. Esercizi

Database organizzato per **Materia → Capitolo → Argomento → Difficoltà**.

**Difficoltà**: ⭐ Facile · ⭐⭐ Medio · ⭐⭐⭐ Difficile · ⭐⭐⭐⭐ Esame

**Modalità**
- **Allenamento** — 10 esercizi casuali
- **Argomento specifico** — es. solo integrali
- **Errori** — solo esercizi sbagliati in precedenza
- **Esame** — simulazione completa

---

## 🧪 8. Simulazione d'esame

Una delle funzioni potenzialmente più importanti.

**Setup**: materia, durata (es. 120 min), difficoltà (Esame), numero esercizi (es. 6).
Timer live durante la prova (`⏱️ 01:43:21`).

**Alla fine**
- Risultato (es. `27/30`)
- **Analisi degli errori** per capitolo (es. ❌ Integrali — 2 errori, 🟡 Derivate —
  1 errore, 🟢 Limiti — perfetto)
- Consiglio automatico: *"Prima dell'esame ti consiglio di ripassare gli integrali."*

---

## 📂 9. Materiali

Upload del materiale universitario: PDF, PowerPoint, Word, immagini, appunti,
dispense, esercizi, libri digitali legalmente disponibili. Organizzato per
materia/cartella, es.:

```
📁 Analisi 1
 ├── 📄 Lezione 01.pdf
 ├── 📄 Lezione 02.pdf
 ├── 📄 Derivate.pdf
 ├── 📄 Esercizi.pdf
 └── 📄 Appunti personali.pdf
```

---

## 🧠 10. "Parla con i miei materiali"

Funzione ad alto valore: lo studente carica le slide del professore e chiede,
es. "Spiegami il teorema di Rolle usando le slide del professore." L'AI risponde
usando **prima** il materiale del corso, e se l'argomento non compare nei
materiali caricati lo dichiara esplicitamente — per evitare che l'AI inventi
che qualcosa sia stato spiegato dal professore quando non lo è stato.

---

## 📝 11. Appunti intelligenti

Creazione di nuovi appunti con assistenza AI per: correggere, organizzare,
riassumere, creare formule, generare domande, trasformare appunti in flashcard.

---

## 🧠 12. Flashcard

Flusso domanda → risposta → autovalutazione:

```
😵 Non la sapevo   😐 Così così   🙂 La sapevo   🔥 Perfettamente
```

L'app usa queste informazioni per programmare il ripasso (spaced repetition).

---

## 📅 13. Calendario

Calendario universitario con eventi tipizzati: 📚 Lezione, 📝 Esercitazione,
🧪 Laboratorio, 🎓 Esame, 📖 Studio. Possibilità di inserire eventi ricorrenti
(es. "Analisi — lunedì 14:00–16:00").

---

## 🎯 14. Piano di studio AI

Lo studente inserisce l'obiettivo (es. "Esame Analisi 1, 18 gennaio, posso
studiare 2h al giorno") e l'AI costruisce un piano settimanale
(Settimana 1: limiti + continuità, Settimana 2: derivate, Settimana 3: integrali,
ecc.). Se lo studente salta una sessione ("Ho perso la sessione di oggi"),
l'AI ricalcola automaticamente il programma.

---

## 📊 15. Progressi

Dashboard personale con:
- **Preparazione semestre** complessiva (es. barra di progresso 78%)
- **Progresso per materia** (tabella Materia → Progresso)
- **⚠️ Punti deboli** (es. Integrali, Serie numeriche, Matrici)

---

## 🏆 16. Gamification

Da usare con moderazione, non come meccanica dominante.

- **XP**: +20 esercizio, +50 simulazione, +100 esame simulato
- **Streak**: 🔥 giorni consecutivi
- **Obiettivi/badge**: 100 esercizi completati, prima simulazione, 7 giorni
  consecutivi, capitolo completato

---

## 🧮 17. Engineering tools

Sezione strumenti, divisa per area:

- **Matematica**: calcolatrice, equazioni, derivate, integrali, matrici,
  vettori, numeri complessi, grafici
- **Fisica**: conversioni, cinematica, dinamica, energia, quantità di moto
- **Ingegneria**: conversione unità, proprietà geometriche, statica, momenti,
  tensioni, termodinamica

---

## 📐 18. Grafici

Input funzione (es. `f(x)=x²-4x+3`) → grafico interattivo. Comandi in linguaggio
naturale sul grafico, es. "Mostrami i punti di massimo e minimo" → evidenziazione
automatica.

---

## 🔔 19. Notifiche

Da usare con parsimonia — solo notifiche utili:
- 📚 È ora di Analisi.
- ⚠️ Mancano 7 giorni all'esame.
- 🔥 Hai completato 5 giorni consecutivi.
- 🎯 Oggi devi completare 3 esercizi.

---

## 👤 20. Profilo

Dati profilo (nome, corso, università, anno) e impostazioni: lingua, tema
chiaro/scuro, notifiche, AI, privacy, materiali, account.

---

## ⚙️ 21. Impostazioni AI

Personalizzazione del comportamento del tutor:

- **Stile di spiegazione**: Semplice · Universitario · Tecnico · Molto dettagliato
- **Quando sbaglio**: Dammi la soluzione · Dammi un suggerimento · Fammi ragionare
- **Livello**: Principiante → Intermedio → Avanzato

---

## 🧩 22. Struttura di navigazione principale

Bottom bar a 5 sezioni:

```
🏠 Home   📚 Studio   🤖 AI   📊 Progressi   👤 Profilo
```

Dentro **Studio**: 📚 Materie · 📝 Esercizi · 📂 Materiali · 📅 Piano di studio ·
🧮 Strumenti · 🎓 Esami

---

## 🔥 23. La funzione "centrale" (differenziante)

L'idea distintiva del prodotto: l'app incrocia autonomamente stato dello
studente (esame tra N giorni, % di studio, punti deboli, errori recenti, tempo
disponibile oggi) e propone un percorso concreto per la sessione odierna, es.:

```
Oggi ti consiglio questo percorso
① 20 min — Ripasso teoria integrali
② 30 min — Esempi guidati
③ 40 min — 5 esercizi
④ 20 min — Correzione errori
⑤ 10 min — Flashcard
```

Sintesi del posizionamento: *"So dove sei → so dove devi arrivare → costruisco
il percorso per portarti lì."* Non è "un'AI che risponde", è un motore di
pianificazione personalizzato guidato dai dati di progresso.

---

## 🏗️ 24. Architettura concettuale

```
                    ENGI AI
                       │
        ┌──────────────┼──────────────┐
        │              │              │
      STUDENTE         AI          DATABASE
        │              │              │
        │         ┌────┼────┐         │
        │         │    │    │         │
      Piano     Tutor Scanner      Materie
      studio    AI    esercizi     esercizi
        │         │    │    │         │
        └─────────┴────┴────┴─────────┘
                       │
                  PROGRESSI
                       │
                  PERSONALIZZAZIONE
```

---

## 🚀 25. Roadmap in 4 fasi

Il progetto **non** va costruito tutto insieme. Fasi proposte:

### 🟢 V1 — MVP
- 👤 Account
- 📚 Materie
- 📖 Argomenti
- 🤖 AI Tutor
- 📷 Foto esercizio
- ✏️ Esercizi
- 📂 Caricamento PDF
- 📊 Progressi

### 🟡 V2
- 📅 Calendario
- 🎯 Piano di studio AI
- 🧠 Flashcard
- 🎓 Simulazioni d'esame
- 🔔 Notifiche

### 🟠 V3
- 🧮 Strumenti avanzati
- Grafici
- Scanner matematico più potente
- Analisi automatica degli errori
- Personalizzazione avanzata

### 🔴 V4
Trasformazione in piattaforma multi-corso di laurea:
Meccanica → Aerospaziale → Elettrica → Informatica → Civile → ecc.
