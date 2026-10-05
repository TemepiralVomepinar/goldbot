# EA MT5 "Drift VWAP Pullback" — dalla trascrizione del video di Matteo Conti

File: `mql5/DriftVWAPPullback_Prop.mq5`. **Non compilato né testato dall'autore.** Le regole vengono dalla trascrizione che mi hai incollato; i risultati del video **non sono verificabili** (nessun report, nessun dato).

## 1. Regole (dal video)
Strumento Nasdaq-100 futures. Il VWAP è ancorato all'apertura 09:30 ET e calcolato sulle barre da 15 minuti; la candela di trigger è da 5 minuti.
Ogni 15 minuti, sulla barra appena chiusa:
- **Long** se: (1) prezzo sopra il VWAP, (2) VWAP in salita rispetto alla barra da 15 minuti precedente, (3) prezzo salito almeno 0,1% nell'ultima ora (4 barre da 15 minuti). **Short** speculare.
- Niente operazioni 09:30–10:30 ET.
- **Trigger:** prima candela rossa (long) / verde (short) a 5 minuti dopo che le tre condizioni valgono; ordine a mercato all'apertura della candela successiva.
- **Uscite:** long SL 80 punti / TP 40; short SL 80 / TP 50.
- **Limiti:** una posizione alla volta, massimo 4 operazioni al giorno, stop dopo 2 perdite, niente nuove entrate dopo le 15:30 ET, chiusura di tutto alle 15:55 ET.

## 2. Dove ho dovuto interpretare (il video non lo dice)
1. **Prezzo "typical" del VWAP:** uso (massimo+minimo+chiusura)/3 pesato per il volume in tick (il CFD non ha volume reale).
2. **Quando scatta la valutazione:** a ogni chiusura di barra da 15 minuti, e se la candela da 5 minuti si chiude nello stesso istante, può già fare da trigger.
3. **Riarmo dopo un'entrata:** il trigger si riarma a ogni valutazione di 15 minuti in cui le condizioni valgono ancora (`InpRearmEveryEval`). Il video dice solo "primo pullback".
4. **"Max due perdite":** lui dice "due perdite consecutive": `InpLossesConsecutive = true`. Con `false` sono due perdite in totale.
5. **Orari:** valgono per un server "NY-close" (apertura 16:30, ultima entrata 22:30, chiusura 22:55). Verifica sul grafico, come per gli altri EA.

## 3. Cosa dicono i numeri del video (e cosa non dicono)
- **Win rate 64–65%, vincita media 866 $, perdita media 1.300 $** (1 contratto NQ, 20 $ a punto). Ne segue un guadagno medio di circa **97 $ per operazione, cioè 4,9 punti NQ lordi** (calcolo mio). Il pareggio è a un win rate del 60%.
- Con target/stop esatti il pareggio è al **66,7% per i long (TP 40/SL 80) e al 61,5% per gli short (TP 50/SL 80)**: a 64–65% i long, da soli, sarebbero in lieve perdita. L'edge dichiarato dipende quindi dalle chiusure di fine giornata (le medie del video, 866 e 1.300, non coincidono con 40–50 e 80 punti) e dal lato short.
- **4,9 punti di margine lordo** sono piccoli rispetto ai costi: spread e slippage sul NAS100 CFD sono di 1–3 punti per operazione (Mesfin assume 2 punti a round-trip). Lo dice anche lui: "se la usi con il tuo capitale è improbabile che ti faccia guadagnare".
- **0,1% e le uscite sono stati ottimizzati sui dati 2020–2024** (lo dice lui). Il 2024–2026 sarebbe fuori campione, ma non ho i dati né i report per verificarlo.
- **"93,6% di passare in quattro tentativi"** è 1 − (1 − 0,498)⁴, cioè assume tentativi **indipendenti** e un edge che resta uguale. Se l'edge non c'è più, falliscono tutti i tentativi insieme. Inoltre 49,8% per tentativo vale per la sua challenge, con 1 contratto NQ (perdita media ≈ 2,6% di un conto da 50k); per GFT va ricalcolato.
- **Incompatibile con i tuoi limiti così com'è:** su un conto da 50k, 1 NQ perde 1.600 $ allo stop (3,2%): due perdite sono 6,4%, oltre il tuo limite giornaliero del 4%. L'EA dimensiona quindi sul rischio (SAFE 0,5%, FAST 1,0% per stop).

## 4. Simulazione per GFT (mia, non backtest)
Con le statistiche del video (vincita 0,67R, perdita 1R, circa 3 operazioni al giorno, stop dopo 2 perdite), target 8% poi 6%, perdita giornaliera 4%, massima 10%:

| win rate | rischio per trade | passa fase 1 | passa entrambe | giorni mediani |
|---|---|---|---|---|
| 64,5% (video) | 0,5% | 98% | 95% | 123 |
| 64,5% | 1,0% | 92% | 85% | 52 |
| 62% | 1,0% | 75% | 59% | 67 |
| 60% (pareggio) | 1,0% | 53% | 32% | 72 |
| 58% | 1,0% | 30% | 12% | 72 |

Lettura: **se il win rate vero è quello del video, la strategia passa quasi sempre; ma basta perdere 4–5 punti percentuali (costi, slippage, edge che svanisce) per scendere sotto il 35%.** Questa è la verifica che conta e la fai tu nello Strategy Tester: se nel test il win rate netto è sotto il 62%, non usarla.

## 5. Come testarla
Come per gli altri EA (`EA_NOISE_AREA_PROP.md`, sezioni 4 e 5): tick reali, ritardo di esecuzione casuale, tre periodi separati (in particolare 2024–2026 come "fuori campione"). Controlla nel report: win rate **netto**, vincita e perdita medie, numero di operazioni al giorno (il video: circa 3). Se non ci sono circa 4.000 operazioni su 5 anni e mezzo, qualcosa nelle mie interpretazioni (punto 2 sopra) è diverso dal suo.
