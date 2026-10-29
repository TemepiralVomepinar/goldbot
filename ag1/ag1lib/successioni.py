"""Insiemi (sup/inf), successioni, limiti (anche con parametro), ordine di infinitesimo, raccordi con parametri."""
import re

import sympy as sp
from sympy import Interval, Rational, S, oo

from .util import (ESITI, k, lim, n, num, ordina, parse, riga, sezione, t, uguali, x)


# ============================================================ sup / inf =======
def _estremi_monotona(e, var, k0):
    """sup/inf di una successione monotona e(var), var >= k0 (intero)."""
    d = sp.simplify(e.subs(var, t + 1) - e.subs(var, t))
    dom = Interval(k0, oo)
    L = sp.simplify(sp.limit(e, var, oo))
    primo = sp.simplify(e.subs(var, k0))
    if sp.solveset(d < 0, t, dom) == dom:  # strettamente decrescente
        return dict(sup=primo, sup_att=True, inf=L, inf_att=False, mono="decrescente")
    if sp.solveset(d > 0, t, dom) == dom:  # strettamente crescente
        return dict(sup=L, sup_att=False, inf=primo, inf_att=True, mono="crescente")
    raise ValueError("successione non monotona")


def _estremi_numerici(e, var, k0, N=4000):
    """Fallback: sup/inf stimati sui primi N termini + limite."""
    f = sp.lambdify(var, e, "mpmath")
    import mpmath as mp
    vals = [mp.mpf(f(mp.mpf(i))) for i in range(k0, k0 + N)]
    L = sp.limit(e, var, oo)
    imax = max(range(N), key=lambda i: vals[i])
    imin = min(range(N), key=lambda i: vals[i])
    mx, mn = vals[imax], vals[imin]
    Lf = float(L) if L.is_finite else None
    sup_att = imax < N - 1 and (Lf is None or float(mx) > Lf + 1e-12)
    inf_att = imin < N - 1 and (Lf is None or float(mn) < Lf - 1e-12)
    sup = sp.nsimplify(float(mx), rational=False) if sup_att else (L if L.is_finite and Lf >= float(mx) - 1e-9 else sp.Float(mx, 10))
    inf = sp.nsimplify(float(mn), rational=False) if inf_att else (L if L.is_finite and Lf <= float(mn) + 1e-9 else sp.Float(mn, 10))
    if L == oo:
        sup, sup_att = oo, False
    if L == -oo:
        inf, inf_att = -oo, False
    return dict(sup=sup, sup_att=sup_att, inf=inf, inf_att=inf_att, mono="(stima numerica)")


def estremi_successione(parti, stampa=True):
    """parti: lista di (espressione, variabile, indice iniziale) = sottosuccessioni che coprono l'insieme."""
    ris = []
    for e, var, k0 in parti:
        try:
            r = _estremi_monotona(e, var, k0)
        except Exception:
            r = _estremi_numerici(e, var, k0)
        if stampa:
            riga(f"sottosuccessione {e} (da {var}={k0}): {r['mono']}; "
                 f"sup={r['sup']}{' (assunto)' if r['sup_att'] else ''}, inf={r['inf']}{' (assunto)' if r['inf_att'] else ''}")
        ris.append(r)
    f_ = lambda v: float(sp.N(v)) if v not in (oo, -oo) else (1e300 if v == oo else -1e300)
    sup = max((r["sup"] for r in ris), key=f_)
    inf = min((r["inf"] for r in ris), key=f_)
    sup_att = any(r["sup_att"] and uguali(r["sup"], sup) for r in ris)
    inf_att = any(r["inf_att"] and uguali(r["inf"], inf) for r in ris)
    return sup, sup_att, inf, inf_att


def riassumi_estremi(sup, sup_att, inf, inf_att):
    riga(f"sup = {sup}  -> {'MASSIMO (appartiene all insieme)' if sup_att else 'nessun massimo'}")
    riga(f"inf = {inf}  -> {'MINIMO (appartiene all insieme)' if inf_att else 'nessun minimo'}")


def _parti_da_espressione(e, var, n0):
    """Spezza in pari/dispari se compaiono (-1)^n o cos(pi n)."""
    pari = e.has(sp.cos) and e.has(sp.pi) or any(
        p_.is_Pow and p_.base == -1 for p_ in e.atoms(sp.Pow))
    if not pari:
        return [(e, var, n0)]
    kk = sp.Symbol("k", integer=True, nonnegative=True)
    k_p = -(-n0 // 2)           # ceil(n0/2): n=2k >= n0
    k_d = -(-(n0 - 1) // 2)     # n=2k+1 >= n0
    ep = sp.simplify(e.subs(var, 2 * kk))
    ed = sp.simplify(e.subs(var, 2 * kk + 1))
    return [(ep, kk, k_p), (ed, kk, k_d)]


def successione(espr, n0=1, stampa=True):
    """Analisi di a_n = espr(n): primi termini, limite, sottosuccessioni, sup/inf/max/min."""
    e = parse(espr)
    var = n
    e = e.subs({s_: n for s_ in e.free_symbols if s_.name == "n"})
    if stampa:
        termini = [sp.N(e.subs(var, i), 6) for i in range(n0, n0 + 8)]
        riga(f"a_n = {e}   (n >= {n0})")
        riga("primi termini:", termini)
    parti = _parti_da_espressione(e, var, n0)
    out = {}
    try:
        L = sp.limit(e, var, oo)
        out["limite"] = L
        if isinstance(L, sp.AccumBounds):
            raise ValueError
        if stampa:
            riga(f"limite per n->oo: {L}")
    except Exception:
        if len(parti) == 2:
            lp = [sp.limit(p_[0], p_[1], oo) for p_ in parti]
            out["sottolimiti"] = lp
            if lp[0] == lp[1]:
                out["limite"] = lp[0]
            if stampa:
                riga(f"sottosuccessioni pari/dispari -> {lp[0]} e {lp[1]}: " +
                     ("il limite NON esiste" if lp[0] != lp[1] else f"il limite esiste: {lp[0]}"))
        elif stampa:
            riga("limite non determinabile in forma chiusa (successione oscillante o non regolare)")
    if len(parti) == 2 and "limite" not in out:
        pass
    sup, sa, inf, ia = estremi_successione(parti, stampa=stampa)
    out.update(sup=sup, sup_att=sa, inf=inf, inf_att=ia)
    if stampa:
        riassumi_estremi(sup, sa, inf, ia)
        limitata = sup not in (oo,) and inf not in (-oo,)
        riga("limitata" if limitata else "NON limitata" + (" superiormente" if sup == oo else "") + (" inferiormente" if inf == -oo else ""))
    return out


def ricorrenza(f_espr, a1, passi=60, stampa=True):
    """a_{n+1} = f(a_n), a_1 = a1: punti fissi, monotonia, limite."""
    a = sp.Symbol("a", real=True)
    f = parse(f_espr, a=a)
    a1 = sp.sympify(parse(str(a1)))
    L = sp.Symbol("L", real=True)
    fissi = sp.solve(sp.Eq(f.subs(a, L), L), L) if True else []
    fissi = [p_ for p_ in fissi if p_.is_real]
    v = a1
    seq = [v]
    for _ in range(passi):
        v = sp.N(f.subs(a, v), 30)
        seq.append(v)
    cresc = all(seq[i + 1] >= seq[i] - 1e-12 for i in range(len(seq) - 1))
    decr = all(seq[i + 1] <= seq[i] + 1e-12 for i in range(len(seq) - 1))
    if stampa:
        riga(f"a_(n+1) = {f.subs(a, sp.Symbol('a_n'))},  a_1 = {a1}")
        riga("punti fissi (L = f(L)):", fissi)
        riga("primi termini:", [sp.N(s_, 8) for s_ in seq[:6]])
        riga("andamento numerico:", "crescente" if cresc else ("decrescente" if decr else "non monotona"),
             f"; a_{passi + 1} ~ {sp.N(seq[-1], 12)}")
    return dict(fissi=fissi, ultimo=seq[-1], crescente=cresc, decrescente=decr)


# ============================================================ insiemi di R ====
_OPS = ["<=", ">=", "!=", "<", ">", "="]


def _relazione(testo, var):
    for op in _OPS:
        if op in testo:
            l, r = testo.split(op, 1)
            L, R = parse(l), parse(r)
            return {"<": L < R, ">": L > R, "<=": L <= R, ">=": L >= R, "=": sp.Eq(L, R), "!=": sp.Ne(L, R)}[op]
    raise ValueError(f"relazione non riconosciuta: {testo}")


def insieme_reale(cond, var=x):
    """'x^2-2x-3<0 and abs(x)>=1' (and/or) -> insieme sympy."""
    ors = re.split(r"\s+or\s+", cond)
    risultato = []
    for o in ors:
        ands = re.split(r"\s+and\s+", o)
        parziale = S.Reals
        for a in ands:
            rel = _relazione(a.strip(), var)
            parziale = parziale.intersect(sp.solveset(rel, var, S.Reals))
        risultato.append(parziale)
    return sp.Union(*risultato)


def estremi_insieme(A, stampa=True):
    """sup, inf, max, min di un sottoinsieme di R (Interval/Union/FiniteSet/ImageSet su Z)."""
    componenti = list(A.args) if isinstance(A, sp.Union) else [A]
    cand_sup, cand_inf = [], []   # (valore, assunto?)
    for c in componenti:
        if isinstance(c, sp.ImageSet):
            lam = c.lamda
            kk = lam.variables[0]
            g = lam.expr
            m = sp.Symbol("m", integer=True, nonnegative=True)
            parti = [(sp.simplify(g.subs(kk, m)), m, 0), (sp.simplify(g.subs(kk, -m - 1)), m, 0)]
            if stampa:
                riga(f"famiglia infinita x = {g}, k in Z: si spezza in k>=0 e k<=-1")
            sup, sa, inf, ia = estremi_successione(parti, stampa=False)
            cand_sup.append((sup, sa))
            cand_inf.append((inf, ia))
        elif isinstance(c, sp.FiniteSet):
            if len(c):
                cand_sup.append((max(c, key=lambda v: float(v)), True))
                cand_inf.append((min(c, key=lambda v: float(v)), True))
        elif isinstance(c, Interval):
            cand_sup.append((c.sup, c.sup in c))
            cand_inf.append((c.inf, c.inf in c))
        elif c == S.EmptySet:
            continue
        else:
            raise ValueError(f"insieme non gestito: {c}")
    if not cand_sup:
        return dict(sup=None)
    f_ = lambda v: float(sp.N(v)) if v not in (oo, -oo) else (1e300 if v == oo else -1e300)
    sup = max((v for v, _ in cand_sup), key=f_)
    inf = min((v for v, _ in cand_inf), key=f_)
    sup_att = any(a_ and uguali(v, sup) for v, a_ in cand_sup)
    inf_att = any(a_ and uguali(v, inf) for v, a_ in cand_inf)
    if stampa:
        riga("insieme:", A)
        riassumi_estremi(sup, sup_att, inf, inf_att)
    return dict(sup=sup, sup_att=sup_att, inf=inf, inf_att=inf_att)


def famiglia_intervalli(a_n, b_n, n0=1, sx_aperto=True, dx_aperto=True, N=60):
    """Unione e intersezione di I_n = (a_n, b_n) (estremi aperti/chiusi) per n >= n0."""
    an, bn = parse(a_n), parse(b_n)
    an = an.subs({s_: n for s_ in an.free_symbols if s_.name == "n"}) if an.free_symbols else an
    bn = bn.subs({s_: n for s_ in bn.free_symbols if s_.name == "n"}) if bn.free_symbols else bn
    mk = lambda i: Interval(an.subs(n, i), bn.subs(n, i), sx_aperto, dx_aperto)
    primi = [mk(i) for i in range(n0, n0 + N)]
    inters = sp.Intersection(*primi[:N])
    # unione: estremi esatti con sup/inf della successione degli estremi
    s_a = estremi_successione([(an, n, n0)], stampa=False)
    s_b = estremi_successione([(bn, n, n0)], stampa=False)
    unione_N = sp.Union(*primi)
    # unione completa: se gli estremi esterni sono determinati dalla coda, sostituiscili con il limite
    comp = sorted(unione_N.args if isinstance(unione_N, sp.Union) else [unione_N], key=lambda c: float(c.inf))
    if comp and isinstance(comp[0], Interval) and uguali(comp[0].start, an.subs(n, n0 + N - 1)):
        comp[0] = Interval(s_a[2], comp[0].end, not s_a[3] or sx_aperto, comp[0].right_open)
    if comp and isinstance(comp[-1], Interval) and uguali(comp[-1].end, bn.subs(n, n0 + N - 1)):
        comp[-1] = Interval(comp[-1].start, s_b[0], comp[-1].left_open, not s_b[1] or dx_aperto)
    unione = sp.Union(*comp)
    return dict(unione=unione, unione_primi=unione_N, intersezione=inters,
                inf_sx=(s_a[2], s_a[3]), sup_sx=(s_a[0], s_a[1]), inf_dx=(s_b[2], s_b[3]), sup_dx=(s_b[0], s_b[1]))


# ================================================================ limiti ======
def limite(espr, var="x", punto="0", direzione=None, stampa=True):
    e = parse(espr)
    v = n if var == "n" else sp.Symbol(var, real=True)
    e = e.subs({s_: v for s_ in e.free_symbols if s_.name == var})
    pt = parse(punto) if isinstance(punto, str) else punto
    L = lim(e, v, pt, direzione)
    if stampa:
        riga(f"lim_({var}->{pt}{direzione or ''}) {e} = {L}")
        if pt in (oo, -oo):
            tests = [10 ** 3, 10 ** 5, 10 ** 7]
            tests = tests if pt == oo else [-s_ for s_ in tests]
        else:
            d = Rational(1, 10 ** 4)
            tests = [pt + d * s_ for s_ in ((1, -1) if direzione in (None, "+-") else ((1,) if direzione == "+" else (-1,)))]
        try:
            riga("controllo numerico:", [(float(a), float(sp.N(e.subs(v, a), 15))) for a in tests])
        except Exception:
            pass
    return L


def ordine_infinitesimo(espr, var=x, x0=0, kmax=12):
    """Primo termine non nullo c*(x-x0)^p dello sviluppo di Taylor (p intero)."""
    e = parse(espr) if isinstance(espr, str) else espr
    h = sp.Symbol("h", real=True)
    s_ = sp.series(e.subs(var, x0 + h), h, 0, kmax).removeO()
    P = sp.Poly(sp.expand(s_), h)
    for (p_,), c in sorted(P.terms(), key=lambda q: q[0][0]):
        if c != 0:
            return p_, sp.simplify(c)
    return None, 0


def limite_parametro(espr, param="a", var="x", punto="0", valore=None, stampa=True):
    """Studia lim espr al variare del parametro (reale): condizioni di finitezza / valore richiesto.
    Usa lo sviluppo in serie in h (x = punto + h, oppure x = 1/h per punto=oo)."""
    a = sp.Symbol(param, real=True)
    v = n if var == "n" else sp.Symbol(var, real=True)
    e = parse(espr, **{param: a})
    e = e.subs({s_: v for s_ in e.free_symbols if s_.name == var})
    pt = parse(punto) if isinstance(punto, str) else punto
    h = sp.Symbol("h", positive=True)
    e_h = e.subs(v, 1 / h) if pt == oo else (e.subs(v, -1 / h) if pt == -oo else e.subs(v, pt + h))
    ser = sp.series(e_h, h, 0, 5).removeO()
    ser = sp.expand(ser)
    coeff = {}
    for term in sp.Add.make_args(ser):
        c, p_ = term.as_coeff_exponent(h)
        coeff[p_] = sp.simplify(coeff.get(p_, 0) + c)
    negative = {p_: c for p_, c in coeff.items() if p_ < 0}
    c0 = coeff.get(0, S.Zero)
    if stampa:
        riga(f"sviluppo in h (h -> 0+): {sp.simplify(ser)} + ...")
    cond = [c for c in negative.values() if c != 0]
    sol_fin = sp.solve(cond, a, dict=True) if cond else [{}]
    out = dict(coefficienti=coeff, finito_per=sol_fin)
    if stampa:
        if cond:
            riga("il limite e' finito solo se si annullano i coefficienti dei termini divergenti:", cond,
                 " =>", sol_fin if sol_fin else "per nessun valore del parametro")
        else:
            riga("nessun termine divergente: il limite e' finito per ogni valore del parametro")
    L = [sp.simplify(c0.subs(s_)) for s_ in sol_fin] if sol_fin else []
    out["limite"] = L
    if stampa and L:
        riga(f"valore del limite (come funzione del parametro, sotto le condizioni): {L}")
    if valore is not None:
        target = sp.sympify(parse(str(valore)))
        risolti = []
        for s_ in sol_fin:
            c0s = c0.subs(s_)
            if c0s.has(a):
                for r in sp.solve(sp.Eq(c0s, target), a):
                    risolti.append(r)
            elif sp.simplify(c0s - target) == 0 and not s_:
                risolti.append("tutti i valori")
        out["soluzioni"] = risolti
        if stampa:
            riga(f"limite = {target}  per  {param} in {risolti}" if risolti else f"limite = {target}: nessun valore di {param}")
    return out


# ============================================================ raccordi =========
def raccordo(f_sx, f_dx, x0=0, parametri=(), stampa=True):
    """f = f_sx per x<x0, f_dx per x>=x0, con parametri: condizioni di continuita', derivabilita' e C^2."""
    ps = {p_: sp.Symbol(p_, real=True) for p_ in parametri}
    fs, fd = parse(f_sx, **ps), parse(f_dx, **ps)
    x0 = sp.sympify(parse(str(x0)))
    pars = list(ps.values())
    cont = sp.simplify(sp.limit(fs, x, x0, "-") - fd.subs(x, x0))
    d1 = sp.simplify(sp.limit(sp.diff(fs, x), x, x0, "-") - sp.diff(fd, x).subs(x, x0))
    d2 = sp.simplify(sp.limit(sp.diff(fs, x, 2), x, x0, "-") - sp.diff(fd, x, 2).subs(x, x0))
    out = {}
    for nome, eq in (("continua", [cont]), ("derivabile", [cont, d1]), ("di classe C^2", [cont, d1, d2])):
        eq = [sp.simplify(e_) for e_ in eq]
        non_nulle = [e_ for e_ in eq if e_ != 0]
        try:
            if not non_nulle:
                sol = "sempre (per ogni valore dei parametri)"
            else:
                sol = sp.solve(non_nulle, pars, dict=True) if pars else []
        except Exception:
            sol = "non risolto"
        out[nome] = sol
        if stampa:
            riga(f"f {nome} in x={x0}  <=>  {eq} = 0  ->  {sol if sol else 'per nessun valore'}")
    return out


def limite_esponente(num_espr, base_espr, punto="0", stampa=True):
    """lim_{x->x0} N(x) / D(x)^a al variare dell'esponente a (D infinitesima).
    Usa gli ordini di infinitesimo: N ~ cN (x-x0)^pN, D ~ cD (x-x0)^pD  =>  N/D^a ~ (x-x0)^(pN - a pD)."""
    x0 = sp.sympify(parse(str(punto)))
    N, D = parse(num_espr), parse(base_espr)
    pN, cN = ordine_infinitesimo(N, x, x0)
    pD, cD = ordine_infinitesimo(D, x, x0)
    out = dict(pN=pN, cN=cN, pD=pD, cD=cD)
    if pD is None or pN is None or pD <= 0:
        if stampa:
            riga("il caso D non infinitesima non e' gestito automaticamente")
        return out
    soglia = Rational(pN, pD)
    out["soglia"] = soglia
    if stampa:
        riga(f"numeratore ~ {cN}*(x-{x0})^{pN};  base ~ {cD}*(x-{x0})^{pD}")
        riga(f"N/D^a ~ (x-{x0})^({pN} - {pD}*a):  esponente nullo per a = {soglia}")
        riga(f"  a < {soglia}: il limite vale 0 (esiste finito)")
        riga(f"  a = {soglia}: il limite e' finito e NON nullo: vale {sp.simplify(cN / cD ** soglia)}")
        riga(f"  a > {soglia}: il limite e' infinito (non esiste finito)")
    return out
