# NQ Profilo v2 — confluenza TPO + Volume Profile + numeri tondi, con controllo su livelli casuali

File: `indicators/atas/NqProfilo.cs` → **NQ Profilo (TPO + Volume Profile)**. Mappa statistica: nessun entry/exit.

> **Onestà.** Questa versione nasce dalla lettura dei PDF che hai caricato. I vantaggi misurati in questi paper sono **piccoli**
> (Osler: +4–6 punti percentuali di rimbalzo rispetto a livelli casuali; Howard: il segnale non filtrato sulla Value Area è nullo).
> Un edge "altissimo" non è documentato da nessuno di essi. L'indicatore serve a **misurare** sui tuoi dati se la confluenza batte il caso.

## 1. Cosa dicono i paper (letti nei PDF; per i più lunghi solo abstract/introduzione e sezioni citate)
| Paper | Risultato usato | Dove |
|---|---|---|
| Howard 2026, E-mini S&P 500, 6.284 eventi, gen 2025–gen 2026 | Breakout della Value Area non filtrato: −2,20 tick, non significativo con errori per giorno (p=0,17); senza aprile 2025 −0,19 (p=0,74). Primi 30 min: −4,04 tick (p<0,001). Tocchi **superficiali** (≤25% della larghezza) +1,49 tick contro negativi per gli altri; differenza +4,01 (p<0,001, regge Bonferroni; esplorativo, non confermato fuori campione). Larghezza VA non predice (p=0,61). Alta volatilità: i bordi diventano rumore. | pp. 12–14, 19–21 |
| Osler 2000 (FRBNY), forex intraday, 6 società, 1996–98 | Test con **10.000 serie di livelli casuali** per giorno: rimbalzo 60,8% sui livelli pubblicati contro 56,2% sui casuali. Potere predittivo ≥ 5 giorni. 70% dei livelli termina in 0, 96% in 0 o 5. | pp. 54–62 |
| Cellier, Bourghelle 2007, Euronext | Ordini limite ammassati su numeri tondi → barriere di prezzo; ordini strategici appena *oltre* i numeri tondi. | pp. 1–3 |
| Teeple (teoria) | Livelli come griglia equispaziata dovuta ad attenzione limitata. Nessun test su NQ. | pp. 1–3 |
| Gao et al. (S&P 500 ETF 1993–2013); Baltussen et al. (oltre 60 futures 1974–2020) | Il rendimento della giornata fino a 30 min dalla chiusura predice quello degli ultimi 30 min (R² ≈ 1,6% in Gao: debole). | abstract + intro |
| Cont, Kukanov, Stoikov | Il prezzo si muove in modo lineare con lo sbilancio degli ordini al best bid/ask. Richiede il DOM, che ATAS non conserva storicamente: **non usato**. | abstract + intro |
| Bailey, López de Prado (Deflated Sharpe) | Senza contare il numero di prove, un backtest "è senza valore". Per questo il pannello applica Bonferroni e tu devi contare ogni parametro che cambi. | abstract + intro |

## 2. Cosa cambia rispetto alla v1
1. **Controllo con livelli casuali (Osler).** Ogni giorno vengono generati 40 livelli casuali (altezza media delle zone, centrati sull'apertura ± il range del giorno prima) e trattati con le **stesse regole** (stessi tocchi, stesso esito). Il pannello confronta il rimbalzo di ogni grado con quello dei casuali: **l'edge è la differenza**, non la percentuale assoluta. Test a due proporzioni, soglia |z| ≥ 2,39 (Bonferroni su 3 gradi), niente verdetto sotto n=30. I livelli casuali condividono lo stesso giorno, quindi i p-value sono ottimistici (Howard corregge con errori per giorno).
2. **Numeri tondi** (multipli di 50 punti, peso 1,5; di 100, peso 2,0) come quarta famiglia di confluenza.
3. **Profilo multi-giorno:** le feature delle ultime 3 sessioni (parametro) alimentano le zone, con peso decrescente (×0,75 per giorno di età). Etichette tipo `POC-1d`.
4. **Tocchi superficiali contro profondi** (Howard): la penetrazione nella zona alla barra di primo contatto (≤25% = superficiale) è misurata *prima* dell'esito, e il pannello mostra il rimbalzo per i due casi.
5. **Filtro di regime:** giorni con ATR > 1,5× la mediana degli ultimi 20 giorni sono segnalati "HIGH-VOL" e i loro tocchi non entrano nelle statistiche.
6. **Contesto ultimi 30 minuti:** riga informativa col movimento dalla chiusura precedente (debole: R² ~1–2%).
7. Tolta la frase della v1 che collegava i "break" ripetuti a Howard: Howard non trova continuazione in media.

## 3. Logica base (invariata)
Profilo della sessione RTH (09:30–16:00 ET) in bracket da 8 tick. Volume Profile: POC, VAH/VAL (70%), HVN. TPO (30 min): TPOC, VAH/VAL TPO, single print.
Estremi: massimo/minimo del giorno, Initial Balance. Pesi (ipotesi): POC 3, TPOC/VAH/VAL/TVAH/TVAL 2,5, SP/PDH/PDL 2, HVN/IBH/IBL 1,5.
Confluenza entro 8 tick. **A**: ≥3 famiglie o punteggio ≥8. **B**: ≥2 famiglie e punteggio ≥4,5. **C**: il resto (nascosto di default).
Colore: viola se la zona è sopra il prezzo, verde se sotto. Etichetta `A 9.0 POC+TPOC+R100 T1`.
Tocchi contati solo dopo i primi 30 minuti (Howard). Esito entro 10 barre: bounce / break / neutro (±0,5 ATR).

## 4. Limiti
- I pesi, le soglie A/B/C e la tolleranza sono ipotesi non calibrate; ogni modifica è una prova in più (Bailey–López de Prado).
- Serve storico di almeno 4–5 giorni; la prima sessione non ha zone.
- Profilo sulla sessione RTH, non Globex.
- Un confronto con livelli casuali non elimina la correlazione tra eventi dello stesso giorno.
