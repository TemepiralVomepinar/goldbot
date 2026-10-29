"""Geometria analitica nello spazio R^3: vettori, rette, piani, distanze, angoli, posizioni reciproche.
Accetta parametri simbolici (es. a, alpha) e risolve le condizioni su di essi."""
import re

import sympy as sp
from sympy import Matrix, Rational, S, sqrt

from .util import parse, riga

X, Y, Z = sp.symbols("x y z", real=True)
_s, _u = sp.symbols("s u", real=True)
_PAR = {}


def _simb(espr):
    """parse con x,y,z coordinate e parametri reali creati al volo."""
    nomi = set(re.findall(r"[A-Za-z_]\w*", espr)) - {"x", "y", "z", "sqrt", "pi", "e", "exp", "sin", "cos", "tan", "log",
                                                      "ln", "atan", "abs", "cbrt", "I", "i", "oo"}
    loc = {"x": X, "y": Y, "z": Z}
    for n_ in nomi:
        loc[n_] = _PAR.setdefault(n_, sp.Symbol(n_, real=True))
    return parse(espr, **loc)


def vec(testo):
    """'(1,-3,2)' o '1,-3,2' -> Matrix colonna (anche con parametri)."""
    t_ = testo.strip().strip("()[]")
    parti = re.split(r",(?![^()]*\))", t_)
    return Matrix([_simb(p_) for p_ in parti])


def _isnull(v):
    return all(sp.simplify(c) == 0 for c in v)


def _fmt(v):
    return "(" + ", ".join(str(sp.simplify(c)) for c in v) + ")"


def _norm(v):
    return sp.simplify(sqrt(sp.simplify(v.dot(v))))


def _pulisci(e):
    return sp.simplify(e)


# ------------------------------------------------------------------ piani ----
def piano_da_equazione(testo):
    """'2x+y-2z=-5' -> (n, d) con n·(x,y,z) = d."""
    if "=" in testo:
        l, r = testo.split("=", 1)
        e = _simb(l) - _simb(r)
    else:
        e = _simb(testo)
    e = sp.expand(e)
    n_ = Matrix([e.coeff(X), e.coeff(Y), e.coeff(Z)])
    d = -(e - n_[0] * X - n_[1] * Y - n_[2] * Z)
    return n_, sp.simplify(d)


def _norm_piano(n_, d):
    n_ = Matrix([sp.simplify(c) for c in n_])
    d = sp.simplify(d)
    if all(c.is_Rational for c in list(n_) + [d]):
        den = sp.ilcm(*[c.q for c in list(n_) + [d]])
        vals = [int(c * den) for c in n_] + [int(d * den)]
        g = sp.igcd(*vals) or 1
        n_, d = Matrix([sp.Integer(v // g) for v in vals[:3]]), sp.Integer(vals[3] // g)
    else:
        try:   # coefficienti non razionali (es. con pi): divide per il MCD simbolico
            g = sp.gcd_list([c for c in list(n_) + [d] if c != 0])
            if g not in (0, 1) and g.is_number:
                n_, d = (n_ / g).applyfunc(sp.simplify), sp.simplify(d / g)
        except Exception:
            pass
    primo = next((c for c in n_ if c != 0), 1)
    try:
        if primo < 0:
            n_, d = -n_, -d
    except TypeError:
        pass
    return n_, d


def str_piano(n_, d):
    n_, d = _norm_piano(n_, d)
    termini = []
    for c, v in zip(n_, "xyz"):
        if c == 0:
            continue
        coef = "" if c == 1 else ("-" if c == -1 else (f"({c})*" if c.is_Add else f"{c}*"))
        termini.append(coef + v)
    return (" + ".join(termini).replace("+ -", "- ") or "0") + f" = {d}"


def retta_per_punti(P, Q, stampa=True):
    P, Q = vec(P), vec(Q)
    d = (Q - P).applyfunc(sp.simplify)
    return retta_param(P, d, stampa)


def retta_param(P, d, stampa=True):
    par = [sp.simplify(P[i] + _s * d[i]) for i in range(3)]
    if stampa:
        riga(f"punto P = {_fmt(P)}, direzione d = {_fmt(d)}")
        riga("equazioni parametriche: " + ", ".join(f"{n_} = {e}" for n_, e in zip("xyz", par)) + "   (s in R)")
        nz = [i for i in range(3) if d[i] != 0]
        if len(nz) == 3:
            riga("forma simmetrica: " + " = ".join(f"({n_} - {P[i]})/{d[i]}" for i, n_ in enumerate("xyz")))
        # due piani che la contengono
        e1 = d.cross(Matrix([1, 0, 0])) if not _isnull(d.cross(Matrix([1, 0, 0]))) else d.cross(Matrix([0, 1, 0]))
        e2 = d.cross(e1)
        riga("equazioni cartesiane (intersezione di due piani): "
             f"{str_piano(e1, e1.dot(P))};  {str_piano(e2, e2.dot(P))}")
    return par


def retta_da_piani(eq1, eq2, stampa=True):
    n1, d1 = piano_da_equazione(eq1)
    n2, d2 = piano_da_equazione(eq2)
    dirz = n1.cross(n2).applyfunc(sp.simplify)
    if _isnull(dirz):
        if stampa:
            riga("i piani sono paralleli (normali proporzionali): intersezione vuota o piani coincidenti")
        return None
    sol = None
    for libera in (Y, X, Z):
        altre = [v for v in (X, Y, Z) if v != libera]
        try:
            sol = sp.solve([n1.dot(Matrix([X, Y, Z])) - d1, n2.dot(Matrix([X, Y, Z])) - d2, libera - _s], [X, Y, Z], dict=True)
            if sol:
                break
        except Exception:
            continue
    if stampa:
        riga(f"direzione d = n1 x n2 = {_fmt(dirz)}")
        if sol:
            sol = sol[0]
            riga("equazioni parametriche: " + ", ".join(f"{n_} = {sp.simplify(sol[v])}" for n_, v in zip("xyz", (X, Y, Z))) + "   (s in R)")
    return dirz, sol


def piano_tre_punti(P, Q, R, stampa=True):
    P, Q, R = vec(P), vec(Q), vec(R)
    n_ = (Q - P).cross(R - P).applyfunc(sp.simplify)
    if stampa:
        riga(f"PQ x PR = {_fmt(n_)}" + ("  (punti ALLINEATI: non c'e' un solo piano)" if _isnull(n_) else ""))
        riga("piano:", str_piano(n_, n_.dot(P)))
    return n_, n_.dot(P)


def piano_punto_normale(P, n_, stampa=True):
    P, n_ = vec(P), vec(n_)
    if stampa:
        riga("piano:", str_piano(n_, n_.dot(P)))
    return n_, n_.dot(P)


def piano_retta_punto(P0, d, R, stampa=True):
    """Piano che contiene la retta (P0,d) e il punto R."""
    P0, d, R = vec(P0), vec(d), vec(R)
    n_ = d.cross(R - P0).applyfunc(sp.simplify)
    if stampa:
        riga(f"normale = d x P0R = {_fmt(n_)}")
        riga("piano:", str_piano(n_, n_.dot(P0)))
    return n_, n_.dot(P0)


def piano_due_rette(P1, d1, P2, d2, stampa=True):
    """Piano contenente due rette (incidenti o parallele)."""
    P1, d1, P2, d2 = vec(P1), vec(d1), vec(P2), vec(d2)
    n_ = d1.cross(d2)
    if _isnull(n_):
        n_ = d1.cross(P2 - P1)
    n_ = n_.applyfunc(sp.simplify)
    if stampa:
        riga(f"normale = {_fmt(n_)}")
        riga("piano:", str_piano(n_, n_.dot(P1)))
    return n_, n_.dot(P1)


# --------------------------------------------------------------- posizioni ----
def posizione_rette(P1, d1, P2, d2, stampa=True):
    P1, d1, P2, d2 = vec(P1), vec(d1), vec(P2), vec(d2)
    c = d1.cross(d2).applyfunc(sp.simplify)
    w = (P2 - P1).applyfunc(sp.simplify)
    out = {}
    if _isnull(c):
        coincid = _isnull(w.cross(d1))
        out["tipo"] = "coincidenti" if coincid else "parallele (distinte)"
        if stampa:
            riga(f"d1 x d2 = {_fmt(c)} = 0: direzioni PARALLELE")
            riga("le rette sono " + out["tipo"] + (f"; distanza = {sp.simplify(_norm(w.cross(d1)) / _norm(d1))}" if not coincid else ""))
        return out
    tripl = sp.simplify(w.dot(c))
    if tripl == 0:
        sol = sp.solve([P1[i] + _s * d1[i] - P2[i] - _u * d2[i] for i in range(3)], [_s, _u], dict=True)
        pt = None
        if sol:
            pt = [sp.simplify((P1[i] + _s * d1[i]).subs(sol[0])) for i in range(3)]
        out["tipo"] = "incidenti"
        out["punto"] = pt
        if stampa:
            riga(f"d1 x d2 = {_fmt(c)} != 0 e (P2-P1)·(d1 x d2) = 0: rette COPLANARI e non parallele => INCIDENTI")
            if pt:
                riga(f"punto di intersezione: {_fmt(pt)}")
            ang = sp.acos(sp.Abs(d1.dot(d2)) / (_norm(d1) * _norm(d2)))
            riga(f"angolo fra le rette: {sp.simplify(ang)}  (~ {sp.N(ang, 6)} rad)")
    else:
        out["tipo"] = "sghembe"
        out["distanza"] = sp.simplify(sp.Abs(tripl) / _norm(c))
        if stampa:
            riga(f"d1 x d2 = {_fmt(c)} != 0 e (P2-P1)·(d1 x d2) = {tripl} != 0 => SGHEMBE")
            riga(f"distanza fra le rette = |(P2-P1)·(d1 x d2)| / |d1 x d2| = {out['distanza']}  (~ {sp.N(out['distanza'], 6)})")
        if tripl.free_symbols:
            riga("condizione di complanarita' sul parametro:", sp.solve(tripl, list(tripl.free_symbols)))
    return out


# ------------------------------------------------------------------ distanze ----
def distanza_punto_piano(P, eq, stampa=True):
    P = vec(P)
    n_, d = piano_da_equazione(eq)
    dist = sp.simplify(sp.Abs(n_.dot(P) - d) / _norm(n_))
    H = (P - ((n_.dot(P) - d) / n_.dot(n_)) * n_).applyfunc(sp.simplify)
    if stampa:
        riga(f"d(P, piano) = |n·P - d|/|n| = |{sp.simplify(n_.dot(P) - d)}|/{_norm(n_)} = {dist}   (~ {sp.N(dist, 6)})")
        riga(f"proiezione ortogonale di P sul piano: H = {_fmt(H)}")
    return dist, H


def distanza_punto_retta(P, P0, d, stampa=True):
    P, P0, d = vec(P), vec(P0), vec(d)
    dist = sp.simplify(_norm((P - P0).cross(d)) / _norm(d))
    s0 = sp.simplify((P - P0).dot(d) / d.dot(d))
    H = (P0 + s0 * d).applyfunc(sp.simplify)
    if stampa:
        riga(f"d(P, retta) = |(P-P0) x d| / |d| = {dist}   (~ {sp.N(dist, 6)})")
        riga(f"piede della perpendicolare: H = {_fmt(H)}")
    return dist, H


def distanza_piani(eq1, eq2, stampa=True):
    n1, d1 = piano_da_equazione(eq1)
    n2, d2 = piano_da_equazione(eq2)
    if not _isnull(n1.cross(n2)):
        if stampa:
            riga("i piani non sono paralleli: si intersecano in una retta (distanza 0)")
        return 0
    k_ = sp.simplify(n2[next(i for i in range(3) if n1[i] != 0)] / n1[next(i for i in range(3) if n1[i] != 0)])
    dist = sp.simplify(sp.Abs(d2 - k_ * d1) / _norm(n2))
    if stampa:
        riga(f"piani paralleli: distanza = {dist}  (~ {sp.N(dist, 6)})")
    return dist


# ----------------------------------------------------------------- angoli ----
def angolo_vettori(u, v, stampa=True, uguale_a=None):
    """Angolo fra due vettori; con parametri e uguale_a (es. 'pi/3') trova i valori del parametro."""
    u, v = vec(u), vec(v)
    c = sp.simplify(u.dot(v) / (_norm(u) * _norm(v)))
    ang = sp.acos(c)
    if stampa:
        riga(f"u·v = {sp.simplify(u.dot(v))}, |u| = {_norm(u)}, |v| = {_norm(v)}, cos(theta) = {c}")
        if ang.free_symbols:
            riga(f"theta = {sp.simplify(ang)}")
        else:
            riga(f"theta = {sp.simplify(ang)}   (~ {sp.N(ang, 6)} rad = {sp.N(ang * 180 / sp.pi, 6)} gradi)")
        riga("ortogonali" if u.dot(v) == 0 else ("paralleli" if _isnull(u.cross(v)) else "ne' ortogonali ne' paralleli")
             if not ang.free_symbols else "(dipende dal parametro)")
    if uguale_a is not None and ang.free_symbols:
        th = sp.sympify(_simb(uguale_a))
        par = sorted(ang.free_symbols, key=str)
        sol = [r for r in sp.solve(sp.Eq(c, sp.cos(th)), par) if abs(sp.im(sp.N(r[0] if isinstance(r, tuple) else r))) < 1e-12]
        # verifica: l'angolo (non solo il coseno) deve valere th
        buone = []
        for r in sol:
            rv = r[0] if isinstance(r, tuple) else r
            if abs(sp.N(ang.subs(par[0], rv)) - sp.N(th)) < 1e-9:
                buone.append(rv)
        if stampa:
            riga(f"angolo = {th} per {par[0]} in {buone if buone else 'nessun valore'}")
        return ang, buone
    return ang


def angolo_retta_piano(d, eq, stampa=True):
    d = vec(d)
    n_, _ = piano_da_equazione(eq)
    sn = sp.simplify(sp.Abs(d.dot(n_)) / (_norm(d) * _norm(n_)))
    ang = sp.asin(sn)
    if stampa:
        riga(f"sin(theta) = |d·n|/(|d||n|) = {sn}  ->  theta = {sp.simplify(ang)}  (~ {sp.N(ang, 6)} rad)")
    return ang


def angolo_piani(eq1, eq2, stampa=True):
    n1, _ = piano_da_equazione(eq1)
    n2, _ = piano_da_equazione(eq2)
    c = sp.simplify(sp.Abs(n1.dot(n2)) / (_norm(n1) * _norm(n2)))
    ang = sp.acos(c)
    if stampa:
        riga(f"cos(theta) = |n1·n2|/(|n1||n2|) = {c} -> theta = {sp.simplify(ang)}  (~ {sp.N(ang, 6)} rad)")
    return ang


# ---------------------------------------------------------- aree / volumi ----
def area_triangolo(P, Q, R, stampa=True):
    P, Q, R = vec(P), vec(Q), vec(R)
    c = (Q - P).cross(R - P).applyfunc(sp.simplify)
    A = sp.simplify(_norm(c) / 2)
    if stampa:
        riga(f"PQ x PR = {_fmt(c)};  Area = |PQ x PR|/2 = {A}   (~ {sp.N(A, 6)})")
    return A


def prodotto_misto(u, v, w, stampa=True):
    u, v, w = vec(u), vec(v), vec(w)
    pm = sp.simplify(u.dot(v.cross(w)))
    if stampa:
        riga(f"u·(v x w) = {pm}  ->  " + ("COMPLANARI" if pm == 0 else "NON complanari") +
             f";  volume parallelepipedo = {sp.Abs(pm)}, tetraedro = {sp.Abs(pm) / 6}")
        if pm.free_symbols:
            riga("complanari se e solo se:", sp.solve(pm, list(pm.free_symbols)))
    return pm


def prodotti(u, v, stampa=True):
    u, v = vec(u), vec(v)
    c = u.cross(v).applyfunc(sp.simplify)
    if stampa:
        riga(f"u·v = {sp.simplify(u.dot(v))};   u x v = {_fmt(c)};   |u| = {_norm(u)},  |v| = {_norm(v)}")
    return u.dot(v), c


def condizioni(tipo, vettori, stampa=True):
    """Valori dei parametri per cui i vettori sono: ortogonali (a coppie), paralleli, complanari (3 vettori)."""
    vs = [vec(v) for v in vettori]
    if tipo == "ortogonali":
        eqs = [sp.simplify(vs[i].dot(vs[j])) for i in range(len(vs)) for j in range(i + 1, len(vs))]
    elif tipo == "paralleli":
        eqs = [sp.simplify(c) for i in range(len(vs)) for j in range(i + 1, len(vs)) for c in vs[i].cross(vs[j])]
    elif tipo == "complanari":
        eqs = [sp.simplify(vs[0].dot(vs[1].cross(vs[2])))]
    else:
        raise ValueError("tipo: ortogonali | paralleli | complanari")
    par = sorted(set().union(*[e.free_symbols for e in eqs]), key=str)
    sol = sp.solve(eqs, par, dict=True) if par else ([{}] if all(e == 0 for e in eqs) else [])
    if stampa:
        riga(f"condizioni ({tipo}): {eqs} = 0")
        riga("soluzioni:", sol if sol else "nessun valore del parametro")
    return sol


def vettore_parallelo_piano(v, eq, stampa=True):
    """Un vettore e' parallelo al piano iff v·n = 0."""
    v = vec(v)
    n_, _ = piano_da_equazione(eq)
    cond = sp.simplify(v.dot(n_))
    par = sorted(cond.free_symbols, key=str)
    sol = sp.solve(cond, par, dict=True) if par else None
    if stampa:
        riga(f"v·n = {cond} = 0  ->  {sol if par else ('parallelo' if cond == 0 else 'non parallelo')}")
    return sol


def appartenenza(P, eq, stampa=True):
    P = vec(P)
    n_, d = piano_da_equazione(eq)
    cond = sp.simplify(n_.dot(P) - d)
    par = sorted(cond.free_symbols, key=str)
    sol = sp.solve(cond, par, dict=True) if par else None
    if stampa:
        riga(f"n·P - d = {cond}  ->  " + (f"il punto appartiene al piano per {sol}" if par else ("APPARTIENE" if cond == 0 else "NON appartiene")))
    return sol


def retta_ortogonale_piano(P, eq, stampa=True):
    P = vec(P)
    n_, _ = piano_da_equazione(eq)
    return retta_param(P, n_, stampa)


def piano_punti_parallelo(P, Q, d, stampa=True):
    """Piano per i punti P e Q parallelo alla direzione d."""
    P, Q, d = vec(P), vec(Q), vec(d)
    n_ = (Q - P).cross(d).applyfunc(sp.simplify)
    if stampa:
        riga(f"normale = PQ x d = {_fmt(n_)}")
        riga("piano:", str_piano(n_, n_.dot(P)))
    return n_, n_.dot(P)


def retta_perp_incidente(P, P0, d, stampa=True):
    """Retta per P ortogonale e incidente alla retta (P0,d): passa per il piede H della perpendicolare."""
    Pv, P0v, dv = vec(P), vec(P0), vec(d)
    s0 = sp.simplify((Pv - P0v).dot(dv) / dv.dot(dv))
    H = (P0v + s0 * dv).applyfunc(sp.simplify)
    dirz = (H - Pv).applyfunc(sp.simplify)
    if stampa:
        riga(f"piede H = {_fmt(H)}, direzione PH = {_fmt(dirz)}" + ("  (P appartiene alla retta)" if _isnull(dirz) else ""))
    if not _isnull(dirz):
        return retta_param(Pv, dirz, stampa)
    return None
