"""Simboli, stampa e verifica condivisi da tutti i moduli."""
import os

import sympy as sp
from sympy import Abs, I, Interval, Rational, S, Symbol, Union, oo

# ---------------------------------------------------------------- simboli ----
x = Symbol("x", real=True)
xp = Symbol("xp", positive=True)
n = Symbol("n", integer=True, positive=True)
k = Symbol("k", integer=True, nonnegative=True)
t = Symbol("t", real=True)
OUT_DIR = os.environ.get("AG1_OUT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"))

ESITI = []  # (esercizio, etichetta, ok)
_corrente = [0]
SOLO_TITOLO = [False]


class FineTitolo(Exception):
    pass


def titolo(num, testo):
    _corrente[0] = num
    if SOLO_TITOLO[0]:
        print(f"{str(num):>4}. {testo}")
        raise FineTitolo
    print(f"\n{'=' * 74}\nEsercizio {num}: {testo}\n{'=' * 74}")


def riga(*a):
    print("   ", *a)


def sezione(testo):
    print(f"  -- {testo}")


# --------------------------------------------------------------- confronti ----
def num(v):
    return complex(sp.N(v, 30))


def uguali(a, b, tol=1e-9):
    """Confronto robusto fra risultati sympy / liste / insiemi / intervalli."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(uguali(p, q, tol) for p, q in zip(a, b))
    if isinstance(a, Union) or isinstance(b, Union):
        if not (isinstance(a, Union) and isinstance(b, Union)):
            return False
        return uguali(sorted(a.args, key=lambda s: num(s.inf).real),
                      sorted(b.args, key=lambda s: num(s.inf).real), tol)
    if isinstance(a, Interval) and isinstance(b, Interval):
        return (a.left_open == b.left_open and a.right_open == b.right_open and
                uguali(a.start, b.start, tol) and uguali(a.end, b.end, tol))
    if isinstance(a, sp.FiniteSet) and isinstance(b, sp.FiniteSet):
        return uguali(sorted(a, key=lambda v: num(v).real), sorted(b, key=lambda v: num(v).real), tol)
    if isinstance(a, (str, bool)) or isinstance(b, (str, bool)):
        return a == b
    try:
        a, b = sp.sympify(a), sp.sympify(b)
        if a in (oo, -oo) or b in (oo, -oo):
            return a == b
        return abs(num(a - b)) < tol
    except Exception:
        return a == b


def complessi_uguali(lista_a, lista_b, tol=1e-8):
    """Uguaglianza fra insiemi di numeri complessi (a meno dell'ordine)."""
    a = [num(v) for v in lista_a]
    b = [num(v) for v in lista_b]
    if len(a) != len(b):
        return False
    return all(any(abs(p - q) < tol for q in b) for p in a)


def registra(etichetta, ok, atteso=None):
    ESITI.append((_corrente[0], etichetta, ok))
    segno = "OK  (= soluzione)" if ok else f"DIVERSO dalla soluzione! atteso: {atteso}"
    riga(f"[{segno}] {etichetta}")
    return ok


def verifica(etichetta, calcolato, atteso):
    return registra(etichetta, uguali(calcolato, atteso), atteso)


def verifica_complessi(etichetta, calcolati, attesi):
    return registra(etichetta, complessi_uguali(calcolati, attesi), attesi)


# ----------------------------------------------------------------- utilita' ----
def s(v):
    """Semplifica un valore (espande prima, cosi' (-1+(1+sqrt2)^2) -> 1+2*sqrt2)."""
    return sp.simplify(sp.expand(v))


def lim(e, var, punto, direzione=None):
    if direzione is None and punto not in (oo, -oo):
        direzione = "+-"
    r = sp.limit(e, var, punto, direzione) if direzione else sp.limit(e, var, punto)
    return sp.simplify(r)


def parse(espr, **extra):
    """Testo -> espressione sympy (accetta ^, moltiplicazione implicita, ln, tg, arctg, sen, e)."""
    from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication_application, parse_expr,
                                            standard_transformations)
    tr = standard_transformations + (implicit_multiplication_application, convert_xor)
    loc = {"x": x, "t": t, "n": n, "e": sp.E, "ln": sp.log, "tg": sp.tan, "arctg": sp.atan, "sen": sp.sin,
           "I": I, "i": I, "abs": sp.Abs, "sgn": sp.sign, "oo": oo, "inf": oo, "pi": sp.pi,
           "cbrt": lambda v: sp.Pow(v, Rational(1, 3)), "radice": sp.sqrt, "log": sp.log,
           "arcsin": sp.asin, "arccos": sp.acos, "atan": sp.atan, "sinh": sp.sinh, "cosh": sp.cosh}
    loc.update(extra)
    return parse_expr(espr.replace("|", "|"), local_dict=loc, transformations=tr)


def ordina(valori):
    return sorted(valori, key=lambda v: float(sp.N(v)))
