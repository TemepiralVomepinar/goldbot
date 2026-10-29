"""Motore per lo studio di funzione reale di una variabile.

Gestisce: valore assoluto, radici di indice dispari (radice reale), funzioni a tratti (Piecewise),
logaritmi/esponenziali/arctan, parametri esclusi.  La funzione viene spezzata nei punti in cui cambia
"forma" (zeri/poli degli argomenti di |.|, di sign e delle basi delle radici dispari, soglie dei Piecewise);
su ogni tratto liscio si usano limiti, derivate e segni con sympy; i nodi (punti di raccordo ed estremi
del dominio) vengono classificati (continuita', derivabilita', asintoti verticali, flessi a tangente verticale).
"""
import os

import sympy as sp
from sympy import FiniteSet, Interval, Rational, S, Union, oo
from sympy.calculus.util import continuous_domain

from .util import OUT_DIR, num, ordina, riga, s, sezione, uguali, x as X


# ======================================================== preparazione ========
def realifica(expr, var=X):
    """b**(p/q) con q dispari  ->  sign(b)**(p mod 2) * |b|**(p/q)  (radice reale)."""
    def cond(e):
        if not e.is_Pow:
            return False
        b, ex = e.as_base_exp()
        return ex.is_Rational and ex.q > 1 and ex.q % 2 == 1 and b.has(var)

    def val(e):
        b, ex = e.as_base_exp()
        fattore = sp.sign(b) if ex.p % 2 else 1
        return fattore * sp.Abs(b) ** ex
    return expr.replace(cond, val)


def _zeri_reali(e, var):
    e = sp.simplify(e)
    if e.is_number:
        return []
    try:
        sol = sp.solveset(e, var, S.Reals)
        if isinstance(sol, FiniteSet):
            return [p for p in sol if p.is_real]
    except Exception:
        pass
    try:
        return [r for r in sp.Poly(e, var).real_roots()]
    except Exception:
        return []


def punti_di_rottura(expr, var=X):
    """Punti reali in cui cambia la forma di |.|, sign e Piecewise."""
    argomenti = [a.args[0] for a in expr.atoms(sp.Abs)] + [a.args[0] for a in expr.atoms(sp.sign)]
    for pw in expr.atoms(sp.Piecewise):
        for _, c in pw.args:
            for rel in c.atoms(sp.Rel):
                argomenti.append(rel.lhs - rel.rhs)
    punti = []
    for a in argomenti:
        num_, den_ = sp.fraction(sp.together(a))
        for e in (num_, den_):
            if e.has(var):
                punti += _zeri_reali(e, var)
    unici = []
    for p in ordina(punti):
        if not any(uguali(p, q) for q in unici):
            unici.append(sp.nsimplify(p) if p.is_Float else p)
    return unici


def _punto_prova(p, q):
    if p.is_finite and q.is_finite:
        return (p + q) / 2
    if p == -oo and q.is_finite:
        return q - 1
    if q == oo and p.is_finite:
        return p + 1
    return S.Zero


def _segno_in(b, var, m):
    v = sp.N(b.subs(var, m), 30)
    return 1 if v > 0 else (-1 if v < 0 else 0)


def specializza(expr, var, m):
    """Elimina Piecewise, |.| e sign valutando i segni nel punto di prova m."""
    def scegli(pw):
        for e, c in pw.args:
            if c == True or bool(c.subs(var, m)):  # noqa: E712
                return e
        return sp.nan
    e = expr.replace(lambda z: isinstance(z, sp.Piecewise), scegli)
    for _ in range(8):  # sympy puo' rigenerare Abs/sign dopo una sostituzione
        if not (e.atoms(sp.Abs) or e.atoms(sp.sign)):
            break
        e = e.replace(lambda z: isinstance(z, sp.Abs), lambda z: z.args[0] * (_segno_in(z.args[0], var, m) or 1))
        e = e.replace(lambda z: isinstance(z, sp.sign), lambda z: _segno_in(z.args[0], var, m))
    return e


def valore_in(f, var, c):
    """f(c) se finito e reale, altrimenti None."""
    try:
        v = f.subs(var, c)
        if v.has(sp.zoo, sp.nan, oo, -oo, sp.AccumBounds):
            return None
        v = sp.simplify(v)
        if v.has(sp.zoo, sp.nan, oo, -oo, sp.AccumBounds):
            return None
        if abs(sp.im(sp.N(v, 20))) > 1e-12:
            return None
        return sp.re(v) if v.has(sp.I) else v
    except Exception:
        return None


def limite(e, var, p, lato=None):
    try:
        if p in (oo, -oo):
            r = sp.limit(e, var, p)
        else:
            r = sp.limit(e, var, p, lato or "+-")
        if isinstance(r, sp.AccumBounds):
            return r
        return sp.simplify(r)
    except Exception:
        return sp.nan


def _fin(v):
    return v is not None and v.is_finite is True


# ============================================================ analisi =========
def _punti_test(a, b):
    if a.is_finite and b.is_finite:
        return [a + (b - a) / 3, a + 2 * (b - a) / 3, (a + b) / 2]
    if a.is_finite:
        return [a + 1, a + Rational(5, 2), a + 7]
    if b.is_finite:
        return [b - 1, b - Rational(5, 2), b - 7]
    return [S.Zero, S.One, -S.One]


def semplifica_reale(raw, var, a, b):
    """simplify(raw) solo se resta reale e uguale a raw sull'intervallo (a,b): evita (-1)**(1/3) spuri."""
    try:
        cand = sp.simplify(raw)
    except Exception:
        return raw
    if cand.has(sp.Piecewise, sp.zoo, sp.nan):
        return raw
    for m in _punti_test(a, b):
        try:
            vr = complex(sp.N(raw.subs(var, m), 20))
            vc = complex(sp.N(cand.subs(var, m), 20))
        except Exception:
            return raw
        if abs(vc.imag) > 1e-9 or abs(vc - vr) > 1e-7 * (1 + abs(vr)):
            return raw
    return cand


class Tratto:
    """Un intervallo (a,b) su cui l'espressione e' liscia."""

    def __init__(self, a, b, e, var):
        self.a, self.b, self.e, self.var = a, b, e, var
        self.de = semplifica_reale(sp.diff(e, var), var, a, b)
        self.d2e = semplifica_reale(sp.diff(self.de, var), var, a, b)
        self.crit = []
        self.approssimato = False

    def punti_interni(self, g):
        """Zeri reali di g nell'intervallo aperto (a,b)."""
        J = Interval.open(self.a, self.b)
        candidati = [g]
        num_, _ = sp.fraction(sp.together(g))
        regolare = sp.Mul(*[f for f in sp.Mul.make_args(num_)
                            if not f.is_number and not (f.is_Pow and f.exp.is_Rational and not f.exp.is_Integer)])
        if regolare != g and regolare.has(self.var):
            candidati.append(regolare)
        esatte = None
        for cand in candidati:
            try:
                sol = sp.solveset(cand, self.var, J)
            except Exception:
                continue
            if isinstance(sol, FiniteSet) or sol == S.EmptySet:
                esatte = [p for p in sol if p.is_real] if isinstance(sol, FiniteSet) else []
                break
        numeriche = self._radici_numeriche(g)
        if esatte is None:
            self.approssimato = True
            return ordina(numeriche)
        # unisce: radici esatte + eventuali cambi di segno trovati numericamente e non gia' presenti
        extra = [r for r in numeriche if not any(abs(num(r) - num(e_)) < 1e-6 for e_ in esatte)]
        if extra:
            self.approssimato = True
        return ordina(esatte + extra)

    def _radici_numeriche(self, g):
        import numpy as np
        a = float(self.a) if self.a.is_finite else -60.0
        b = float(self.b) if self.b.is_finite else 60.0
        f = sp.lambdify(self.var, g, "numpy")
        xs = np.linspace(a, b, 6001)[1:-1] + 1e-7 * (b - a)   # evita nodi esatti della griglia
        with np.errstate(all="ignore"):
            ys = np.asarray(f(xs) + 0 * xs, dtype=float)
        out = []
        for i in range(len(xs) - 1):
            if np.isfinite(ys[i]) and np.isfinite(ys[i + 1]) and ys[i] * ys[i + 1] < 0:
                lo, hi = xs[i], xs[i + 1]
                for _ in range(80):
                    mid = (lo + hi) / 2
                    fm = float(f(mid))
                    if fm == 0 or not np.isfinite(fm):
                        break
                    if float(f(lo)) * fm < 0:
                        hi = mid
                    else:
                        lo = mid
                r = (lo + hi) / 2
                cand = sp.nsimplify(r, rational=True, tolerance=1e-9)
                ok = abs(float(g.subs(self.var, cand))) < 1e-7 if cand.is_Rational and cand.q < 10 ** 4 else False
                out.append(cand if ok else sp.Float(r, 15))
        return out

    def partizione(self, punti):
        return [self.a] + list(punti) + [self.b]

    def segno(self, g, p, q):
        m = _punto_prova(p, q)
        v = sp.N(g.subs(self.var, m), 30)
        return 1 if v > 0 else (-1 if v < 0 else 0)


class Studio:
    def __init__(self, f, var=X):
        self.f0 = sp.sympify(f)
        self.var = var
        self.f = realifica(self.f0, var)
        self.rotture = punti_di_rottura(self.f, var)
        self.tratti = []
        self.note = []
        self._costruisci()

    # ------------------------------------------------------------- struttura
    def _costruisci(self):
        var = self.var
        estremi = [-oo] + self.rotture + [oo]
        for p, q in zip(estremi[:-1], estremi[1:]):
            m = _punto_prova(p, q)
            e = specializza(self.f, var, m)
            try:
                dom = continuous_domain(e, var, Interval.open(p, q))
            except Exception:
                dom = Interval.open(p, q)
                self.note.append(f"dominio su ({p},{q}) non determinato automaticamente")
            if isinstance(dom, Interval):
                dom = [dom]
            elif isinstance(dom, Union):
                dom = [d for d in dom.args if isinstance(d, Interval)]
            else:
                dom = []
            for J in dom:
                if J.start < J.end:
                    self.tratti.append(Tratto(J.start, J.end, e, var))
        self.tratti.sort(key=lambda T: (float(T.a) if T.a.is_finite else -1e300))
        self.nodi = self._nodi()
        self.dominio = self._dominio()
        self._analizza_tratti()
        self._classifica_nodi()
        self.immagine = self._immagine()

    def _nodi(self):
        pts = list(self.rotture)
        for T in self.tratti:
            for p in (T.a, T.b):
                if p.is_finite and not any(uguali(p, q) for q in pts):
                    pts.append(p)
        return ordina(pts)

    def _dominio(self):
        parti = [Interval.open(T.a, T.b) for T in self.tratti]
        for c in self.nodi:
            if valore_in(self.f, self.var, c) is not None:
                parti.append(FiniteSet(c))
        return Union(*parti) if parti else S.EmptySet

    def valore(self, c):
        return valore_in(self.f, self.var, c)

    # ------------------------------------------------------- tratti: monotonia
    def _analizza_tratti(self):
        var = self.var
        for T in self.tratti:
            T.crit = T.punti_interni(T.de)
            pts = T.partizione(T.crit)
            T.parti = []
            for p, q in zip(pts[:-1], pts[1:]):
                sg = T.segno(T.de, p, q)
                T.parti.append(dict(p=p, q=q, segno=sg))
            # valori agli estremi dei sottointervalli
            vals = []
            for i, c in enumerate(pts):
                if i == 0:
                    v = limite(T.e, var, c, "+") if c.is_finite else limite(T.e, var, c)
                    vals.append((v, False))
                elif i == len(pts) - 1:
                    v = limite(T.e, var, c, "-") if c.is_finite else limite(T.e, var, c)
                    vals.append((v, False))
                else:
                    vals.append((s(T.e.subs(var, c)), True))
            T.vals = vals
            T.flessi = []
            T.z2 = T.punti_interni(T.d2e)
            pts2 = T.partizione(T.z2)
            T.conv = []
            for p, q in zip(pts2[:-1], pts2[1:]):
                T.conv.append(dict(p=p, q=q, segno=T.segno(T.d2e, p, q)))
            for i, c in enumerate(T.z2):
                if T.conv[i]["segno"] * T.conv[i + 1]["segno"] < 0:
                    T.flessi.append(c)

    def trattosx(self, c):
        for T in self.tratti:
            if T.b == c:
                return T

    def trattodx(self, c):
        for T in self.tratti:
            if T.a == c:
                return T

    # ----------------------------------------------------------------- nodi
    def _classifica_nodi(self):
        var = self.var
        self.info = []
        for c in self.nodi:
            L, R = self.trattosx(c), self.trattodx(c)
            v = self.valore(c)
            d = dict(c=c, v=v, tipo=None, sx=None, dx=None, dsx=None, ddx=None)
            if L is not None:
                d["sx"] = limite(L.e, var, c, "-")
                d["dsx"] = limite(L.de, var, c, "-")
            if R is not None:
                d["dx"] = limite(R.e, var, c, "+")
                d["ddx"] = limite(R.de, var, c, "+")
            d["tipo"] = self._tipo(d, L, R)
            self.info.append(d)

    @staticmethod
    def _tipo(d, L, R):
        sx, dx, v = d["sx"], d["dx"], d["v"]
        lati = [t for t in (sx, dx) if t is not None]
        if any(not _fin(t) for t in lati):
            return "asintoto verticale (discontinuita' di seconda specie)" if L is not None and R is not None \
                else "asintoto verticale"
        cont_sx = sx is None or (v is not None and uguali(sx, v))
        cont_dx = dx is None or (v is not None and uguali(dx, v))
        if L is not None and R is not None:
            if not uguali(sx, dx):
                return "discontinuita' di prima specie (salto %s)" % sp.simplify(dx - sx)
            if v is None or not uguali(v, sx):
                return "discontinuita' eliminabile"
        else:
            if v is None:
                return "estremo del dominio (non incluso)"
            if not (cont_sx and cont_dx):
                return "estremo del dominio (f non continua)"
        dsx, ddx = d["dsx"], d["ddx"]
        if L is not None and R is not None:
            if _fin(dsx) and _fin(ddx):
                return "derivabile" if uguali(dsx, ddx) else "punto angoloso"
            if dsx in (oo, -oo) and ddx in (oo, -oo):
                return "flesso a tangente verticale" if dsx == ddx else "cuspide"
            return "non derivabile (tangente verticale da un lato)"
        der = dsx if L is not None else ddx
        if der in (oo, -oo):
            return "estremo del dominio con tangente verticale"
        return "estremo del dominio"

    # ---------------------------------------------------------------- immagine
    def _immagine(self):
        parti = []
        for T in self.tratti:
            for i, pz in enumerate(T.parti):
                a, b = T.vals[i][0], T.vals[i + 1][0]
                if a is sp.nan or b is sp.nan or isinstance(a, sp.AccumBounds) or isinstance(b, sp.AccumBounds):
                    self.note.append("immagine non determinabile con sicurezza (limite non calcolabile)")
                    continue
                lo, hi = (a, b) if num(a).real <= num(b).real else (b, a)
                if lo != hi:
                    parti.append(Interval.open(lo, hi))
        valori = []
        for T in self.tratti:
            for v, att in T.vals:
                if att:
                    valori.append(v)
        for d in self.info:
            if d["v"] is not None:
                valori.append(d["v"])
        return Union(*parti, FiniteSet(*valori)) if (parti or valori) else S.EmptySet

    # ------------------------------------------------------------- asintoti
    def asintoti(self):
        var = self.var
        out = dict(verticali=[], orizzontali=[], obliqui=[])
        for d in self.info:
            for lato, val in (("-", d["sx"]), ("+", d["dx"])):
                if val in (oo, -oo):
                    out["verticali"].append((d["c"], lato, val))
        for T in self.tratti:
            for punto, nome in ((T.a, "-oo"), (T.b, "+oo")):
                if punto not in (oo, -oo):
                    continue
                nome = "+oo" if punto == oo else "-oo"
                Lm = limite(T.e, var, punto)
                if _fin(Lm):
                    out["orizzontali"].append((nome, Lm))
                elif Lm in (oo, -oo):
                    m = limite(T.e / var, var, punto)
                    if _fin(m) and m != 0:
                        q = limite(T.e - m * var, var, punto)
                        if _fin(q):
                            out["obliqui"].append((nome, m, q))
        return out

    # ----------------------------------------------------------------- zeri
    def zeri(self):
        """Lista di (x, esatto?) degli zeri e numero totale (per IVT sui tratti monotoni)."""
        var = self.var
        zs = []
        for T in self.tratti:
            for i, pz in enumerate(T.parti):
                a, b = T.vals[i][0], T.vals[i + 1][0]
                if a is sp.nan or b is sp.nan or isinstance(a, sp.AccumBounds) or isinstance(b, sp.AccumBounds):
                    continue
                sa, sb = _sgn(a), _sgn(b)
                if sa * sb < 0:
                    J = Interval.open(pz["p"], pz["q"])
                    sol = None
                    try:
                        sol = sp.solveset(T.e, var, J)
                    except Exception:
                        pass
                    if isinstance(sol, FiniteSet) and len(sol) == 1:
                        zs.append((list(sol)[0], True))
                    else:
                        zs.append((self._zero_numerico(T, pz), False))
            for i, (v, att) in enumerate(T.vals):
                if att and v == 0:
                    zs.append((T.partizione(T.crit)[i], True))
        for d in self.info:
            if d["v"] is not None and d["v"] == 0 and not any(uguali(d["c"], z) for z, _ in zs):
                zs.append((d["c"], True))
        # elimina doppioni
        uniq = []
        for z, ex in zs:
            if not any(abs(num(z) - num(w)) < 1e-9 for w, _ in uniq):
                uniq.append((z, ex))
        return sorted(uniq, key=lambda t_: num(t_[0]).real)

    def _zero_numerico(self, T, pz):
        a = float(pz["p"]) if pz["p"].is_finite else None
        b = float(pz["q"]) if pz["q"].is_finite else None
        f = sp.lambdify(self.var, T.e, "mpmath")
        import mpmath as mp
        if a is None and b is None:
            a, b = -1.0, 1.0
        if a is None:
            a = b - 1.0
            while sp.N(T.e.subs(self.var, a)) * sp.N(T.e.subs(self.var, b - 1e-12)) > 0 and a > -1e6:
                a = b - 2 * (b - a)
        if b is None:
            b = a + 1.0
            while sp.N(T.e.subs(self.var, a + 1e-12)) * sp.N(T.e.subs(self.var, b)) > 0 and b < 1e6:
                b = a + 2 * (b - a)
        eps = 1e-12 * (1 + abs(b - a))
        try:
            return sp.Float(mp.findroot(f, (a + eps, b - eps), solver="anderson", tol=1e-18, maxsteps=200))
        except Exception:
            return sp.Float(mp.findroot(f, (a + b) / 2))

    # ---------------------------------------------------------- estremi locali
    def estremi(self):
        """Lista di (x, tipo, valore, globale?)."""
        out = []
        sup, inf = self.immagine.sup, self.immagine.inf
        for T in self.tratti:
            for i, c in enumerate(T.crit):
                s1, s2 = T.parti[i]["segno"], T.parti[i + 1]["segno"]
                v = T.vals[i + 1][0]
                if s1 > 0 and s2 < 0:
                    out.append((c, "massimo", v, uguali(v, sup)))
                elif s1 < 0 and s2 > 0:
                    out.append((c, "minimo", v, uguali(v, inf)))
                else:
                    out.append((c, "flesso a tangente orizzontale", v, False))
        for d in self.info:
            c, v = d["c"], d["v"]
            if v is None:
                continue
            L, R = self.trattosx(c), self.trattodx(c)
            sl = L.parti[-1]["segno"] if L else None
            sr = R.parti[0]["segno"] if R else None
            cont = (d["sx"] is None or uguali(d["sx"], v)) and (d["dx"] is None or uguali(d["dx"], v))
            if not cont:
                continue
            tipo = None
            if sl is not None and sr is not None:
                if sl > 0 and sr < 0:
                    tipo = "massimo"
                elif sl < 0 and sr > 0:
                    tipo = "minimo"
            elif sl is not None:
                tipo = "massimo" if sl > 0 else "minimo"
            elif sr is not None:
                tipo = "minimo" if sr > 0 else "massimo"
            if tipo:
                glob = uguali(v, sup) if tipo == "massimo" else uguali(v, inf)
                out.append((c, tipo + (" (di frontiera)" if sl is None or sr is None else ""), v, glob))
        return sorted(out, key=lambda t_: num(t_[0]).real)

    def flessi(self):
        out = []
        for T in self.tratti:
            for c in T.flessi:
                out.append((c, s(T.e.subs(self.var, c))))
        for d in self.info:
            if d["tipo"] == "flesso a tangente verticale":
                out.append((d["c"], d["v"]))
        return sorted(out, key=lambda t_: num(t_[0]).real)


def _sgn(v):
    if v == oo:
        return 1
    if v == -oo:
        return -1
    n_ = sp.N(v, 30)
    return 1 if n_ > 0 else (-1 if n_ < 0 else 0)


# ============================================================ rapporto ========
def mostra(v, cifre=6):
    """Espressione leggibile: se troppo lunga mostra solo l'approssimazione numerica."""
    if v is None:
        return "n.d."
    try:
        if sp.count_ops(v) > 28:
            return f"~ {sp.N(v, cifre)}"
    except Exception:
        pass
    return str(v)


def _segni(St, zs):
    """Intervalli in cui f>0 / f<0."""
    pos, neg = [], []
    zv = [z for z, _ in zs]
    for T in St.tratti:
        interni = [z for z in zv if num(T.a).real < num(z).real < num(T.b).real] if True else []
        pts = [T.a] + interni + [T.b]
        for p, q in zip(pts[:-1], pts[1:]):
            m = _punto_prova(p, q)
            v = sp.N(T.e.subs(St.var, m), 30)
            etichetta = f"({mostra(p)}, {mostra(q)})"
            (pos if v > 0 else neg).append(etichetta)
    return pos, neg


def studio_funzione(f, var=X, nome="f", png=None, finestra=(-6, 6), stampa=True, completo=True):
    """Studio completo con stampa in italiano. Restituisce l'oggetto Studio."""
    St = Studio(f, var)
    if not stampa:
        return St
    riga(f"{nome}(x) = {St.f0}")
    sezione("DOMINIO, SEGNO, LIMITI, ASINTOTI")
    riga("dominio:", St.dominio)
    if St.rotture:
        riga("punti di raccordo (cambio forma |.|, radici, tratti):", St.rotture)
    # simmetria
    try:
        if sp.simplify(St.f.subs(var, -var) - St.f) == 0:
            riga("simmetria: f e' PARI")
        elif sp.simplify(St.f.subs(var, -var) + St.f) == 0:
            riga("simmetria: f e' DISPARI")
        else:
            riga("simmetria: ne' pari ne' dispari")
    except Exception:
        pass
    zs = St.zeri()
    riga("zeri:", [(mostra(z) if ex else f"~ {sp.N(z, 8)}") for z, ex in zs] if zs else "nessuno")
    pos, neg = _segni(St, zs)
    riga("segno: f > 0 in", " U ".join(pos) if pos else "nessun intervallo", "; f < 0 in", " U ".join(neg) if neg else "nessun intervallo")
    for d in St.info:
        a, b = d["sx"], d["dx"]
        desc = []
        if a is not None:
            desc.append(f"lim x->{d['c']}- f = {a}")
        if b is not None:
            desc.append(f"lim x->{d['c']}+ f = {b}")
        if d["v"] is not None:
            desc.append(f"f({d['c']}) = {d['v']}")
        riga(f"in x = {d['c']}: " + "; ".join(desc) + f"  ->  {d['tipo']}")
    for T in St.tratti:
        for punto in (T.a, T.b):
            if punto in (oo, -oo):
                riga(f"lim x->{'+oo' if punto == oo else '-oo'} f = {limite(T.e, var, punto)}   (sul tratto ({T.a}, {T.b}))")
    As = St.asintoti()
    for p, lato, v in As["verticali"]:
        riga(f"asintoto VERTICALE x = {p} (da {'destra' if lato == '+' else 'sinistra'}, f -> {v})")
    for nome_, L in As["orizzontali"]:
        riga(f"asintoto ORIZZONTALE y = {L} (x -> {nome_})")
    for nome_, m, q in As["obliqui"]:
        riga(f"asintoto OBLIQUO y = {sp.simplify(m * var + q)} (x -> {nome_})")
    if not any(As.values()):
        riga("nessun asintoto")
    sezione("DERIVATA PRIMA, MONOTONIA, ESTREMI")
    prec = None
    for T in St.tratti:
        if prec is None or sp.simplify(T.de - prec) != 0:
            riga(f"su ({T.a}, {T.b}): f'(x) = {sp.factor(T.de)}")
        else:
            riga(f"su ({T.a}, {T.b}): f'(x) come sopra")
        prec = T.de
    riga("dominio di f':", _dominio_derivata(St))
    for d in St.info:
        if d["tipo"] not in ("derivabile",) and not d["tipo"].startswith("asintoto") and d["v"] is not None:
            riga(f"x = {d['c']}: {d['tipo']}"
                 + (f"  (f'- = {d['dsx']}, f'+ = {d['ddx']})" if d["dsx"] is not None and d["ddx"] is not None else ""))
    for T in St.tratti:
        for i, pz in enumerate(T.parti):
            dirz = "crescente" if pz["segno"] > 0 else ("decrescente" if pz["segno"] < 0 else "costante")
            riga(f"su ({pz['p']}, {pz['q']}): {dirz}   (da {T.vals[i][0]} a {T.vals[i + 1][0]})")
    for c, tipo, v, glob in St.estremi():
        riga(f"x = {mostra(c)}: {tipo}{' GLOBALE' if glob and 'frontiera' not in tipo else (' (globale)' if glob else ' relativo')}"
             f", f = {mostra(v)}" + (f" ~ {sp.N(v, 6)}" if sp.count_ops(v) <= 28 else ""))
    if not St.estremi():
        riga("nessun punto di estremo")
    if completo:
        sezione("DERIVATA SECONDA, CONVESSITA', FLESSI")
        prec = None
        for T in St.tratti:
            if prec is None or sp.simplify(T.d2e - prec) != 0:
                riga(f"su ({T.a}, {T.b}): f''(x) = {sp.factor(T.d2e)}")
            else:
                riga(f"su ({T.a}, {T.b}): f''(x) come sopra")
            prec = T.d2e
            for pz in T.conv:
                riga(f"   su ({mostra(pz['p'])}, {mostra(pz['q'])}): "
                     f"{'convessa' if pz['segno'] > 0 else ('concava' if pz['segno'] < 0 else 'lineare')}")
        fl = St.flessi()
        riga("flessi:", [(mostra(c), f"f = {mostra(v)}") for c, v in fl] if fl else "nessuno")
    sezione("ZERI (conteggio con il teorema degli zeri), IMMAGINE")
    riga(f"numero esatto di zeri: {len(zs)}")
    riga("IMMAGINE:", St.immagine)
    for nota in St.note:
        riga("(nota)", nota)
    if png:
        grafico(St, png, finestra)
    return St


def _dominio_derivata(St):
    parti = [Interval.open(T.a, T.b) for T in St.tratti]
    for d in St.info:
        if d["tipo"] == "derivabile":
            parti.append(FiniteSet(d["c"]))
    return Union(*parti) if parti else S.EmptySet


def grafico(St, png, finestra=(-6, 6)):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    os.makedirs(OUT_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ys_all = []
    for T in St.tratti:
        lo = max(float(T.a) if T.a.is_finite else finestra[0], finestra[0])
        hi = min(float(T.b) if T.b.is_finite else finestra[1], finestra[1])
        if lo >= hi:
            continue
        fn = sp.lambdify(St.var, T.e, "numpy")
        xs = np.linspace(lo, hi, 4000)
        if T.a.is_finite:
            xs = xs[1:]
        if T.b.is_finite:
            xs = xs[:-1]
        with np.errstate(all="ignore"):
            ys = np.asarray(fn(xs) + 0 * xs, dtype=complex)
        ys = np.where(np.abs(ys.imag) < 1e-9, ys.real, np.nan)
        ys = np.where(np.abs(ys) > 60, np.nan, ys)
        ax.plot(xs, ys, color="#1f4e9c", lw=1.8)
        ys_all.append(ys[np.isfinite(ys)])
    for d in St.info:
        if d["v"] is not None:
            ax.plot([float(d["c"])], [float(sp.N(d["v"]))], "o", color="#1f4e9c", ms=4)
    As = St.asintoti()
    for p, _, _ in As["verticali"]:
        ax.axvline(float(p), color="gray", ls="--", lw=0.8)
    mezzo = (finestra[0] + finestra[1]) / 2
    for nome_, m, q in As["obliqui"]:
        xx = np.linspace(mezzo, finestra[1], 10) if nome_ == "+oo" else np.linspace(finestra[0], mezzo, 10)
        ax.plot(xx, float(m) * xx + float(q), color="gray", ls="--", lw=0.8)
    for nome_, L in As["orizzontali"]:
        lo_, hi_ = (mezzo, finestra[1]) if nome_ == "+oo" else (finestra[0], mezzo)
        ax.plot([lo_, hi_], [float(L), float(L)], color="gray", ls="--", lw=0.8)
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlim(*finestra)
    ys_all = np.concatenate(ys_all) if ys_all else np.array([])
    if len(ys_all):
        lo, hi = np.percentile(ys_all, 1), np.percentile(ys_all, 99)
        lo, hi = min(lo, ys_all.min() if len(ys_all) < 50 else lo), max(hi, ys_all.max() if len(ys_all) < 50 else hi)
        pad = 0.2 * (hi - lo + 1e-9)
        ax.set_ylim(lo - pad, hi + pad)
    ax.set_title(f"f(x) = {St.f0}", fontsize=10)
    ax.grid(alpha=0.3)
    path = os.path.join(OUT_DIR, png)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    riga(f"grafico salvato in: {path}")
    return path


# ================================================== utilita' di compatibilita' ==
def asintoti(f, var=X, stampa=True):
    St = Studio(f, var)
    As = St.asintoti()
    if stampa:
        for p, lato, v in As["verticali"]:
            riga(f"asintoto verticale x = {p} (per x -> {p}{lato}, f -> {v})")
        for nome_, L in As["orizzontali"]:
            riga(f"asintoto orizzontale y = {L} (x -> {nome_})")
        for nome_, m, q in As["obliqui"]:
            riga(f"asintoto obliquo y = {sp.simplify(m * var + q)} (x -> {nome_})")
        if not any(As.values()):
            riga("nessun asintoto")
    return As


def classifica_discontinuita(f, p, var=X):
    St = Studio(f, var)
    for d in St.info:
        if uguali(d["c"], p):
            return d["sx"], d["dx"], d["tipo"]
    return None


def immagine(f, var=X):
    return Studio(f, var).immagine


def classifica_critico(f, var=X, x0=0):
    """Primo termine non nullo di Taylor c*(x-x0)^k: pari -> max/min locale, dispari -> nessun estremo."""
    s_ = sp.series(f, var, x0, 12).removeO()
    termini = sp.Poly(sp.expand(s_.subs(var, var + x0) if x0 else s_), var)
    for (ordine,), c in sorted(termini.terms(), key=lambda tc: tc[0][0]):
        if c != 0:
            if ordine % 2 == 0:
                return ordine, c, ("minimo locale" if c > 0 else "massimo locale")
            return ordine, c, "nessun estremo (flesso a tangente orizzontale)"
    return None, 0, "f identicamente nulla"


def estremi_assoluti(f, a, b, var=X, stampa=True):
    """Massimo e minimo assoluti di f su [a,b] (candidati: estremi, punti critici, punti di non derivabilita')."""
    f = sp.sympify(f)
    a, b = sp.sympify(a), sp.sympify(b)
    St = Studio(f, var)
    cand = [a, b]
    for T in St.tratti:
        cand += [c for c in T.crit if a < c < b]
    cand += [c for c in St.nodi if a < c < b]
    vals = []
    for c in cand:
        v = valore_in(St.f, var, c)
        if v is not None and not any(abs(num(c) - num(w)) < 1e-12 for w, _ in vals):
            vals.append((c, s(v)))
    vals.sort(key=lambda t_: num(t_[0]).real)
    if stampa:
        for c, v in vals:
            riga(f"f({mostra(c)}) = {mostra(v)}   ~ {sp.N(v, 8)}")
    if not vals:
        riga("f non definita nei candidati")
        return None
    mx = max(vals, key=lambda t_: num(t_[1]).real)
    mn = min(vals, key=lambda t_: num(t_[1]).real)
    if stampa:
        riga(f"MASSIMO assoluto su [{a},{b}]: {mostra(mx[1])} in x = {mostra(mx[0])}")
        riga(f"MINIMO assoluto su [{a},{b}]:  {mostra(mn[1])} in x = {mostra(mn[0])}")
    return dict(max=mx, min=mn)
