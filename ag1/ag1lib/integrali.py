"""Integrali (propri, impropri, con parametro), area, funzione integrale, equazioni differenziali, curve."""
import re
import signal

import sympy as sp
from sympy import Interval, Rational, S, oo

from .funzioni import realifica
from .geometria import str_piano
from .util import parse, riga, sezione, t, uguali, x


# ----------------------------------------------------------------- timeout ---
class _Timeout(Exception):
    pass


def con_timeout(fun, secondi=25):
    def gestore(signum, frame):
        raise _Timeout()
    try:
        vecchio = signal.signal(signal.SIGALRM, gestore)
        signal.alarm(secondi)
    except ValueError:   # non nel main thread
        return fun()
    try:
        return fun()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, vecchio)


def _integra(f, var, a=None, b=None):
    try:
        r = con_timeout(lambda: sp.integrate(f, var) if a is None else sp.integrate(f, (var, a, b)))
        if isinstance(r, sp.Integral) or r.has(sp.Integral):
            return None
        return r
    except Exception:
        return None


def _numerico(f, var, a, b):
    import mpmath as mp
    fn = sp.lambdify(var, f, "mpmath")
    lo = -mp.inf if a == -oo else mp.mpf(sp.N(a))
    hi = mp.inf if b == oo else mp.mpf(sp.N(b))
    try:
        return mp.quad(fn, [lo, hi])
    except Exception:
        return None


# ============================================ convergenza di integrali impropri
def _p_numerico(g, u, punto):
    """Stima numerica dell'esponente p con g ~ c u^p (u -> punto) e del tasso esponenziale."""
    import mpmath as mp
    mp.mp.dps = 80
    fn = sp.lambdify(u, g, "mpmath")
    if punto == oo:
        u1, u2 = mp.mpf(10) ** 20, mp.mpf(10) ** 25
        a1, a2 = abs(fn(u1)), abs(fn(u2))
        if a1 == 0 or a2 == 0:
            return None, None
        p = mp.log(a2 / a1) / mp.log(u2 / u1)
        v1, v2 = mp.mpf(200), mp.mpf(400)
        r = (mp.log(abs(fn(v2))) - mp.log(abs(fn(v1)))) / (v2 - v1) if abs(fn(v1)) > 0 and abs(fn(v2)) > 0 else None
        return float(p), (float(r) if r is not None else None)
    h1, h2 = mp.mpf(10) ** -30, mp.mpf(10) ** -40
    a1, a2 = abs(fn(h1)), abs(fn(h2))
    if a1 == 0 or a2 == 0:
        return None, None
    return float(mp.log(a2 / a1) / mp.log(h2 / h1)), None


def comportamento_estremo(f, var, c, lato="+"):
    """Convergenza di f vicino a c (finito, da lato '+'/'-') o a +-oo.
    Restituisce (converge: True/False/None, descrizione)."""
    u = sp.Symbol("u", positive=True)
    if c in (oo, -oo):
        g = f.subs(var, u if c == oo else -u)
        try:
            r = sp.limit(sp.log(sp.Abs(g)) / u, u, oo)
        except Exception:
            r = None
        if r is not None and r.is_number and r.is_real is not False and not isinstance(r, sp.AccumBounds) and not r.has(sp.nan):
            if r < 0:
                return True, f"|f| ~ e^({r}*|x|): decadimento esponenziale"
            if r > 0:
                return False, f"|f| ~ e^({r}*|x|): crescita esponenziale"
            try:
                p = sp.limit(sp.log(sp.Abs(g)) / sp.log(u), u, oo)
            except Exception:
                p = None
            if p is not None and p.is_number and p.is_real and not isinstance(p, sp.AccumBounds):
                return bool(p < -1), f"|f| ~ x^({p}) all'infinito: converge se esponente < -1"
        p, r_ = _p_numerico(g, u, oo)
        if p is None:
            return None, "comportamento asintotico non determinato"
        if r_ is not None and r_ < -1e-6:
            return True, f"(stima numerica) decadimento esponenziale, tasso {r_:.4g}"
        if r_ is not None and r_ > 1e-6:
            return False, f"(stima numerica) crescita esponenziale, tasso {r_:.4g}"
        return bool(p < -1 + 1e-9 and abs(p + 1) > 1e-6), f"(stima numerica) |f| ~ x^({p:.4g}) all'infinito"
    g = f.subs(var, c + u) if lato == "+" else f.subs(var, c - u)
    try:
        p = -sp.limit(sp.log(sp.Abs(g)) / sp.log(u), u, 0, "+")
    except Exception:
        p = None
    if p is not None and p.is_number and p.is_real and not isinstance(p, sp.AccumBounds):
        return bool(p < 1), f"|f| ~ |x-{c}|^(-{p}) vicino a {c}: converge se esponente < 1"
    p, _ = _p_numerico(g, u, 0)
    if p is None:
        return None, "comportamento locale non determinato"
    return bool(-p < 1 - 1e-9), f"(stima numerica) |f| ~ |x-{c}|^({p:.4g}) vicino a {c}"


def punti_singolari(f, var, a, b):
    """Estremi infiniti e punti dove f non e' limitata in [a,b]."""
    from sympy.calculus.util import continuous_domain
    pts = []
    for e in (a, b):
        pts.append(e)
    try:
        dom = continuous_domain(f, var, Interval(a, b) if a.is_finite and b.is_finite else S.Reals)
        bd = [q for q in dom.boundary if q.is_finite and (a <= q <= b)]
    except Exception:
        bd = []
    num_, den_ = sp.fraction(sp.together(f))
    if den_.has(var):
        try:
            zeri_den = sp.solveset(den_, var, S.Reals)
        except Exception:
            zeri_den = None
        if isinstance(zeri_den, sp.FiniteSet):
            bd += [d for d in zeri_den if d.is_real and a <= d <= b]
        elif a.is_finite and b.is_finite:      # denominatore trascendente: cerca zeri numericamente
            import numpy as np
            fn = sp.lambdify(var, den_, "numpy")
            xs = np.linspace(float(a), float(b), 4001)
            with np.errstate(all="ignore"):
                ys = np.asarray(fn(xs) + 0 * xs, dtype=float)
            for i in range(len(xs) - 1):
                if np.isfinite(ys[i]) and np.isfinite(ys[i + 1]) and ys[i] * ys[i + 1] <= 0:
                    r = sp.nsimplify(round((xs[i] + xs[i + 1]) / 2, 6), rational=True)
                    bd.append(r)
    out = []
    for q in pts + bd:
        if not any(uguali(q, w) for w in out):
            out.append(q)
    return sorted(out, key=lambda q: float(q) if q.is_finite else (1e300 if q == oo else -1e300))


def analizza_convergenza(f, var, a, b, stampa=True):
    """Converge l'integrale improprio di f su (a,b)? (criteri asintotici del confronto)."""
    a, b = sp.sympify(a), sp.sympify(b)
    esiti = []
    for q in punti_singolari(f, var, a, b):
        lati = []
        if q in (oo, -oo):
            lati = [None]
        else:
            if q > a:
                lati.append("-")
            if q < b:
                lati.append("+")
        for lato in lati:
            if q not in (oo, -oo):
                try:
                    L = sp.limit(f, var, q, lato)
                    if L.is_finite:
                        continue            # f limitata vicino a q: nessun problema
                except Exception:
                    pass
            ok, desc = comportamento_estremo(f, var, q, lato or "+")
            esiti.append((q, lato, ok, desc))
            if stampa:
                riga(f"in {q}{'' if lato is None else ' (da ' + ('destra' if lato == '+' else 'sinistra') + ')'}: "
                     f"{'CONVERGE' if ok else ('DIVERGE' if ok is False else 'non determinato')} - {desc}")
    if not esiti and stampa:
        riga("nessuna singolarita': l'integrale e' proprio (f continua e limitata su [a,b])")
    if any(e[2] is False for e in esiti):
        return False
    if any(e[2] is None for e in esiti):
        return None
    return True


def convergenza_parametro(espr, a, b, param="a", campioni=None, stampa=True):
    """Per quali valori del parametro converge ∫_a^b f dx ? (scansione esatta + bisezione sulle soglie)."""
    p = sp.Symbol(param, real=True)
    f = parse(espr, **{param: p})
    a, b = sp.sympify(parse(str(a))), sp.sympify(parse(str(b)))

    def conv(val):
        fv = f.subs(p, val)
        if fv.has(sp.nan, sp.zoo):
            return "nd"          # valore del parametro per cui f non e' definita
        try:
            return analizza_convergenza(fv, x, a, b, stampa=False)
        except Exception:
            return None

    campioni = campioni or [Rational(m, 2) for m in range(-12, 13)] + [Rational(1, 4), Rational(3, 4), Rational(-1, 4)]
    campioni = sorted(set(campioni))
    esiti = [(c, conv(c)) for c in campioni]
    esclusi = [c for c, e in esiti if e == "nd"]
    esiti = [(c, e) for c, e in esiti if e != "nd"]
    soglie = []
    for (c1, e1), (c2, e2) in zip(esiti[:-1], esiti[1:]):
        if e1 != e2:
            lo, hi = c1, c2
            for _ in range(14):
                mid = sp.nsimplify(round(float((lo + hi) / 2), 5), rational=True, tolerance=1e-5)
                if mid in (lo, hi):
                    break
                em = conv(mid)
                if em == e1:
                    lo = mid
                else:
                    hi = mid
            cand = sp.nsimplify(float(hi), rational=True, tolerance=1e-3)
            for ctest in (cand, sp.nsimplify(float(lo), rational=True, tolerance=1e-3)):
                if lo - Rational(1, 100) <= ctest <= hi + Rational(1, 100) and conv(ctest) != e1:
                    cand = ctest
                    break
            soglie.append((cand, conv(cand)))
    if stampa:
        riga("scansione: " + ", ".join(f"{param}={c}:{'C' if e else ('D' if e is False else '?')}" for c, e in esiti[::2]))
    intervalli = []
    if esiti:
        inizio = -oo
        stato = esiti[0][1]
        for cand, ec in soglie:
            pass
        punti = [s_[0] for s_ in soglie]
        estremi = [-oo] + punti + [oo]
        for i in range(len(estremi) - 1):
            test = (estremi[i] + estremi[i + 1]) / 2 if estremi[i].is_finite and estremi[i + 1].is_finite else (
                estremi[i + 1] - 1 if estremi[i] == -oo else estremi[i] + 1)
            if conv(test):
                intervalli.append(Interval(estremi[i], estremi[i + 1], True, True))
        for cand, ec in soglie:
            if ec is True:
                intervalli.append(sp.FiniteSet(cand))
    ins = sp.Union(*intervalli) if intervalli else S.EmptySet
    if stampa:
        riga(f"soglie trovate: {[s_[0] for s_ in soglie]};  l'integrale converge per {param} in  {ins}"
             + (f"  (valori per cui f non e' definita: {sorted(set(s_[0] for s_ in soglie if s_[1] == 'nd')) or esclusi[:1]})" if esclusi else ""))
    return ins


def integrale(espr, a=None, b=None, stampa=True):
    """Integrale indefinito (a,b assenti) o definito/improprio con valore esatto, numerico e convergenza."""
    f = parse(espr)
    if a is None:
        F = _integra(f, x)
        if stampa:
            riga(f"primitiva: {F} + C" if F is not None else "primitiva non trovata in forma chiusa")
            if F is not None:
                riga("verifica (F' - f):", sp.simplify(sp.diff(F, x) - f))
        return F
    a, b = sp.sympify(parse(str(a))), sp.sympify(parse(str(b)))
    improprio = a in (oo, -oo) or b in (oo, -oo) or bool(
        [q for q in punti_singolari(f, x, a, b) if q.is_finite and _non_limitata(f, q, a, b)])
    out = {}
    if improprio:
        if stampa:
            sezione("INTEGRALE IMPROPRIO: convergenza")
        conv = analizza_convergenza(f, x, a, b, stampa=stampa)
        out["converge"] = conv
        if conv is False:
            if stampa:
                riga("=> l'integrale DIVERGE (o non esiste)")
            return out
    f_r = realifica(f, x)
    val = None
    if a == -b and a.is_finite and sp.simplify(f_r.subs(x, -x) + f_r) == 0:
        val = S.Zero
        if stampa:
            riga("f e' DISPARI e l'intervallo e' simmetrico: l'integrale (convergente) vale 0")
    if val is None:
        val = _integra(f_r if f_r.has(sp.Abs, sp.sign) is False else f, x, a, b)
    num_ = _numerico(f_r, x, a, b)
    out["valore"] = val
    out["numerico"] = num_
    if stampa:
        if val is not None:
            vs = sp.simplify(val)
            if sp.count_ops(vs) > 60 or vs.has(sp.I):
                riga("valore esatto: (espressione troppo lunga) " + f"~ {sp.N(sp.re(val), 12)}")
            else:
                riga(f"valore esatto: {vs}   ~ {sp.N(val, 10)}")
        if num_ is not None:
            riga(f"valore numerico (mpmath): {sp.N(num_, 10)}")
        if val is None and num_ is None:
            riga("valore non calcolabile")
    return out


def _non_limitata(f, q, a, b):
    for lato in ("+", "-"):
        if (lato == "+" and q < b) or (lato == "-" and q > a):
            try:
                if not sp.limit(f, x, q, lato).is_finite:
                    return True
            except Exception:
                return True
    return False


def area_tra_curve(f1, f2, a, b, stampa=True):
    """Area compresa fra y=f1 e y=f2 per x in [a,b]: ∫|f1-f2|."""
    F, G = parse(f1), parse(f2)
    a, b = sp.sympify(parse(str(a))), sp.sympify(parse(str(b)))
    d = sp.simplify(F - G)
    try:
        zeri = [z for z in sp.solveset(d, x, Interval(a, b)) if z.is_real]
    except Exception:
        zeri = []
    if not isinstance(zeri, list):
        zeri = list(zeri)
    zeri = sorted(zeri, key=float)
    pts = [a] + [z for z in zeri if a < z < b] + [b]
    totale = S.Zero
    for p, q in zip(pts[:-1], pts[1:]):
        m = (p + q) / 2
        seg = 1 if sp.N(d.subs(x, m)) > 0 else -1
        I_ = sp.integrate(seg * d, (x, p, q))
        totale += I_
        if stampa:
            riga(f"su [{p}, {q}]: {'f1 sopra f2' if seg > 0 else 'f2 sopra f1'}, contributo {sp.simplify(I_)}")
    totale = sp.simplify(totale)
    if stampa:
        riga(f"intersezioni in [{a},{b}]: {zeri};  AREA = {totale}  ~ {sp.N(totale, 8)}")
    return totale


def funzione_integrale(f_espr, estremo_inf, estremo_sup, stampa=True):
    """G(x) = ∫_{u(x)}^{v(x)} f(t) dt  ->  G'(x) = f(v) v' - f(u) u'  (teorema fondamentale + chain rule)."""
    f = parse(f_espr)
    tt = [s_ for s_ in f.free_symbols][0] if f.free_symbols else t
    u, v = parse(str(estremo_inf)), parse(str(estremo_sup))
    Gp = sp.simplify(f.subs(tt, v) * sp.diff(v, x) - f.subs(tt, u) * sp.diff(u, x))
    if stampa:
        riga(f"G(x) = ∫_({u})^({v}) f({tt}) d{tt},  f({tt}) = {f}")
        riga(f"G'(x) = f({v})*({sp.diff(v, x)}) - f({u})*({sp.diff(u, x)}) = {Gp}")
        crit = sp.solveset(Gp, x, S.Reals)
        riga("punti critici di G (G'=0):", crit)
    return Gp


# ================================================== equazioni differenziali =======
_y = sp.Function("y")


def _parse_edo(testo):
    s_ = testo.replace(" ", "")
    s_ = re.sub(r"y'''", "D3", s_)
    s_ = re.sub(r"y''", "D2", s_)
    s_ = re.sub(r"y'", "D1", s_)
    s_ = re.sub(r"\by\b", "Y0", s_)
    s_ = re.sub(r"dy/dx", "D1", s_)
    loc = dict(D1=_y(x).diff(x), D2=_y(x).diff(x, 2), D3=_y(x).diff(x, 3), Y0=_y(x))
    if "=" in s_:
        l, r = s_.split("=", 1)
        return parse(l, **loc) - parse(r, **loc)
    return parse(s_, **loc)


def edo(testo, x0=None, y0=None, stampa=True):
    """Risolve una EDO (anche con dato di Cauchy). Es.: "y' = y + x", "y' + x*y = x", "y'' - 3*y' + 2*y = exp(x)"."""
    eq = _parse_edo(testo)
    ordine = max([d.derivative_count for d in eq.atoms(sp.Derivative)] or [0])
    classi = sp.classify_ode(eq, _y(x))
    out = dict(equazione=eq, classi=classi)
    if stampa:
        riga(f"equazione: {eq} = 0   (ordine {ordine})")
        riga("tipo (sympy):", ", ".join(c for c in classi[:4]))
    if ordine == 1:
        yp, Y = sp.Symbol("yp"), sp.Symbol("Y")
        espl = sp.solve(eq.subs(_y(x).diff(x), yp), yp)
        if espl and stampa:
            f_xy = espl[0].subs(_y(x), Y)
            riga(f"forma normale: y' = {f_xy}")
            A = sp.diff(f_xy, Y)
            if not A.has(Y):
                Pp, Qq = -A, sp.simplify(f_xy - A * Y)
                riga(f"LINEARE del 1o ordine: y' + P(x) y = Q(x), P = {sp.simplify(Pp)}, Q = {Qq}")
                riga(f"  A(x) = ∫P = {sp.integrate(Pp, x)};  y = e^(-A) (C + ∫ Q e^A dx)")
            sep = sp.separatevars(f_xy, [x, Y], dict=True)
            if sep and sep.get(x) is not None and sep.get(Y) is not None and not A.has(Y) is False:
                riga(f"A VARIABILI SEPARABILI: y' = g(x) h(y) con g(x) = {sp.simplify(sep['coeff'] * sep[x])}, h(y) = {sep[Y]}"
                     f"  ->  ∫ dy/h(y) = ∫ g(x) dx")
    ics = {_y(x0): y0} if x0 is not None else None
    try:
        sol = con_timeout(lambda: sp.dsolve(eq, _y(x), ics=ics))
    except Exception as ex:
        if stampa:
            riga("dsolve non riesce a risolvere:", repr(ex)[:100])
        return out
    out["soluzione"] = sol
    if stampa:
        riga("soluzione:" if ics else "soluzione generale:", sol)
        try:
            riga("verifica per sostituzione:", sp.checkodesol(eq, sol)[0])
        except Exception:
            pass
    if ordine == 1 and ics:
        analisi_locale(eq, x0, y0, stampa)
    return out


def analisi_locale(eq, x0, y0, stampa=True):
    """Comportamento della soluzione di y'=f(x,y), y(x0)=y0 in x0 (derivate successive)."""
    Y = sp.Symbol("Y")
    yp = sp.Symbol("yp")
    espl = sp.solve(eq.subs(_y(x).diff(x), yp), yp)
    if not espl:
        return None
    F = espl[0].subs(_y(x), Y)
    d = [sp.Integer(y0), sp.simplify(F.subs({x: x0, Y: y0}))]
    cur = F
    for _ in range(4):
        cur = sp.diff(cur, x) + sp.diff(cur, Y) * F
        d.append(sp.simplify(cur.subs({x: x0, Y: y0})))
        if len(d) > 4:
            break
    nome = ["y(x0)", "y'(x0)", "y''(x0)", "y'''(x0)", "y''''(x0)"]
    if stampa:
        riga("derivate in x0:", {nome[i]: d[i] for i in range(len(d))})
    # primo termine non nullo dopo y'
    giudizio = None
    if d[1] != 0:
        giudizio = "x0 non e' punto stazionario: la soluzione e' strettamente " + ("crescente" if d[1] > 0 else "decrescente") + " vicino a x0"
    else:
        for ordn in range(2, len(d)):
            if d[ordn] != 0:
                if ordn % 2 == 0:
                    giudizio = "punto stazionario: " + ("MINIMO locale" if d[ordn] > 0 else "MASSIMO locale")
                else:
                    giudizio = "punto stazionario: FLESSO a tangente orizzontale"
                break
    if stampa and giudizio:
        riga(giudizio)
    return d, giudizio


# ======================================================================= curve ===
def _comp(testo):
    parts = [p_ for p_ in re.split(r",(?![^()]*\))", testo) if p_.strip()]
    return sp.Matrix([parse(p_) for p_ in parts])


def _normalizza_piano(nrm, d):
    """Divide per il MCD (se interi) e rende positivo il primo coefficiente non nullo."""
    nrm = sp.Matrix([sp.simplify(c) for c in nrm])
    d = sp.simplify(d)
    if all(c.is_Rational for c in list(nrm) + [d]):
        den = sp.ilcm(*[c.q for c in list(nrm) + [d]])
        vals = [int(c * den) for c in nrm] + [int(d * den)]
        g = sp.igcd(*vals) or 1
        nrm, d = sp.Matrix([sp.Integer(v // g) for v in vals[:3]]), sp.Integer(vals[3] // g)
    primo = next((c for c in nrm if c != 0), 1)
    if primo < 0:
        nrm, d = -nrm, -d
    return nrm, d


def _norma(vel2):
    """sqrt(vel2) semplificata (riconosce i quadrati perfetti, es. 4e^(2t)+4+e^(-2t) = (2e^t+e^-t)^2)."""
    base = sp.sqrt(vel2)
    migliore = sp.simplify(base)
    for cand in (sp.sqrt(sp.factor(sp.together(vel2))), sp.sqrt(sp.factor(sp.expand(vel2)))):
        r = sp.simplify(cand)
        if sp.count_ops(r) < sp.count_ops(migliore):
            migliore = r
    return migliore


def curva(componenti, t0, t1, stampa=True):
    """Curva r(t) in R^2/R^3, t in [t0,t1]: regolarita', lunghezza, chiusa, piana."""
    r = _comp(componenti)
    t0, t1 = sp.sympify(parse(str(t0))), sp.sympify(parse(str(t1)))
    v = r.diff(t)
    vel2 = sp.simplify(v.dot(v))
    vel = _norma(vel2)
    out = dict(r=r, v=v, velocita=vel)
    if stampa:
        riga(f"r(t) = {tuple(r)},  t in [{t0}, {t1}]")
        riga(f"r'(t) = {tuple(sp.simplify(c) for c in v)},   |r'(t)| = {vel}")
    zeri = sp.solveset(vel2, t, Interval(t0, t1)) if vel2.has(t) else (S.Reals if vel2 == 0 else S.EmptySet)
    out["regolare"] = zeri == S.EmptySet
    if stampa:
        riga("REGOLARE (r' != 0 su tutto [t0,t1])" if out["regolare"] else f"NON regolare: r'(t)=0 per t in {zeri}")
    if len(r) == 3:
        biv = sp.simplify(v.cross(v.diff(t)).dot(v.cross(v.diff(t))))
        zb = sp.solveset(biv, t, Interval(t0, t1)) if biv.has(t) else (S.Reals if biv == 0 else S.EmptySet)
        out["biregolare"] = zb == S.EmptySet
        if stampa:
            riga("BIREGOLARE (r' x r'' != 0)" if out["biregolare"] else f"non biregolare: r' x r'' = 0 per t in {zb}")
    L = _integra(vel, t, t0, t1)
    num_ = _numerico(vel, t, t0, t1)
    out["lunghezza"] = L
    if stampa:
        riga(f"lunghezza = ∫|r'| dt = {sp.simplify(L) if L is not None else '?'}   ~ {sp.N(L, 10) if L is not None else sp.N(num_, 10)}")
    chiusa = sp.simplify(r.subs(t, t0) - r.subs(t, t1)) == sp.zeros(len(r), 1)
    out["chiusa"] = chiusa
    if stampa:
        riga("curva CHIUSA (r(t0) = r(t1))" if chiusa else "curva non chiusa")
    if len(r) == 3:
        r1, r2, r3 = v, v.diff(t), v.diff(t, 2)
        det = sp.simplify(sp.Matrix.hstack(r1, r2, r3).det())
        out["piana"] = det == 0
        if stampa:
            if det == 0:
                nrm = r1.cross(r2)
                nrm = sp.simplify(nrm.subs(t, t0)) if nrm.has(t) else nrm
                d0 = sp.simplify(nrm.dot(r.subs(t, t0)))
                nrm, d0 = _normalizza_piano(nrm, d0)
                riga(f"curva PIANA (det[r',r'',r'''] = 0): piano {str_piano(nrm, d0)}")
            else:
                riga(f"curva NON piana (det[r',r'',r'''] = {det})")
    return out


def autointersezioni(componenti, t0, t1, N=700, stampa=True):
    """Ricerca numerica di coppie t<u con r(t)=r(u) (curva non semplice)."""
    import numpy as np
    r = _comp(componenti)
    f = sp.lambdify(t, list(r), "numpy")
    a, b = float(sp.N(t0)), float(sp.N(t1))
    ts = np.linspace(a, b, N)
    P = np.array([np.broadcast_to(np.asarray(c, dtype=float), ts.shape) for c in f(ts)]).T
    d = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    passo = (b - a) / N
    trovate = []
    for i in range(N):
        for j in range(i + 1, N):
            if (j - i) * passo > 0.2 * (b - a) / 10 and d[i, j] < 6 * np.linalg.norm(P[1] - P[0]) + 1e-9:
                u = np.array([ts[i], ts[j]])
                for _ in range(40):
                    res = np.array(f(u[0]), dtype=float) - np.array(f(u[1]), dtype=float)
                    J = np.zeros((len(res), 2))
                    h = 1e-7
                    J[:, 0] = (np.array(f(u[0] + h), dtype=float) - np.array(f(u[0] - h), dtype=float)) / (2 * h)
                    J[:, 1] = -(np.array(f(u[1] + h), dtype=float) - np.array(f(u[1] - h), dtype=float)) / (2 * h)
                    step = np.linalg.lstsq(J, -res, rcond=None)[0]
                    u = u + step
                    if np.linalg.norm(step) < 1e-13:
                        break
                res = np.linalg.norm(np.array(f(u[0]), dtype=float) - np.array(f(u[1]), dtype=float))
                tt, uu = sorted(u)
                if res < 1e-9 and a - 1e-9 <= tt and uu <= b + 1e-9 and uu - tt > 1e-3:
                    if not any(abs(tt - x_) < 1e-6 and abs(uu - y_) < 1e-6 for x_, y_ in trovate):
                        trovate.append((tt, uu))
    # escludi la coppia (t0,t1) che descrive solo la chiusura della curva
    chiusura = [(x_, y_) for x_, y_ in trovate if abs(x_ - a) < 1e-6 and abs(y_ - b) < 1e-6]
    interne = [(x_, y_) for x_, y_ in trovate if (x_, y_) not in chiusura]
    if stampa:
        if interne:
            riga("curva NON SEMPLICE: r(t) = r(u) per " + ", ".join(
                f"(t,u) = ({sp.nsimplify(x_, rational=True, tolerance=1e-8)}, {sp.nsimplify(y_, rational=True, tolerance=1e-8)})"
                for x_, y_ in interne))
        else:
            riga("curva SEMPLICE (nessuna autointersezione trovata numericamente)" + (" [chiusa: r(t0)=r(t1)]" if chiusura else ""))
    return interne


def piano_osculatore(componenti, t0, stampa=True):
    """Piano per r(t0) contenente r'(t0) e r''(t0): normale r' x r''."""
    r = _comp(componenti)
    t0 = sp.sympify(parse(str(t0)))
    P = r.subs(t, t0)
    v1, v2 = r.diff(t).subs(t, t0), r.diff(t, 2).subs(t, t0)
    n_ = v1.cross(v2).applyfunc(sp.simplify)
    nrm, d0 = _normalizza_piano(n_, n_.dot(P))
    if stampa:
        riga(f"r({t0}) = {tuple(P)}, r' = {tuple(v1)}, r'' = {tuple(v2)}, normale r' x r'' = {tuple(n_)}")
        riga(f"piano: {str_piano(nrm, d0)}" if n_ != sp.zeros(3, 1) else "r' e r'' paralleli: piano non determinato")
    return nrm, d0


def retta_tangente_curva(componenti, t0, stampa=True):
    r = _comp(componenti)
    t0 = sp.sympify(parse(str(t0)))
    P = r.subs(t, t0)
    d = sp.simplify(r.diff(t).subs(t, t0))
    s = sp.Symbol("s")
    par = [sp.simplify(P[i] + s * d[i]) for i in range(len(r))]
    if stampa:
        riga(f"punto P = {tuple(P)}, vettore tangente r'({t0}) = {tuple(d)}")
        riga("retta tangente: " + ", ".join(f"{n_} = {e}" for n_, e in zip("xyz", par)) + "   (s in R)")
    return P, d


def integrale_di_linea(componenti, f_espr, t0, t1, stampa=True):
    """∫_γ f(x,y,z) ds = ∫ f(r(t)) |r'(t)| dt."""
    r = _comp(componenti)
    t0, t1 = sp.sympify(parse(str(t0))), sp.sympify(parse(str(t1)))
    X, Y, Z = sp.symbols("x y z", real=True)
    f = parse(f_espr, x=X, y=Y, z=Z)
    sost = {X: r[0], Y: r[1]}
    if len(r) == 3:
        sost[Z] = r[2]
    ft = sp.simplify(f.subs(sost))
    vel = _norma(sp.simplify(r.diff(t).dot(r.diff(t))))
    integrando = sp.simplify(ft * vel)
    val = _integra(integrando, t, t0, t1)
    num_ = _numerico(integrando, t, t0, t1)
    if stampa:
        riga(f"f(r(t)) = {ft},  |r'(t)| = {vel}")
        riga(f"∫ f ds = ∫ {integrando} dt su [{t0},{t1}] = {sp.simplify(val) if val is not None else '?'}   ~ {sp.N(val if val is not None else num_, 10)}")
    return val
