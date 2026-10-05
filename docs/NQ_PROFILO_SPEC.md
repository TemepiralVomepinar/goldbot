# NQ Profilo — zone di confluenza TPO + Volume Profile giornaliero (mappa statistica, nessun entry/exit)

File: `indicators/atas/NqProfilo.cs` → indicatore **NQ Profilo (TPO + Volume Profile)**. Pacchetto separato da "NQ Potenziato".

> **Sull'"altissimo edge".** Non posso prometterlo e la letteratura non lo dimostra. L'abstract del paper più vicino (Howard, sotto)
> dice che il test empirico sistematico delle regole del Market Profile è "largamente assente" dalla letteratura accademica.
> La combinazione TPO + Volume Profile qui è una **mia ipotesi di progetto**; il pannello misura se la confluenza funziona sui tuoi dati.
> Ho letto solo titoli e abstract dai risultati di ricerca (l'accesso diretto a SSRN dal mio ambiente è bloccato).

## 1. Letteratura (SSRN)
| Idea | Paper |
|---|---|
| Value Area (profilo di volume) su E-mini S&P 500: breakout di VA, 6.284 eventi, gen 2025–gen 2026, dati al secondo. Eventi nei **primi 30 minuti** peggiori (p<0.001: i bordi della VA sono inaffidabili durante la formazione iniziale dell'asta). Stop di prezzo distruggono valore a tutte le 12 distanze testate; uscite basate sul tempo meglio in 11 mesi su 13. | Howard — [Stop Distance, Exit Methodology, and Signal Preservation in Intraday Value Area Breakouts](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6350238) |
| Ordini limite/stop si ammassano su livelli di prezzo: inversioni e movimenti rapidi dopo la rottura | Osler — [Support for Resistance: Technical Analysis and Intraday Exchange Rates](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID888805_code387943.pdf?abstractid=888805&mirid=1); [Currency Orders and Exchange-Rate Dynamics](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=923370) |
| Supporto/resistenza emergono perché i trader discretizzano il prezzo su una griglia (aggiornamento bayesiano "grossolano") | Teeple — [Support, Resistance, and Technical Trading](https://papers.ssrn.com/sol3/Delivery.cfm/3667920.pdf?abstractid=3667920&mirid=1) |

Cosa ne prendo: (a) i livelli del profilo giornaliero come punti di ammassamento di liquidità; (b) **non contare i tocchi nei primi 30 minuti**
(parametro `Arm zones after`); (c) nessuna logica di stop: l'indicatore è solo una mappa.

## 2. Logica (profilo della sessione RTH precedente → zone di oggi)
Profilo costruito su barre chiuse della sessione NY (09:30–16:00 ET), con *bracket* di prezzo di 8 tick (2 punti, parametro).
**Volume Profile:** POC (massimo del volume smussato), VAH/VAL (70% del volume, espansione di 2 bracket), fino a 3 **HVN** (massimi locali con z robusto ≥ 1).
**TPO** (periodi da 30 min): TPO POC, VAH/VAL TPO (70% dei TPO), **single print** (almeno 3 bracket consecutivi con un solo TPO, bordi alto/basso, le 2 serie più lunghe).
**Estremi:** massimo/minimo del giorno (PDH/PDL) e Initial Balance (primi 60 min: IBH/IBL).
Pesi (ipotesi): POC 3, TPOC 2.5, VAH/VAL 2.5, TVAH/TVAL 2.5, SP 2, PDH/PDL 2, HVN 1.5, IBH/IBL 1.5.

**Confluenza.** I livelli entro 8 tick si fondono in una zona (altezza min 12 tick). Punteggio = somma dei pesi dei livelli distinti;
*famiglie* = Volume Profile / TPO / Estremi.
**A**: tutte e 3 le famiglie, o punteggio ≥ 8. **B**: ≥ 2 famiglie e punteggio ≥ 4.5. **C**: il resto (nascosto di default: `Min grade shown` = 2).

**Colore.** Viola se la zona sta sopra il prezzo (resistenza), verde se sotto (supporto): cambia da sola quando il prezzo la attraversa.
Etichetta: grado, punteggio, livelli che la compongono (es. `A 9.0 POC+TPOC+PDH T1`). Il numero dopo T = tocchi contati.

## 3. Misura (mai assunta)
Primo tocco (dopo l'armamento, con isteresi di 0.5 ATR): entro 10 barre → **bounce** (il prezzo riparte da dove è venuto, ≥ 0.5 ATR),
**break** (oltre la zona ≥ 0.5 ATR) o neutro. Pannello: tasso di bounce per grado, prior 0.50. Servono ~30 tocchi per grado prima di fidarsi.
Un "break" ripetuto sui bordi VA è coerente con i breakout di Howard: se per il grado A il break domina, la zona va letta come continuazione.
Ogni soglia modificata è un test in più: scegli i parametri su alcune sessioni e verificali su altre.

## 4. Limiti
- Servono giorni di storico caricati: la prima sessione non ha zone (non esiste un "giorno precedente").
- Usa la sessione RTH, non Globex.
- I pesi, le soglie A/B/C e la tolleranza di cluster sono ipotesi non calibrate.
