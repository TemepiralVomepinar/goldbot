# Risolutore Analisi e Geometria 1 (Politecnico di Milano)

Programma Python (sympy) che risolve **i 40 esercizi del PDF** *Esercizi AG1 – prima prova in itinere* e
gli **esercizi dei temi d'esame** degli anni precedenti, e che si può usare su **esercizi nuovi dello stesso tipo**.
Ogni risultato dei PDF/temi viene confrontato con la soluzione ufficiale.

```bash
pip install -r requirements.txt
python ag1_solver.py --help
```

## Cosa copre

| Argomento | Comando |
|---|---|
| 40 esercizi del PDF (con confronto) | `esercizi` (`esercizi 14 25`, `--test`, `--lista`) |
| Esercizi dei temi d'esame (con confronto) | `temi` (`temi --lista`, `temi app_9_6_26`) |
| Studio di funzione completo (dominio, segno, limiti, asintoti, f', non derivabilità, monotonia, estremi, f'', flessi, immagine, n° zeri, grafico). Gestisce `abs`, radici cubiche/dispari, `Piecewise` | `studio "x^(4/3)*(2-x)^(1/3)"` |
| Estremi assoluti su un intervallo | `estremi "atan(x+log(x)-1)" 1 5` |
| Limiti (funzioni e successioni), ordine di infinitesimo, Taylor | `limite`, `ordine`, `taylor` |
| Limiti con parametro: "per quali α vale 3?", "per quali a esiste finito non nullo?" | `limite-param`, `limite-esp` |
| Continuità/derivabilità di funzioni a tratti con parametri | `raccordo` |
| Successioni, sup/inf/max/min, ricorrenze, insiemi di R, famiglie di intervalli | `successione`, `ricorrenza`, `insieme`, `famiglia` |
| Numeri complessi: forme, equazioni (anche con `abs`, `conj`, `re`), radici, regioni del piano di Gauss | `complesso`, `eq-complessa`, `radici`, `regione` |
| Integrali (primitive, definiti, impropri con criterio di convergenza), area, funzione integrale | `integrale`, `area`, `funzione-integrale` |
| Convergenza di integrali impropri al variare di un parametro | `conv-param` |
| Equazioni differenziali (1° ordine lineari/separabili, 2° ordine), problema di Cauchy, andamento locale | `edo` |
| Curve: regolarità, biregolarità, lunghezza, chiusa, semplice, piana, retta tangente, piano osculatore, integrale di linea | `curva`, `semplice`, `tangente`, `osculatore`, `linea` |
| Geometria in R³: rette, piani, posizioni reciproche, distanze, angoli, aree, condizioni con parametro | `geo` (`geo aiuto`) |
| Teoria: definizioni, enunciati e dimostrazioni dei teoremi ricorrenti | `teoria` (`teoria fermat`) |

## Esempi

```bash
python ag1_solver.py studio "exp(1/abs(x-1))*(x-1/4)"
python ag1_solver.py studio "Piecewise((cos(pi*exp(x)), x<0), ((2*x-1)*exp(-x^2), True))"
python ag1_solver.py limite-param "n^2*(exp(a/n)-a/n-cos(1/n))" --param a --var n --punto oo --valore 3
python ag1_solver.py limite-esp "sin(x)" "1-cos(x)"                 # per quali a il limite vale 0?
python ag1_solver.py insieme "cos(pi/(x-1)) = -1"                   # sup/inf/max/min
python ag1_solver.py eq-complessa "abs(z-1) = conj(z) - i"
python ag1_solver.py regione "1<=abs(z)<=2 and 0<=arg(z)<=pi/3"
python ag1_solver.py conv-param "exp(a*x)/(exp(x)+1)" -oo oo --param a   # converge sse 0<a<1
python ag1_solver.py integrale "x/sqrt(x^2+9)" 0 4
python ag1_solver.py edo "y' = y + x" --x0 0 --y0 0                  # soluzione e punto stazionario
python ag1_solver.py curva "2*exp(t), exp(-t), 2*t" 0 "log(2)"
python ag1_solver.py linea "cos(t),sin(t)" "x/(1+y^2)" 0 "pi/2"
python ag1_solver.py geo posizione-rette "3,1,1;-2,-1,0" "1,0,1;-1,1,-1"
python ag1_solver.py geo ortogonali "(1,a,2)" "(-1,2,1)" "(a-4,-3,a+2)"
python ag1_solver.py geo angolo "(1,0,t)" "(0,2,2)" --angolo "pi/3"
python ag1_solver.py teoria "valori intermedi"
```

Sintassi delle espressioni: `^` o `**`, moltiplicazione implicita (`2x`), `ln`/`log`, `tg`, `arctg`, `sen`, `abs`,
`cbrt`, `e`, `pi`, `i` (per i complessi), `oo`. I grafici vengono salvati in `output/`.

## Struttura

```
ag1_solver.py            punto d'ingresso
ag1lib/funzioni.py       motore di studio di funzione
ag1lib/successioni.py    insiemi, successioni, limiti con parametro, raccordi
ag1lib/complessi.py      numeri complessi
ag1lib/integrali.py      integrali, equazioni differenziali, curve
ag1lib/geometria.py      geometria in R^3
ag1lib/teoria.py         enunciati e dimostrazioni
ag1lib/esercizi_pdf.py   i 40 esercizi del PDF
ag1lib/temi.py           esercizi dei temi d'esame con le soluzioni ufficiali
```

## Limiti noti

- Le domande di teoria "a scelta multipla" puramente concettuali (es. "quale affermazione è falsa") non si risolvono
  con il calcolo: per quelle c'è il comando `teoria`.
- Funzioni con infiniti punti critici (es. `e^-|x| sin x`) vengono studiate solo in modo parziale.
- I criteri di convergenza degli integrali impropri sono quelli del confronto/asintotico; per integrandi che
  oscillano (seni/coseni senza decadimento) il risultato va controllato a mano.
- Gli esercizi di dimostrazione (4, 17, 29, 32 del PDF) stampano lo schema della dimostrazione e verificano i passaggi.
- Es. 28(c): per |x²−1| in x=±1 le derivate unilaterali sono −2 (sinistra) e +2 (destra) in entrambi i punti; nel PDF
  sono scritte in forma sintetica ("±2 e ∓2").
