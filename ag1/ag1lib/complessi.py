"""Numeri complessi: forme, equazioni (anche con |z| e coniugato), radici, regioni del piano di Gauss."""
import ast
import numpy as np
import os

import sympy as sp
from sympy import I, Rational, pi, sqrt

from .util import OUT_DIR, complessi_uguali, num, riga, sezione, uguali

z = sp.Symbol("z")
a_, b_ = sp.symbols("a b", real=True)


def parse_c(espr):
    from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication_application, parse_expr,
                                            standard_transformations)
    tr = standard_transformations + (implicit_multiplication_application, convert_xor)
    loc = {"z": z, "i": I, "I": I, "j": I, "e": sp.E, "pi": pi, "conj": sp.conjugate, "Re": sp.re, "Im": sp.im,
           "re": sp.re, "im": sp.im, "abs": sp.Abs, "mod": sp.Abs, "arg": sp.arg, "ln": sp.log, "log": sp.log,
           "sen": sp.sin, "tg": sp.tan}
    return parse_expr(espr, local_dict=loc, transformations=tr)


# ----------------------------------------------------------------- forme ----
def forma_esp(w):
    rho, th = sp.simplify(sp.Abs(w)), sp.simplify(sp.arg(w))
    return f"{rho}*e^(i*({th}))"


def analizza(w, stampa=True):
    """Modulo, argomento, Re, Im, forma algebrica ed esponenziale di un numero complesso."""
    w = sp.sympify(w)
    alg = sp.simplify(sp.expand_complex(w))
    re_, im_ = sp.simplify(sp.re(alg)), sp.simplify(sp.im(alg))
    rho = sp.simplify(sp.Abs(alg))
    out = dict(alg=alg, re=re_, im=im_, mod=rho)
    if alg != 0:
        th = sp.simplify(sp.arg(alg))
        out["arg_principale"] = th                      # (-pi, pi]
        out["arg_0_2pi"] = th if num(th).real >= 0 else sp.simplify(th + 2 * pi)
    if stampa:
        riga(f"forma algebrica:    {alg}   (~ {sp.N(alg, 8)})")
        riga(f"Re = {re_},  Im = {im_}")
        riga(f"modulo |z| = {rho}   (~ {sp.N(rho, 8)})")
        if alg != 0:
            riga(f"Arg in (-pi, pi]:   {out['arg_principale']}   (~ {sp.N(out['arg_principale'], 8)})")
            riga(f"arg in [0, 2pi):    {out['arg_0_2pi']}")
            riga(f"forma esponenziale: {rho}*e^(i*({out['arg_principale']}))")
        riga("puramente reale" if im_ == 0 else ("puramente immaginario" if re_ == 0 else "ne' reale ne' immaginario puro"))
    return out


def radici_n(w, m, r=None, phi=None):
    """Radici m-esime di w: lista (z_k, rho, theta_k)."""
    r = sp.simplify(sp.Abs(w)) if r is None else r
    phi = sp.simplify(sp.arg(w)) if phi is None else phi
    rho = sp.simplify(r ** Rational(1, m))
    out = []
    for j in range(m):
        th = sp.simplify((phi + 2 * pi * j) / m)
        out.append((rho * sp.exp(I * th), rho, th))
    return out


def stampa_radici(w, m):
    riga(f"z^{m} = {w}:  |w| = {sp.simplify(sp.Abs(w))}, arg w = {sp.simplify(sp.arg(w))}  ->  {m} radici (vertici di un {m}-gono regolare)")
    for zk, r, th in radici_n(w, m):
        riga(f"z = {r} e^(i*({th})) = {sp.simplify(sp.expand_complex(zk))}   ~ {sp.N(zk, 6)}")


# -------------------------------------------------------------- equazioni ----
def _a_cartesiane(e):
    """z=a+ib; ogni |w| diventa una variabile r>=0 con il vincolo r^2 = Re(w)^2 + Im(w)^2.
    Restituisce (espressione, vincoli, variabili ausiliarie)."""
    rs = []

    def sost(q):
        w = sp.expand_complex(q.args[0].subs(z, a_ + I * b_))
        r = sp.Symbol(f"r{len(rs)}", nonnegative=True)
        rs.append((r, sp.expand(sp.re(w) ** 2 + sp.im(w) ** 2)))
        return r
    e = e.replace(lambda q: isinstance(q, sp.Abs), sost)   # prima dei moduli: subs li valuterebbe da solo
    e = e.subs(z, a_ + I * b_)
    return sp.expand_complex(e), [r ** 2 - m for r, m in rs], [r for r, _ in rs]


def _binomia(espr):
    """z^n - w  ->  (n, w) se l'espressione e' del tipo c1*z^n + c0."""
    try:
        P = sp.Poly(espr, z)
    except Exception:
        return None
    ts = P.terms()
    if len(ts) == 2 and {t_[0][0] for t_ in ts} == {0, P.degree()} and P.degree() >= 2:
        c1 = [c for (m,), c in ts if m == P.degree()][0]
        c0 = [c for (m,), c in ts if m == 0][0]
        return P.degree(), sp.simplify(-c0 / c1)
    return None


def risolvi_equazione(eq, stampa=True):
    """eq: 'lhs = rhs' (piu' equazioni separate da ';' o 'and'). Restituisce le soluzioni
    (oppure (soluzioni, famiglie) se ce ne sono infinite)."""
    import re as _re
    parti = [p_.strip() for p_ in _re.split(r"\s+and\s+|;", eq) if p_.strip()]
    espr_list = []
    for pt in parti:
        if "=" in pt:
            l, r = pt.split("=", 1)
            espr_list.append(parse_c(l) - parse_c(r))
        else:
            espr_list.append(parse_c(pt))
    solo_z = len(espr_list) == 1 and not espr_list[0].has(sp.conjugate, sp.Abs, sp.re, sp.im, sp.arg)
    sol, infinite = [], None
    forme = {}   # soluzione -> (rho, theta) quando note in forma esponenziale
    coniche = []
    if solo_z:
        espr = espr_list[0]
        bin_ = _binomia(sp.together(espr).as_numer_denom()[0])
        if bin_:
            n_, w = bin_
            rr = radici_n(w, n_)
            sol = [zk for zk, _, _ in rr]
            forme = {id(zk): (rho_, th_) for zk, rho_, th_ in rr}
            if stampa:
                riga(f"equazione binomia z^{n_} = {w}: |w| = {sp.simplify(sp.Abs(w))}, arg w = {sp.simplify(sp.arg(w))};"
                     f" {n_} radici sui vertici di un {n_}-gono regolare")
        else:
            try:
                rad = sp.roots(sp.Poly(sp.together(espr).as_numer_denom()[0], z), z)
                sol = list(rad.keys()) if rad else sp.solve(espr, z)
            except Exception:
                sol = sp.solve(espr, z)
    else:
        eqs, aus = [], []
        for espr in espr_list:
            cart, vinc, ax_ = _a_cartesiane(espr)
            eqs += [sp.simplify(sp.re(cart)), sp.simplify(sp.im(cart))] + vinc
            aus += ax_
        res = sp.solve(eqs, [a_, b_] + aus, dict=True)
        for d in res:
            if a_ in d and b_ in d and not (d[a_].free_symbols | d[b_].free_symbols):
                sol.append(sp.simplify(d[a_] + I * d[b_]))
            else:
                infinite = infinite or []
                infinite.append(d)
        sol = [s_ for s_ in sol if all(_verifica(e_, s_) for e_ in espr_list)]
        if infinite and stampa:
            riga("insieme infinito di soluzioni (curva/regione). Condizioni su a=Re z, b=Im z:")
            for d in infinite:
                riga("   ", d)
            if len(aus) == 1:
                for d in infinite:
                    val = d.get(aus[0])
                    if val is not None and not val.free_symbols:
                        F = sp.expand(val ** 2 - (aus[0] ** 2 - eqs[-1]))
                        coniche.append(F)
                        riga(f"   equazione cartesiana: {F} = 0  ->  {classifica_conica(F)}")
    uniche = []
    for s_ in sol:
        if not any(abs(num(s_) - num(t_)) < 1e-9 for t_ in uniche):
            uniche.append(s_)
    if stampa:
        if not uniche and not infinite:
            riga("nessuna soluzione in C")
        for s_ in uniche:
            ge = sp.N(s_, 6)
            if id(s_) in forme:
                rho_, th_ = forme[id(s_)]
                riga(f"z = {rho_}*e^(i*({th_}))   ~ {ge}")
                continue
            alg = sp.simplify(sp.expand_complex(s_))
            riga(f"z = {alg}" + ("" if alg == 0 else f"   = {forma_esp(alg)}") + f"   ~ {ge}")
        riga(f"numero di soluzioni distinte: {len(uniche)}" + (" (piu' un insieme infinito)" if infinite else ""))
    return uniche if not infinite else (uniche, infinite)


def classifica_conica(F):
    """F(a,b)=0 di secondo grado: circonferenza, ellisse, parabola, iperbole o rette."""
    try:
        P = sp.Poly(F, a_, b_)
        if P.total_degree() == 1:
            return "retta"
        if P.total_degree() != 2:
            return "curva di grado > 2"
        A = P.coeff_monomial(a_ ** 2)
        B = P.coeff_monomial(a_ * b_)
        C = P.coeff_monomial(b_ ** 2)
        d = B ** 2 - 4 * A * C
        if d < 0:
            return "circonferenza" if B == 0 and A == C else "ellisse"
        if d == 0:
            return "parabola (o coppia di rette parallele)"
        return "iperbole (o coppia di rette incidenti)"
    except Exception:
        return "?"


def _verifica(espr, s_):
    try:
        return abs(complex(sp.N(espr.subs(z, s_).doit(), 20))) < 1e-8
    except Exception:
        return True


# ---------------------------------------------------------------- regioni ----
class _Catena(ast.NodeTransformer):
    """a<b<c -> (a<b)&(b<c);  and/or/not -> &,|,~;  a==b -> abs(a-b)<tol."""

    def visit_Compare(self, node):
        self.generic_visit(node)
        parti = []
        sx = node.left
        for op, dx in zip(node.ops, node.comparators):
            if isinstance(op, ast.Eq):
                parti.append(ast.Compare(left=ast.Call(func=ast.Name("abs", ast.Load()),
                                                       args=[ast.BinOp(sx, ast.Sub(), dx)], keywords=[]),
                                         ops=[ast.Lt()], comparators=[ast.Name("_tol", ast.Load())]))
            else:
                parti.append(ast.Compare(left=sx, ops=[op], comparators=[dx]))
            sx = dx
        out = parti[0]
        for p in parti[1:]:
            out = ast.BinOp(out, ast.BitAnd(), p)
        return out

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        op = ast.BitAnd() if isinstance(node.op, ast.And) else ast.BitOr()
        out = node.values[0]
        for v in node.values[1:]:
            out = ast.BinOp(out, op, v)
        return out

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not):
            return ast.UnaryOp(ast.Invert(), node.operand)
        return node


def maschera_regione(cond, R=4.0, N=900, arg_0_2pi=False):
    """Maschera booleana dei punti z del piano che soddisfano la condizione (stringa python/numpy)."""
    import numpy as np
    X, Y = np.meshgrid(np.linspace(-R, R, N), np.linspace(-R, R, N))
    Z = X + 1j * Y
    scala = 2 * R / N
    albero = _Catena().visit(ast.parse(cond.replace("^", "**").replace("|z|", "abs(z)"), mode="eval"))
    ast.fix_missing_locations(albero)
    arg = (lambda w: np.mod(np.angle(w), 2 * np.pi)) if arg_0_2pi else np.angle
    env = dict(z=Z, abs=np.abs, arg=arg, re=np.real, im=np.imag, conj=np.conj, exp=np.exp, log=np.log,
               sqrt=np.sqrt, pi=np.pi, e=np.e, sin=np.sin, cos=np.cos, i=1j, j=1j, _tol=2.5 * scala,
               Re=np.real, Im=np.imag, Arg=arg)
    with np.errstate(all="ignore"):
        m = eval(compile(albero, "<regione>", "eval"), {"__builtins__": {}}, env)
    return X, Y, np.asarray(m, dtype=bool)


def disegna_regione(cond, png="regione.png", R=4.0, arg_0_2pi=False, punti=()):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(OUT_DIR, exist_ok=True)
    X, Y, m = maschera_regione(cond, R, arg_0_2pi=arg_0_2pi)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(m, extent=(-R, R, -R, R), origin="lower", cmap="Blues", alpha=0.85)
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_title(cond, fontsize=9)
    for p in punti:
        pc = complex(sp.N(parse_c(p)))
        ax.plot([pc.real], [pc.imag], "o", color="crimson")
    path = os.path.join(OUT_DIR, png)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path, m


def stampa_regione(cond, R=4.0, arg_0_2pi=False, punti=(), png="regione.png"):
    path, m = disegna_regione(cond, png, R, arg_0_2pi, punti)
    import numpy as np
    frazione = m.mean()
    bordo = m[0, :].any() or m[-1, :].any() or m[:, 0].any() or m[:, -1].any()
    riga(f"condizione: {cond}")
    if not m.any():
        riga("nessun punto trovato nella finestra: regione vuota (o contenuta in un insieme di misura nulla / fuori finestra)")
    else:
        riga(f"area stimata nella finestra [-{R},{R}]^2: {frazione * (2 * R) ** 2:.3f}  "
             f"({'illimitata (tocca il bordo della finestra)' if bordo else 'sembra limitata'})")
        ys, xs = np.nonzero(m)
        riga(f"Re z in [{(-R + xs.min() * 2 * R / (m.shape[1] - 1)):.2f}, {(-R + xs.max() * 2 * R / (m.shape[1] - 1)):.2f}], "
             f"Im z in [{(-R + ys.min() * 2 * R / (m.shape[0] - 1)):.2f}, {(-R + ys.max() * 2 * R / (m.shape[0] - 1)):.2f}]")
    for p in punti:
        pc = complex(sp.N(parse_c(p)))
        i_ = int(round((pc.imag + R) / (2 * R) * (m.shape[0] - 1)))
        j_ = int(round((pc.real + R) / (2 * R) * (m.shape[1] - 1)))
        dentro = bool(m[i_, j_]) if 0 <= i_ < m.shape[0] and 0 <= j_ < m.shape[1] else False
        riga(f"il punto {p} = {pc:.3f} {'APPARTIENE' if dentro else 'NON appartiene'} alla regione")
    riga(f"disegno: {path}")
    return m
