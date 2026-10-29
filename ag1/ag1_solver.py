#!/usr/bin/env python3
"""Risolutore di Analisi e Geometria 1 (Politecnico di Milano): esercizi del PDF, temi d'esame e esercizi nuovi.

    python ag1_solver.py esercizi            # i 40 esercizi del PDF, con confronto
    python ag1_solver.py temi                # esercizi dei temi d'esame, con confronto
    python ag1_solver.py studio "x*exp(-abs(x))"
    python ag1_solver.py --help              # tutti i comandi
"""
import sys

from ag1lib.cli import main

if __name__ == "__main__":
    sys.exit(main())
