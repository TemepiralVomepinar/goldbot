# Risolutore Analisi e Geometria 1 (prima prova in itinere)

`ag1_solver.py` risolve con **sympy** tutti i 40 esercizi del PDF *Esercizi AG1 – prima prova*
(estremi e induzione, complessi, funzioni, successioni, limiti, continuità, derivate,
teoremi, Taylor, studio di funzione) e **confronta ogni risultato con la soluzione del PDF**
(80 controlli; `--test` termina con codice 0 solo se coincidono tutti).

```bash
pip install -r requirements.txt
python ag1_solver.py              # tutti gli esercizi, con i passaggi
python ag1_solver.py 14 25 37     # solo alcuni
python ag1_solver.py --lista      # elenco
python ag1_solver.py --test       # controllo silenzioso contro il PDF
```

I grafici (studi di funzione, regioni nel piano di Gauss) vanno in `output/`.

## Strumenti generici (per esercizi nuovi dello stesso tipo)

```bash
python ag1_solver.py limite "sin(x)/x" --punto 0
python ag1_solver.py limite "(1+2/n)**(3*n)" --var n --punto oo
python ag1_solver.py derivata "log(x+sqrt(x**2+1))"
python ag1_solver.py taylor "exp(x)*sin(x)" --ordine 3
python ag1_solver.py asintoti "x*exp(1/x)"
python ag1_solver.py radici -- "-8*I" 3
python ag1_solver.py studio "x*exp(-x)"
```

## Note

- Gli esercizi di dimostrazione (4, 17, 29, 32) stampano lo schema della dimostrazione e
  verificano con sympy/numericamente i passaggi chiave.
- Es. 28(c): per |x²−1| in x=±1 le derivate unilaterali sono −2 (sinistra) e +2 (destra) in
  entrambi i punti; nel PDF sono scritte in forma sintetica ("±2 e ∓2").
