# EA MT5 "Noise Area Momentum Prop" — guida, limiti e protocollo di test

File: `mql5/NoiseAreaMomentum_Prop.mq5`. **Non è stato compilato né testato dall'autore** (qui non c'è MetaEditor né dati).

## 1. Su cosa si basa (paper letti nei PDF)
- **Zarattini, Aziz, Barbon, "Beat the Market" (SSRN 4824172)**, SPY 2007–2024, dati a 1 minuto. *Noise Area*: media su 14 giorni di |prezzo/apertura − 1| per ogni orario; bande attorno a max/min(apertura, chiusura di ieri). Decisioni solo a HH:00 e HH:30, long sopra la banda alta, short sotto la bassa. Uscita: il prezzo attraversa max(banda alta, VWAP) per i long, min(banda bassa, VWAP) per gli short. Con sizing a volatilità target: Sharpe 1,33, 19,6% annuo, drawdown 25%; senza VWAP e con stop sulla banda opposta solo Sharpe 0,61 (pp. 11–16). Win rate delle operazioni ~37%.
- **Maróy (SSRN 5095349)** replica su dati a 1 secondo, 10 anni: SPY Sharpe 0,98 (non 1,33), QQQ (Nasdaq-100) 1,11 con 14 giorni e 1,28 con 90 giorni. I suoi Sharpe > 3 arrivano da ottimizzazione di parametri: **non li considero attendibili**.
- **Fetna (SSRN 7428398)**: nessuna delle 225 varianti di Opening Range Breakout sopravvive a 25 $ di costo per round-trip sui futures (2010–2026). Il Noise Area è un'altra regola, ma della stessa famiglia (momentum dall'apertura): il rischio che i costi mangino il vantaggio è reale.
- **Mesfin (SSRN 6709401)**: su MNQ i segnali OHLCV semplici falliscono fuori campione; assume 2 punti di attrito per round-trip.
- Seeck (SSRN 7364204), mean reversion sul Nasdaq-100 quando il VXN è alto: **non incluso** (il feed del broker non ha il VXN e il campione è di 860 eventi).

## 2. Cosa aggiungo io (non dai paper)
Sizing: il minimo tra volatilità target e rischio massimo al *hard stop*; stop rigido sul broker (il paper controlla lo stop solo ogni 30 minuti, troppo per un limite giornaliero del 4%); blocco giornaliero a −2,5% e totale a −6,5% (limiti prop 4% e 10%); blocco al raggiungimento del target (8% / 6%); filtro spread; filtro news ±2 minuti (solo in live: il tester MT5 non ha il calendario); chiusura 5 minuti prima del close.

## 3. Aspettative realistiche (simulazione, non backtest)
Simulazione Monte Carlo con rendimenti giornalieri a code spesse, target 8% poi 6%, stop se la perdita intraday supera 4% (stima con intraday 1,25× la chiusura) o il drawdown totale 10%, senza limite di tempo (max 250 giorni):

| Sharpe annuo supposto | volatilità giornaliera | P(passa fase 1) | P(passa entrambe) | giorni mediani |
|---|---|---|---|---|
| 1,0 | 0,7% | 71% | 45% | 146 |
| 1,0 | 1,0% | 65% | 45% | 92 |
| 1,0 | 1,5% | 49% | 28% | 43 |
| 1,0 | 2,0% | 41% | 20% | 25 |
| 1,3 | 0,7% | 77% | 55% | 139 |
| 1,3 | 1,0% | 70% | 52% | 90 |
| 1,3 | 2,0% | 46% | 25% | 23 |
| 0,5 | 1,0% | 55% | 32% | 96 |

Lettura: **rischiare di più per fare in fretta abbassa la probabilità di passare**. Il punto migliore è circa 0,7–1,0% di volatilità giornaliera, che richiede mesi. Anche con lo Sharpe del paper la probabilità di passare entrambe le fasi è circa 50%. Questi numeri dipendono dallo Sharpe che ipotizzo: lo Sharpe vero su NAS100 CFD con i costi di GFT è sconosciuto finché non lo testi.

Stima grezza del margine: nel paper il guadagno medio per operazione è ~0,09 $ su azioni SPY da circa 200–300 $, cioè ~3–4 punti base; su NAS100 a ~25.000 sono ~8–10 punti lordi per operazione, contro 2–4 punti di spread e slippage. Margine sottile: lo slippage reale di GFT, che non è pubblico, può decidere tutto.

## 4. Installazione
1. In MT5: File → Apri cartella dati → `MQL5\Experts`, copia `NoiseAreaMomentum_Prop.mq5`.
2. MetaEditor → apri il file → F7. Se compare un errore, mandami le righe `error`.
3. **Orario del server:** il parametro più importante. `InpOpenHour/Min` è l'apertura US (09:30 New York) **sull'orologio del server del tuo broker**. Per i server "NY close" (GMT+2/+3 con ora legale USA) è 16:30 e la chiusura 23:00. Verifica sul grafico M1 del NAS100: la barra di apertura del cash USA (grosso volume e salto) deve cadere a quell'ora. Se il tuo server è diverso, cambia i quattro parametri.
4. Lo strumento è quello del grafico a cui attacchi l'EA (NAS100/US100). Serve storico M1 di almeno 3 settimane già scaricato (scorri il grafico M1 all'indietro).
5. Live: imposta `InpInitialBalance` al saldo iniziale reale del conto (serve per i limiti 10% e target).

## 5. Protocollo di test (lo fai tu in MT5 → Strategy Tester)
1. Simbolo NAS100/US100 del conto GFT, periodo M1, modello **"Ogni tick basato su tick reali"**, depositi uguali al conto, leva 1:100.
2. Intervallo: tutto lo storico che il broker offre (idealmente 2021–2026). **Non ottimizzare** al primo giro: parametri di default.
3. **Ritardo di esecuzione** (slippage): prova "Nessun ritardo", poi "Ritardo casuale" (es. 100–500 ms) e poi uno stress con `InpDeviationPoints` più alto. Se i risultati spariscono con lo slippage, la strategia non è usabile su GFT.
4. Tre test separati: gli ultimi 12 mesi, i 12 prima, il resto. Se funziona in uno solo, non c'è un edge stabile (come in Howard: regime di aprile 2025).
5. Prova `InpLookback` 14 e 90 e `InpVolMult` 1,0 e 1,3. Sono 4 combinazioni: conta ogni combinazione come una prova (Bailey–López de Prado) e scegli sul primo periodo, controlla sul secondo.
6. Mandami per ogni test: il report HTML (tasto destro → Salva come report) e i parametri usati. Con quelli verifico drawdown giornaliero, rapporto con i limiti 4% e 10% e rifaccio la simulazione con i tuoi numeri reali.

## 6. Regole GFT da verificare (non pubbliche o non verificate da me)
Perdita giornaliera su saldo o equity e a che ora si azzera (`InpDayResetHour`); perdita massima fissa o trailing; EA ammessi; limite lotti; slippage; blocco news (secondo siti terzi: profitto entro ±2 minuti da news ad alto impatto limitato all'1%, da confermare sul sito GFT).
