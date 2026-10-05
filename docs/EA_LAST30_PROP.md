# EA MT5 "Last Half-Hour Momentum Prop" — l'edge con l'evidenza più ampia, e i suoi limiti

File: `mql5/LastHalfHourMomentum_Prop.mq5`. **Non compilato né testato dall'autore.**

## 1. Perché questo e non gli altri (valutazione dell'evidenza, dai PDF che hai caricato)
| Edge | Evidenza | Limiti |
|---|---|---|
| **Momentum nell'ultima mezz'ora** — Baltussen, Da, Lammers, Martens (SSRN 3760365); Gao, Han, Li, Zhou (SSRN 2440866) | Più di 60 futures, 1974–2020, tick data. Sui futures su indici azionari il rendimento "dalla chiusura precedente a 30 minuti dal close" (rROD) predice quello dell'ultima mezz'ora: R² fuori campione 2,88% sul pool, positivo e significativo in 14 contratti su 17 (pp. 13–14). Presente in entrambi i sottoperiodi 1974–1999 e 2000–2020 (p. 16). Sharpe 0,87–1,73 per classe di attività (p. 26). Meccanismo plausibile e testato: copertura di gamma degli opzionisti e degli ETF a leva. | Sharpe **lordo** (nessun costo, p. 17; con 1 tick di costo su S&P futures resta positivo). R² di pochi punti percento. **Una sola operazione al giorno.** L'effetto sparisce nei giorni con gamma netto positivo e **non si estende oltre le 16:00 ET** (p. 20, 26). Si inverte nei 1–2 giorni successivi. Zarattini cita un calo della prevedibilità dopo il 2013 (Rosa): non l'ho trovato né letto. |
| Noise Area (Zarattini; Maróy) | Replica su QQQ: Sharpe 1,1–1,3 con costi, ETF, 10 anni. | ETF, non CFD; stessa famiglia dei breakout che Fetna e Mesfin trovano non redditizi sui futures. |
| Seeck (reversione dopo sfondamento banda VXN/16) | OOS 2023–2026 Sharpe 1,29; pre-campione 2010–2017 Sharpe 1,24 solo con VXN>25. | Preprint di un singolo autore, 191 operazioni fuori campione, evento raro, richiede dati VXN. |
| Opening range breakout, segnali OHLCV a 5 minuti (Fetna, Mesfin) | Nessuna variante sopravvive ai costi. | Sono risultati negativi. |

Nessuno di questi ha un edge garantito, e **gli unici con evidenza ampia fanno poche operazioni al giorno**. Questo è in conflitto con "tante operazioni e passare in fretta".

## 2. Regola dell'EA (dal paper, equazione 12)
Alle 15:30 New York: rROD = P(15:30) / chiusura di ieri − 1. Se rROD > 0 compra, se < 0 vendi, esci alle 15:58 (prima delle 16:00). Una operazione al giorno.
Aggiunte mie: stop rigido a 2× il movimento tipico dell'ultima mezz'ora (media su 20 giorni), sizing a rischio fisso, gli stessi blocchi prop dell'altro EA (−2,5% giornaliero, −6,5% totale, target 8%/6%), filtro spread e news.
Parametro `InpMinSignalPct`: 0 = regola pura del paper (solo il segno); un valore più alto scarta i segnali piccoli, ma non è nel paper: è un parametro in più da testare.

## 3. Aspettative realistiche
Con una operazione al giorno, rischio 0,5% e stop a 2× il movimento tipico, la volatilità giornaliera del conto è dell'ordine di 0,5–0,7%. Dalla simulazione già mostrata (volatilità 0,7%, Sharpe 1,0): **circa 45% di probabilità di passare entrambe le fasi, in circa 146 giorni di borsa (7 mesi)**. Con Sharpe 0,5 circa 28%. Con il preset FAST (1,5%) i giorni scendono ma la probabilità cala (vedi tabella dell'altra guida). Lo Sharpe del paper è lordo e storico: quello netto su NAS100 CFD di GFT è sconosciuto finché non lo testi.

## 4. Installazione e test
Come per l'altro EA (guida `EA_NOISE_AREA_PROP.md`, sezioni 4 e 5): copia in `MQL5\Experts`, compila con F7, imposta l'orario del server (`InpCloseHour`: 23 per i server NY-close; controlla che la chiusura del cash US cada lì), testa con tick reali e ritardo di esecuzione su tre periodi separati. Per questa strategia confronta con la strategia "sempre long" nello stesso orario, come fa il paper: se non batte "sempre long" di almeno il costo, non c'è edge.
Report da mandarmi: HTML del tester con i parametri.
