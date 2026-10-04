# NQ Flow Zones — zone "origine dell'impulso" con storico (mappa statistica, nessun entry/exit)

File: `indicators/atas/NqPotenziato.cs` (indicatore: **NQ Potenziato**).
Convive con `NqQualifiedZones` (più selettivo, con controllo FDR): questo è la versione **più frequente**, con grafica a box e storico.

> **Cosa è dedotto e cosa no.** La logica interna di Deepcharts è proprietaria e non la conosco. Dallo screenshot ho preso solo lo
> **stile** (box viola sell / verdi buy di dimensione fissa, lasciati sul grafico come storico, media mobile che cambia colore) e
> **dedotto** dove nascono i box: sull'origine di un movimento impulsivo (sell sul massimo prima del calo, buy sul minimo prima
> del rialzo). La regola sotto è una mia ipotesi *ispirata* alla letteratura, non la loro. Il pannello in alto a sinistra misura
> se funziona davvero sui tuoi dati.

## 1. Edge di letteratura (SSRN) usato qui

| Idea | Paper |
|---|---|
| Lo sbilancio di ordini è **persistente** (ordini grandi spezzati in tanti piccoli dello stesso segno) | Chordia, Subrahmanyam — [Order Imbalance and Individual Stock Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=354122); Gould, Porter, Howison — [The Long Memory of Order Flow in the FX Spot Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2595325) |
| L'impatto del flusso è in parte **transitorio** (propagatore che decade) | Taranto et al. — [Linear Models for the Impact of Order Flow on Prices I](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2770352) |
| Esiste **liquidità latente** non visibile nel book, rivelata quando il prezzo si muove | Donier et al. — [A Fully Consistent, Minimal Model for Non-Linear Market Impact](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2531917); Benzaquen, Bouchaud — [Market Impact with Multi-Timescale Liquidity](https://www.ssrn.com/abstract=3050724); Dall'Amico et al. — [How Does Latent Liquidity Get Revealed in the Limit Order Book?](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3240474) |
| OFI come segnale intraday su futures/ETF/azioni a orizzonti brevi | Kethan S E — [Predictive Order Flow Imbalance](https://papers.ssrn.com/sol3/Delivery.cfm/7053198.pdf?abstractid=7053198&mirid=1&type=2) (letto solo l'abstract) |

**Ipotesi di progetto (non dimostrata per NQ 1m):** un impulso con flusso persistente e unilaterale indica un metaordine in esecuzione.
La zona di base da cui è partito è dove si è formata la liquidità latente; al ritorno del prezzo si osserva una reazione (bounce) o
la rottura. Il tracker misura quale delle due prevale, per grado di zona.

## 2. Logica (barra a 1 minuto, solo barre chiuse)
1. Delta di barra `Δ_t = Σ(Ask − Bid)` per livello di prezzo.
2. Flusso persistente: `F_t = λ·F_{t−1} + Δ_t`, con `λ = 0.5^(1/HalfLife)` (default 4 barre).
3. z robusto su finestra mobile di 60 barre: `z = (F_t − med)/(1.4826·MAD)`.
4. **Impulso** se: `|z| ≥ ZBurst` (default 1.2), il segno di `Δ_t` coincide con quello di `F_t`, e lo spostamento di prezzo sulle
   ultime 1–3 barre in quella direzione è ≥ `MinDispAtr·ATR` (default 0.6).
5. **Zona** = range delle `OriginBars` (2) barre prima dell'impulso, con altezza limitata tra 16 e 48 tick. Impulso rialzista → box
   verde (buy), ribassista → box viola (sell).
6. **Grado:** C se |z|≥1.2, B se ≥2, A se ≥3.
7. Cooldown di 6 barre per direzione e niente box sovrapposti >50%.
8. **Tocco** con isteresi (il prezzo deve allontanarsi di 0.5 ATR). **Mitigata** se la barra chiude oltre il bordo lontano.
9. **Etichetta statistica** (non decisione): dopo un tocco, entro 10 barre → *bounce* (chiusura ≥ 0.5 ATR lontano dalla zona),
   *break* (chiusura ≥ 0.5 ATR oltre la zona) o *neutro*. Pannello: tasso di bounce al primo tocco per grado, con prior 0.50.

## 3. Test multipli: scelta consapevole
Per avere più zone qui **non** applico FDR a ogni candidato. Prezzo da pagare: più falsi positivi. Compenso: i gradi A/B/C e il pannello
dicono *quanto* ciascun grado funziona. Se il grado C mostra ~50% di bounce, non ha edge: alza `MinGrade`. Ogni soglia che provi
va contata come test; scegli i parametri su alcune sessioni e verificali su altre.

## 4. Frequenza attesa (stima, non misura)
Con i default, circa **15–40 zone per sessione** su NQ 1m (più nelle giornate di trend). Per aumentare: abbassa `ZBurst` e `MinDispAtr`;
per diminuire: alza `MinGrade` a 2.

## 5. Grafica
Box viola/verdi di larghezza fissa (`WidthBars`, default 30), storico di `HistoryDays` sessioni, opacità per grado, box mitigati sbiaditi,
media mobile EMA(20) verde se sale / viola se scende, pannello statistico. Per candele verdi/viola come nello screenshot usa i colori
candela di ATAS (impostazioni del grafico). Funziona anche su barre Range (usa l'indice barra), ma i parametri in "barre" vanno ritarati.

## 6. Come riconoscere le zone forti (aggiornamento)
Ogni zona ha un **punteggio 0–100** = 60% persistenza del flusso (|z|, tetto 6) + 40% spostamento di prezzo in ATR (tetto 3).
**A** ≥ 60 (box saturo, bordo spesso, etichetta "A 72 T0"), **B** ≥ 35 (medio), **C** < 35 (tenue, senza etichetta).
Ogni tocco abbassa l'opacità; una zona mitigata (chiusura oltre il bordo lontano) diventa quasi trasparente.
I pesi e le soglie sono ipotesi di progetto: la prova che A sia davvero più forte di C è il **pannello statistico** (tasso di bounce
per grado). Servono almeno ~30 primi tocchi per grado prima di fidarsi; se A non batte nettamente C, il punteggio non ha valore.
Per vedere solo le forti: `Min grade shown` = 2 o 3.
