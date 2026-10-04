# NQ 1-minute "Qualified Zones" — specifica statistica (mappa di riferimento, nessun entry/exit)

Strumento: Nasdaq-100 futures (NQ), grafico a 1 minuto, sessione cash di New York (09:30–16:00 ET).
Output: rettangoli di prezzo con uno stato statistico. Nessuna regola di ingresso/uscita.

> **Onestà sui limiti.** I paper sotto sono verificati (titolo/abstract letti via ricerca su SSRN), ma nessuno di essi
> fornisce parametri calibrati per NQ a 1 minuto. Soglie, pesi, `κ`, `N_max`, ecc. sono **ipotesi di progetto**: l'indicatore
> include un tracker bayesiano che misura quanto le zone funzionano davvero, così le ipotesi vengono falsificate dai dati
> e non assunte. Il codice C# non è stato compilato contro l'SDK ATAS (non disponibile qui): i punti dove l'API va verificata sono marcati `// VERIFY`.

---

## 1. Edge di letteratura (SSRN) → ingredienti operativi

| Concetto | Paper (SSRN) | Cosa ne prendiamo |
|---|---|---|
| Price change ≈ lineare nell'order flow imbalance, pendenza ∝ 1/profondità | Cont, Kukanov, Stoikov — [The Price Impact of Order Book Events](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1712822) | `ΔP ≈ β·OFI`, `β ∝ 1/depth`. Un nodo con grande volume ha β locale basso: il prezzo "fatica" ad attraversarlo. |
| Livelli profondi del book aggiungono potere predittivo | Cao, Hansch, Wang — [The Informational Content of an Open LOB](https://ssrn.com/abstract=565324) | Non guardare solo il best bid/ask: aggregare lo sbilancio su un **intervallo di livelli** (la zona), non su un tick. |
| Impatto transitorio: il prezzo = somma pesata dei segni passati, propagatore che decade a potenza | Taranto, Bormetti, Bouchaud, Lillo, Tóth — [Linear Models for the Impact of Order Flow I](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2770352); Tóth, Eisler, Bouchaud — [Short-Term Price Impact Is Universal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2924029) | Parte dello spostamento causato da flusso unilaterale **decade**. Una zona nata da spinta unilaterale con alta efficienza di prezzo è "impatto" (ritraccia in parte); una con alto |delta| e prezzo fermo è "assorbimento". |
| Clustering di ordini limite/stop su numeri tondi, barriere di prezzo | Osler — [Currency Orders and Exchange Rate Dynamics](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=447361); Cellier, Bourghelle — [Limit Order Clustering and Price Barriers (Euronext)](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID966454_code762440.pdf?abstractid=966454) | Take-profit si ammassano *sul* livello (inversioni), stop *oltre* il livello (movimento rapido dopo il breakout). Flag `RoundNumber` come attributo (prior), da validare. |
| HFT "si appoggia" agli ordini istituzionali a pezzi, poi li segue se informati | van Kervel, Menkveld — [HFT around Large Institutional Orders](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2619686); Korajczyk, Murphy — [HF Market Making to Large Institutional Trades](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2567016) | Impronta = volume elevato a un prezzo con flusso aggressivo prevalentemente da un lato ma prezzo che non avanza (liquidità passiva che assorbe). Si misura con `z_I` + efficienza. |
| Tossicità del flusso in volume-time | Easley, López de Prado, O'Hara — [Flow Toxicity and Liquidity in a High Frequency World](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1695596) (critica: Andersen, Bondarenko — [VPIN and the Flash Crash](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1881731)) | Normalizzare per volume, non per tempo. Cautela: VPIN è correlato per costruzione a volume/volatilità → non lo usiamo come segnale, solo come idea di volume-clock. |
| Test multipli | Harvey, Liu, Zhu — [...and the Cross-Section of Expected Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314); Bailey, López de Prado — [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551) | Controllo FDR (Benjamini–Hochberg) sui candidati-zona di ogni sessione e *alpha-spending* sui tocchi ripetuti. |

Limite dei dati: su ATAS il footprint storico (Ask/Bid volume per prezzo) è disponibile; la **profondità storica del DOM no** (solo live o
se registrata). Quindi l'"imbalance" dello spec è l'**imbalance eseguito** (aggressori buy vs sell per livello), proxy dell'OFI di Cont et al.;
lo sbilancio del book passivo è un modulo opzionale live (§6).

---

## 2. Qualificazione della zona (1 minuto, sessione NY)

Notazione: tick `τ = 0.25`; per barra chiusa `t` e livello `p`: `A_t(p)` volume ask-hit (buy aggressor), `B_t(p)` bid-hit (sell aggressor).
Profilo di sessione cumulato: `A(p)=Σ_t A_t(p)`, `B(p)=Σ_t B_t(p)`, `V=A+B`, `D=A−B`. Azzerato alle 09:30 ET.

**(a) Massa (high-volume node).**
1. Smoothing triangolare ±K tick: `Ṽ(p)=Σ_k w_k V(p+kτ)` (K=2).
2. z robusto cross-sezionale: `z_V(p) = (Ṽ(p) − med(Ṽ)) / (1.4826·MAD(Ṽ))`.
3. Candidato = massimo locale con distanza minima tra picchi ≥ 8 tick e `z_V ≥ 2`.
4. p-value `p_i = 1 − Φ(z_V)`; **Benjamini–Hochberg** sui `m` candidati della barra a livello `q = 0.05`: si tiene il massimo `k` con `p_(k) ≤ (k/m)·q`.
5. Estremi zona `[L,U]`: livelli contigui con `Ṽ ≥ 0.5·Ṽ_peak`, larghezza massima 12 tick.

**(b) Sbilancio eseguito sul nodo.** Con `A_z=ΣA`, `B_z=ΣB` nella zona:
`z_I = (A_z − B_z) / sqrt(φ·V_z)`.
Sotto H0 (buy/sell 50/50, binomiale) `φ=1`, ma i volumi sono fortemente auto-correlati/overdispersi: **φ è stimato in-session** come
`φ = median_p[ (D(p)²/V(p)) ] / 0.455` (0.455 = mediana di χ²₁). Qualificata se `|z_I| ≥ 2`. Segno `s = sign(D_z)` = lato dominante.

**(c) Qualifica.** Zona **Qualified** ⇔ passa BH su (a) **e** `|z_I| ≥ 2` **e** sono trascorse ≥ 15 barre dalle 09:30 (profilo stabile).
Score informativo: `S = min(z_V, z_cap) + min(|z_I|, z_cap)`, `z_cap=6` (evita che un solo outlier domini).

**(d) Attributi (non filtri).**
- `Round`: distanza dal multiplo di 25/50/100 punti ≤ 2 tick (Osler, Cellier). Valore marginale da misurare, non dato per scontato.
- `Type` (opzionale, estensione): su `n` barre di formazione, efficienza `E = |ΔP| / (σ₁ₘ·√n)` e `|D_z|/V_z`. Alto |D|, E bassa → *assorbimento* (impronta HFT/istituzionale); alto |D|, E alta → *impatto* (componente transitoria che tende a decadere).

**(e) Che cosa significa "continuazione" (solo etichetta statistica).**
Al tocco da un lato (approccio da sotto/sopra), esito osservato entro `H=10` barre: chiusura oltre il bordo opposto di `k·ATR₀` (k=0.5) → *continuazione*; chiusura oltre il bordo di approccio di `k·ATR₀` → *rigetto*; altrimenti *neutro* (escluso dal binomiale). Nessuna decisione di trading: serve a stimare `P(continuazione | zona, n° tocco, allineamento)`.
"Allineata" = il lato dominante `s` coincide con la direzione di approccio.

---

## 3. Test multipli e memoria della zona

**Tocco.** Una barra *tocca* se `Low ≤ U` e `High ≥ L`. Un tocco conta come nuovo solo se la zona era "armata": il prezzo si è prima allontanato di ≥ `1.0·ATR₁ₘ(14)` (isteresi, evita di contare 5 barre consecutive dentro la zona come 5 test).

**Consumo di liquidità.** Ogni barra dentro la zona consuma massa: `C_n = Σ volume scambiato nella zona dopo la formazione`. Massa residua `M_n = max(V_z − C_n, 0)`.
`z_V^{eff}(n) = (Ṽ_peak·M_n/V_z − med₀)/(1.4826·MAD₀)` (picco smussato alla formazione scalato per la frazione di massa residua; med/MAD congelati).

**Alpha-spending sui tocchi ripetuti** (stessa ipotesi guardata più volte → niente inflazione dell'evidenza):
`α_n = α · 2^−(n+1)`, α=0.05 ⇒ 2.5%, 1.25%, 0.625%, … e `Σ α_n = α`.
La zona resta **Qualified** al tocco `n` solo se `p_BH` ricalcolato su `z_V^{eff}(n)` è ≤ `α_n`; altrimenti passa a **Weakened** (grigia).

**Scadenza (Expired).** `C_n ≥ κ·V_z` (κ=1.5) oppure `n > N_max` (3) oppure fine sessione. Nessun riporto automatico al giorno dopo (il profilo è di sessione; il riporto richiederebbe un test separato con le sue α).

**Memoria empirica (Beta–Binomiale).** Per classe `c = (allineata?, min(n,3))`: successi `s_c` (continuazioni), fallimenti `f_c` (rigetti).
Posterior `Beta(a₀+s_c, b₀+f_c)` con prior debole `a₀=b₀=5` (nessun edge assunto). Si mostra media posteriore e **limite credibile inferiore al 5%**; un'etichetta "edge" compare solo se il LCB>0.5, e con correzione per il numero di classi testate (Bonferroni sul numero di classi, qui 6). Attenzione al data-snooping: ogni nuova soglia provata va conteggiata come test (Bailey–López de Prado). Validazione consigliata: walk-forward, soglie fissate su un periodo e misurate su uno successivo.

---

## 4. Specifiche indicatore ATAS

Implementazione di riferimento: [`indicators/atas/NqQualifiedZones.cs`](../indicators/atas/NqQualifiedZones.cs).

Flusso (solo su barre **chiuse**, per evitare ricalcoli della barra viva):
```
OnCalculate(bar):
  if bar == 0: Reset()
  if bar < 1 or bar-1 == lastProcessed: return
  c = GetCandle(bar-1)
  if !InNySession(c.Time): return;  if new session date: ResetSession()
  profile += c.GetAllPriceLevels()          # Ask/Bid per prezzo
  UpdateATR(c)
  UpdateExistingZones(c)                    # tocchi, consumo, alpha-spending, scadenza, esiti
  if barsInSession >= MinBars: DetectNewZones()   # §2 a-c, BH
OnRender: per zona -> rettangolo [L,U] da FormBar a barra corrente
          colore per stato (Qualified / Weakened / Expired-ghost), freccia di lato dominante, etichetta "T<n> z=.. p̂=.."
```
Parametri esposti: `ChartTimeOffsetHours`, `SmoothK`, `ZMin`, `FdrQ`, `ZIMin`, `MinBars`, `Kappa`, `MaxTouches`, `AlphaTotal`, `HorizonBars`, `OutcomeAtrK`, `ShowExpired`.

Da verificare sull'SDK ATAS reale prima dell'uso: firme di `OnRender`/`RenderContext`, `ChartInfo.GetXByBar/GetYByPrice`, `GetAllPriceLevels()`, e il fuso orario di `candle.Time`.

---

## 5. Cosa NON fa
Nessun segnale, ingresso, uscita, stop, target o sizing. Le zone sono una mappa condizionale; il tracker (§3) dice solo con quale frequenza osservata il prezzo ha continuato o rigettato dopo i tocchi.

## 6. Estensioni
Sbilancio del book passivo live (`MarketDepthChanged`, OFI di Cont et al. sui livelli 1–10 come Cao et al.), classificazione assorbimento/impatto (§2d), serializzazione su disco delle statistiche Beta per accumulare campione tra sessioni, deseasonalizzazione del volume per minuto del giorno.
