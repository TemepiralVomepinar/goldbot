"""Esercizi dei temi d'esame degli anni precedenti, risolti con il pacchetto e confrontati con le soluzioni
ufficiali (le risposte attese sono prese dai PDF delle soluzioni)."""
import sympy as sp
from sympy import Interval, Rational, S, Union, exp, oo, pi, sqrt

from . import complessi as C
from . import geometria as G
from . import integrali as I_
from . import successioni as SU
from .funzioni import Studio, estremi_assoluti, valore_in
from .util import k, lim, n, num, parse, registra, riga, t, titolo, uguali, verifica, x

TEMI = {}


def tema(nome, descr):
    def deco(fn):
        TEMI[nome] = dict(descr=descr, fn=fn)
        return fn
    return deco


def _estremo(St, c):
    """(tipo, valore, globale) del punto di estremo in x=c, se esiste."""
    for cc, tipo, v, glob in St.estremi():
        if uguali(cc, c):
            return tipo.split(" ")[0], v, glob
    return None


def _tipo_nodo(St, c):
    for d in St.info:
        if uguali(d["c"], c):
            return d["tipo"]


def _asint(St):
    A = St.asintoti()
    return ([(p, l) for p, l, _ in A["verticali"]], [(nm, L) for nm, L in A["orizzontali"]],
            [(nm, m, q) for nm, m, q in A["obliqui"]])


def _valori(sol):
    """[{a: v}, ...] -> [v, ...]"""
    return [list(d.values())[0] for d in sol] if isinstance(sol, list) else sol


# ============================================================ prime prove ====
@tema("pp_2024_25_A", "Prima prova 11/11/2024 [A]")
def pp_2024_25_A():
    titolo("pp 2024-25 A", "sqrt(x^2-1)/(x-2), (-1)^n arctan n, log(cos x)/(x sin 2x), (2+i)e^(1+3 pi i)")
    St = Studio(sp.sqrt(x ** 2 - 1) / (x - 2), x)
    v, o, _ = _asint(St)
    verifica("dominio (-oo,-1] U [1,2) U (2,oo)", St.dominio,
             Union(Interval(-oo, -1), Interval.Ropen(1, 2), Interval.open(2, oo)))
    verifica("asintoto verticale x=2", sorted({p for p, _ in v}), [2])
    verifica("asintoti orizzontali y=-1 (-oo) e y=1 (+oo)", sorted([(nm, L) for nm, L in o], key=str), sorted([("-oo", -1), ("+oo", 1)], key=str))
    verifica("x=+-1: massimi relativi, f'->+-oo (non derivabile)", (_estremo(St, -1)[0], _estremo(St, 1)[0]), ("massimo", "massimo"))
    verifica("Im f = (-oo,0] U (1,+oo)", St.immagine, Union(Interval(-oo, 0), Interval.open(1, oo)))
    St2 = Studio(sp.sqrt(x ** 2 - 1) / (2 - x), x)
    verifica("[B] Im f = (-oo,-1) U [0,+oo)", St2.immagine, Union(Interval.open(-oo, -1), Interval(0, oo)))
    verifica("lim log(cos x)/(x sin 2x) = -1/4", lim(sp.log(sp.cos(x)) / (x * sp.sin(2 * x)), x, 0), -Rational(1, 4))
    r = SU.successione("(-1)^n*atan(n)", 1, stampa=False)
    verifica("sup{(-1)^n arctan n} = pi/2 (non max)", (r["sup"], r["sup_att"]), (pi / 2, False))
    w = C.analizza(C.parse_c("(2+i)*exp(1+3*pi*i)"), stampa=False)
    verifica("|(2+i)e^(1+3 pi i)| = sqrt(5) e", w["mod"], sqrt(5) * sp.E)


@tema("pp_2023_24_A", "Prima prova 3/11/2023 [A]")
def pp_2023_24_A():
    titolo("pp 2023-24 A", "(x-1)^2 e^-|x|, z^2=|z|+2, (cos x)^(1/x^2), insiemi 1/2k e 1/(2k+1)")
    St = Studio((x - 1) ** 2 * exp(-Abs(x)), x)
    verifica("x=0 punto angoloso", _tipo_nodo(St, 0), "punto angoloso")
    verifica("max in -1 e 3, min in 1", (_estremo(St, -1)[0], _estremo(St, 3)[0], _estremo(St, 1)[0]), ("massimo", "massimo", "minimo"))
    verifica("Im f = [0, 4/e]", St.immagine, Interval(0, 4 / sp.E))
    sol = C.risolvi_equazione("z^2 = abs(z)+2", stampa=False)
    verifica_c = C.complessi_uguali(sol, [2, -2])
    registra("z^2=|z|+2: soluzioni solo reali (+-2)", verifica_c)
    z0 = sp.I * exp((4 + sp.I * pi) / 20)
    w = C.analizza(z0 ** 10, stampa=False)
    verifica("w=z^10: |w| = e^2, arg w = 3pi/2 (cioe' -pi/2)", (w["mod"], w["arg_principale"]), (sp.E ** 2, -pi / 2))
    verifica("lim (cos x)^(1/x^2) = 1/sqrt(e)", lim(sp.cos(x) ** (1 / x ** 2), x, 0), exp(-Rational(1, 2)))
    A = SU.estremi_successione([(1 / (2 * k), k, 1)], stampa=False)
    B = SU.estremi_successione([(1 / (2 * k + 1), k, 0)], stampa=False)
    verifica("inf A = inf B = 0, sup A=1/2 (max), sup B=1 (max), niente minimo", (A, B), ((Rational(1, 2), True, 0, False), (1, True, 0, False)))


@tema("pp_2022_23_A", "Prima prova 4/11/2022 [A]")
def pp_2022_23_A():
    titolo("pp 2022-23 A", "sup (1+1/n)^n, z^8=(2+i)^4, log(1+x^5)/(3x^2 sin x^3)")
    r = SU.successione("(1+1/n)^n", 1, stampa=False)
    verifica("sup{(1+1/n)^n} = e (non max), min = 2", (r["sup"], r["sup_att"], r["inf"], r["inf_att"]), (sp.E, False, 2, True))
    sol = C.risolvi_equazione("z^8=(2+i)^4", stampa=False)
    verifica("z^8=(2+i)^4: 8 soluzioni distinte", len(sol), 8)
    verifica("lim log(1+x^5)/(3 x^2 sin x^3) = 1/3", lim(sp.log(1 + x ** 5) / (3 * x ** 2 * sp.sin(x ** 3)), x, 0), Rational(1, 3))


@tema("pp_2025_26_A", "Prima prova 7/11/2025 [A]")
def pp_2025_26_A():
    titolo("pp 2025-26 A", "(-1)^n(3n+2)/n^2, z^2(z^2+i)=0, e^(1/|x-1|)(x-1/4)")
    r = SU.successione("(-1)^n*(3*n+2)/n^2", 1, stampa=False)
    verifica("max=2 e min=-5 esistono; converge a 0", (r["sup"], r["sup_att"], r["inf"], r["inf_att"], r["limite"]), (2, True, -5, True, 0))
    verifica("|a_n| = (3n+2)/n^2 decrescente", SU.successione("(3*n+2)/n^2", 1, stampa=False)["sup"], 5)
    sol = C.risolvi_equazione("z^2*(z^2+i) = 0", stampa=False)
    verifica("z^2(z^2+i)=0: 3 soluzioni distinte (non 4)", len(sol), 3)
    St = Studio(exp(1 / Abs(x - 1)) * (x - Rational(1, 4)), x)
    v, o, ob = _asint(St)
    verifica("asintoto verticale x=1", [p for p, _ in v], [1, 1])
    verifica("asintoti obliqui y=x+3/4 (+oo), y=x-5/4 (-oo)", sorted([(nm, m, q) for nm, m, q in ob], key=str),
             sorted([("+oo", 1, Rational(3, 4)), ("-oo", 1, -Rational(5, 4))], key=str))
    verifica("minimo locale in x=5/2 (non globale)", _estremo(St, Rational(5, 2))[::2], ("minimo", False))
    verifica("zero in x=1/4", [z for z, _ in St.zeri()], [Rational(1, 4)])


# =================================================================== appelli ===
@tema("app_21_1_26", "Primo appello 21/1/2026 [A]")
def app_21_1_26():
    titolo("app 21/1/2026", "arctan(1/(1-x))-x/2, curva e^t(cos t,sin t,1), complessi, famiglie di intervalli")
    St = Studio(sp.atan(1 / (1 - x)) - x / 2, x)
    verifica("x=1: discontinuita' di prima specie con salto -pi", "salto -pi" in _tipo_nodo(St, 1), True)
    v, o, ob = _asint(St)
    verifica("asintoto obliquo y=-x/2 (+-oo)", sorted([(nm, m, q) for nm, m, q in ob], key=str), sorted([("+oo", -Rational(1, 2), 0), ("-oo", -Rational(1, 2), 0)], key=str))
    verifica("min locale in 0, max locale in 2 (nessuno globale)", (_estremo(St, 0)[0::2], _estremo(St, 2)[0::2]), (("minimo", False), ("massimo", False)))
    verifica("f'' >0 per x<1 (convessa), <0 per x>1 (concava)", [pz["segno"] for T in St.tratti for pz in T.conv], [1, -1])
    sol = C.risolvi_equazione("abs(z-1) = conj(z) - i", stampa=False)
    verifica("|z-1|=conj(z)-i: una sola soluzione", len(sol), 1)
    sol = C.risolvi_equazione("re(z^-2) = 0 and abs(z) = sqrt(2)", stampa=False)
    verifica("A = {Re(z^-2)=0, |z|=sqrt2}: 4 punti (vertici di un quadrato di lato 2)", C.complessi_uguali(sol, [1 + sp.I, 1 - sp.I, -1 + sp.I, -1 - sp.I]), True)
    verifica("lim f/log(1-x^2) con f ~ x^2/2: -1/2", lim((x ** 2 / 2) / sp.log(1 - x ** 2), x, 0), -Rational(1, 2))
    verifica("int_{-1}^{1} e^{x^2} x^{-1/3} cos x dx = 0", I_.integrale("exp(x^2)*x^(-1/3)*cos(x)", -1, 1, stampa=False)["valore"], 0)
    verifica("x+a y-2z=1 parallelo a (2,-1,-3) per a=8", _valori(G.vettore_parallelo_piano("(2,-1,-3)", "x+a*y-2*z=1", stampa=False)), [8])
    verifica("curva e^t(cos t, sin t, 1): lunghezza sqrt(3)", I_.curva("exp(t)*cos(t), exp(t)*sin(t), exp(t)", 0, "log(2)", stampa=False)["lunghezza"], sqrt(3))
    verifica("retta tangente in t=0: direzione (1,1,1)", list(I_.retta_tangente_curva("exp(t)*cos(t), exp(t)*sin(t), exp(t)", 0, stampa=False)[1]), [1, 1, 1])
    verifica("r (tangente) e asse x sono sghembe", G.posizione_rette("1,0,1", "1,1,1", "0,0,0", "1,0,0", stampa=False)["tipo"], "sghembe")
    n_, d_ = G.piano_punti_parallelo("1,0,1", "2,1,2", "1,0,0", stampa=False)
    verifica("piano per r parallelo all'asse x: y - z = -1  e distanza dall'origine 1/sqrt2",
             (G.str_piano(n_, d_), G.distanza_punto_piano("(0,0,0)", "y-z=-1", stampa=False)[0]), ("y - z = -1", sqrt(2) / 2))
    F = SU.famiglia_intervalli("1/n", "2/n")
    verifica("U (1/n,2/n) = (0,2)\\{1}; intersezione vuota", (F["unione"], F["intersezione"]), (Union(Interval.open(0, 1), Interval.open(1, 2)), S.EmptySet))
    verifica("Cauchy y'=4x^3 y, y(1)=-1: y=-e^(x^4-1)", sp.simplify(I_.edo("y' = 4*x^3*y", 1, -1, stampa=False)["soluzione"].rhs + exp(x ** 4 - 1)), 0)


@tema("app_11_2_26", "Secondo appello 11/2/2026 [A]")
def app_11_2_26():
    titolo("app 11/2/2026", "famiglie, limite con alpha, area, Cauchy, rette, angolo, curva e piani")
    s1 = SU.famiglia_intervalli("1/n^2", "1/n", 2, False, False)["unione"]
    s2 = SU.famiglia_intervalli("n", "n^2", 2, False, False)["unione"]
    verifica("U [1/n^2,1/n] = (0,1/2]; U [n,n^2] = [2,oo)", (s1, s2), (Interval.Lopen(0, Rational(1, 2)), Interval(2, oo)))
    verifica("lim n^2(e^(a/n)-a/n-cos(1/n)) = 3  <=>  a = +-sqrt5",
             sorted(SU.limite_parametro("n^2*(exp(a/n)-a/n-cos(1/n))", "a", "n", "oo", 3, stampa=False)["soluzioni"], key=lambda v: float(v)), [-sqrt(5), sqrt(5)])
    verifica("area fra x^2-1 e cos(pi x/2): 4/pi + 4/3", I_.area_tra_curve("x^2-1", "cos(pi*x/2)", -1, 1, stampa=False), 4 / pi + Rational(4, 3))
    verifica("y'=xy, y(0)=2: y=2e^(x^2/2)", sp.simplify(I_.edo("y' = x*y", 0, 2, stampa=False)["soluzione"].rhs - 2 * exp(x ** 2 / 2)), 0)
    r = G.posizione_rette("0,-1,0", "1,1,1", "1,0,1", "2,-1,0", stampa=False)
    verifica("r e s incidenti, contenute nel piano di normale (1,2,-3)", (r["tipo"], G.piano_due_rette("0,-1,0", "1,1,1", "1,0,1", "2,-1,0", stampa=False)[0].T.tolist()[0]), ("incidenti", [1, 2, -3]))
    verifica("angolo fra (1,0,t) e (0,2,2) uguale a pi/3 per t=1", G.angolo_vettori("(1,0,t)", "(0,2,2)", stampa=False, uguale_a="pi/3")[1], [1])
    sol = sp.solveset(t + 2 - t * (sp.log(t) - 1) - 2, t, Interval.open(0, oo))
    verifica("curva (log t, t+2, t(log t-1)) incontra y-z=2 solo per t=e^2", sol, sp.FiniteSet(sp.E ** 2))
    d = G.retta_da_piani("y=e*x", "y-z=2", stampa=False)[0]
    verifica("r (piani y=ex, y-z=2) parallela a s tangente (direzione (1/e,1,1))", G.posizione_rette("0,0,-2", f"{d[0]},{d[1]},{d[2]}", "1,e+2,0", "1/e,1,1", stampa=False)["tipo"], "parallele (distinte)")
    St = Studio(exp(-Abs(x)) * sp.sin(x), x)
    verifica("f=e^-|x| sin x e' derivabile in 0 con f'(0)=1", (_tipo_nodo(St, 0), [d["dsx"] for d in St.info if d["c"] == 0]), ("derivabile", [1]))


@tema("app_30_6_26", "Quarto appello 30/6/2026")
def app_30_6_26():
    titolo("app 30/6/2026", "z=(i-1)/(1+i sqrt3), |z|^2=z^3, x^(4/3)(2-x)^(1/3), rette, curve")
    w = C.analizza(C.parse_c("(i-1)/(1+i*sqrt(3))"), stampa=False)
    verifica("Re z=(sqrt3-1)/4, |z|=sqrt2/2", (w["re"], w["mod"]), ((sqrt(3) - 1) / 4, sqrt(2) / 2))
    sol = C.risolvi_equazione("abs(z)^2 = z^3", stampa=False)
    verifica("|z|^2=z^3: 4 soluzioni (0, 1, e^(+-2 pi i/3))", C.complessi_uguali(sol, [0, 1, sp.exp(2 * pi * sp.I / 3), sp.exp(-2 * pi * sp.I / 3)]), True)
    r = estremi_assoluti(sp.atan((x - 1) ** 2 + 1), 0, 2, stampa=False)
    verifica("min di arctan((x-1)^2+1) su [0,2] = pi/4", r["min"][1], pi / 4)
    verifica("lim (log(1+2x)-2 sin x)/x^2 = -2", lim((sp.log(1 + 2 * x) - 2 * sp.sin(x)) / x ** 2, x, 0), -2)
    verifica("v=(1,-2,1) e w=(2,1,0) ortogonali (v.w=0)", G.prodotti("(1,-2,1)", "(2,1,0)", stampa=False)[0], 0)
    sol = I_.edo("y' - 2*y = exp(x)", stampa=False)["soluzione"]
    verifica("y'-2y=e^x: y = C e^(2x) - e^x", sp.simplify(sol.rhs.subs(sp.Symbol("C1"), 3) - (3 * exp(2 * x) - exp(x))), 0)
    verifica("elica (cos 2t, sin 2t, t), t in [0,pi]: lunghezza pi sqrt5", I_.curva("cos(2*t), sin(2*t), t", 0, "pi", stampa=False)["lunghezza"], sqrt(5) * pi)
    verifica("int_0^oo arctan x/(e^(x/a)-1) converge sse a>0", I_.convergenza_parametro("atan(x)/(exp(x/a)-1)", 0, "oo", "a", stampa=False), Interval.open(0, oo))
    St = Studio(sp.Pow(x, Rational(4, 3)) * sp.Pow(2 - x, Rational(1, 3)), x)
    verifica("min in 0, max in 8/5, x=2 flesso a tangente verticale", (_estremo(St, 0)[0], _estremo(St, Rational(8, 5))[0], _tipo_nodo(St, 2)), ("minimo", "massimo", "flesso a tangente verticale"))
    verifica("s: x=1-l, y=l, z=1-l (piani x+y=1, y+z=1)", [sp.simplify(c) for c in G.retta_da_piani("x+y=1", "y+z=1", stampa=False)[0]], [1, -1, 1])
    r = G.posizione_rette("3,1,1", "-2,-1,0", "1,0,1", "-1,1,-1", stampa=False)
    verifica("r e s incidenti in (1,0,1); piano x-2y-3z+2=0", (r["tipo"], r["punto"], G.str_piano(*G.piano_due_rette("3,1,1", "-2,-1,0", "1,0,1", "-1,1,-1", stampa=False))), ("incidenti", [1, 0, 1], "x - 2*y - 3*z = -2"))


@tema("app_9_6_26", "Terzo appello 9/6/2026")
def app_9_6_26():
    titolo("app 9/6/2026", "|z+2conj z|=3, e^(2x^2)-cos 2x, integrali, geometria, x+arctan(e^-x)")
    res = C.risolvi_equazione("abs(z+2*conj(z))=3", stampa=False)
    verifica("|z+2 conj z|=3 e' una curva (infiniti punti) di equazione 9a^2+b^2=9: ellisse",
             (isinstance(res, tuple), C.classifica_conica(9 * C.a_ ** 2 + C.b_ ** 2 - 9)), (True, "ellisse"))
    o = SU.limite_esponente("exp(2*x^2)-cos(2*x)", "x", "0", stampa=False)
    verifica("lim (e^(2x^2)-cos 2x)/x^a finito non nullo sse a=2", o["soglia"], 2)
    verifica("int_{-oo}^{oo} e^(ax)/(e^x+1) converge sse 0<a<1", I_.convergenza_parametro("exp(a*x)/(exp(x)+1)", "-oo", "oo", "a", stampa=False), Interval.open(0, 1))
    verifica("int_0^4 x/sqrt(x^2+9) dx = 2", I_.integrale("x/sqrt(x^2+9)", 0, 4, stampa=False)["valore"], 2)
    verifica("int 3x^2 ds su (2e^t,e^-t,2t), t in [0,ln2] = 68", I_.integrale_di_linea("2*exp(t), exp(-t), 2*t", "3*x^2", 0, "log(2)", stampa=False), 68)
    verifica("vettori (1,a,2),(-1,2,1),(a-4,-3,a+2) ortogonali sse a=-1/2", _valori(G.condizioni("ortogonali", ["(1,a,2)", "(-1,2,1)", "(a-4,-3,a+2)"], stampa=False)), [-Rational(1, 2)])
    verifica("piano per P,Q,R: 2x+y-2z=-5", G.str_piano(*G.piano_retta_punto("1,-3,2", "1,2,2", "1,1,4", stampa=False)), "2*x + y - 2*z = -5")
    verifica("S_a=(2,a,3) nel piano per a=-3", _valori(G.appartenenza("(2,a,3)", "2*x+y-2*z=-5", stampa=False)), [-3])
    verifica("r e s (per S_1 ortogonale al piano) sono sghembe", G.posizione_rette("1,-3,2", "1,2,2", "2,1,3", "2,1,-2", stampa=False)["tipo"], "sghembe")
    verifica("d(S_a, piano) = 2 per a=3 e a=-9", sp.solveset(sp.Eq(sp.Abs(sp.Symbol("a", real=True) + 3) / 3, 2), sp.Symbol("a", real=True), S.Reals), sp.FiniteSet(3, -9))
    St = Studio(x + sp.atan(exp(-x)), x)
    v, o, ob = _asint(St)
    verifica("asintoti obliqui y=x (+oo) e y=x+pi/2 (-oo)", sorted([(nm, m, q) for nm, m, q in ob], key=str), sorted([("+oo", 1, 0), ("-oo", 1, pi / 2)], key=str))
    verifica("strettamente crescente (nessun estremo), un solo zero, flesso in x=0 (f=pi/4)", (St.estremi(), len(St.zeri()), St.flessi()), ([], 1, [(0, pi / 4)]))


@tema("app_13_6_25", "Terzo appello 13/6/2025")
def app_13_6_25():
    titolo("app 13/6/2025", "insieme cos(pi/(x-1)), integrali, ln|x-1|+x^2+x, geometria piano e punto")
    A = SU.estremi_insieme(SU.insieme_reale("cos(pi/(x-1)) = -1"), stampa=False)
    verifica("A={x: cos(pi/(x-1))=-1}: min A = 0 e max A = 2", (A["inf"], A["inf_att"], A["sup"], A["sup_att"]), (0, True, 2, True))
    c = I_.curva("2*t, exp(t), 2*exp(-t)", 0, "log(2)", stampa=False)
    verifica("curva (2t,e^t,2e^-t): regolare, non chiusa, non piana, lunghezza 2", (c["regolare"], c["chiusa"], c["piana"], c["lunghezza"]), (True, False, False, 2))
    verifica("int_0^+oo e^(ax)/(e^x+1) converge sse a<1", I_.convergenza_parametro("exp(a*x)/(exp(x)+1)", 0, "oo", "a", stampa=False), Interval.open(-oo, 1))
    sol = I_.edo("y' = y + x", 0, 0, stampa=False)
    verifica("y'=y+x, y(0)=0: soluzione y=e^x-x-1, minimo locale in 0", (sol["soluzione"].rhs, I_.analisi_locale(sol["equazione"], 0, 0, stampa=False)[1]), (exp(x) - x - 1, "punto stazionario: MINIMO locale"))
    St = Studio(sp.log(sp.Abs(x - 1)) + x ** 2 + x, x)
    verifica("f=ln|x-1|+x^2+x: esattamente 3 zeri", len(St.zeri()), 3)
    verifica("x=0 minimo (f=0), x=1/2 massimo (f=3/4-ln2), asintoto verticale x=1", (_estremo(St, 0)[0:2], _estremo(St, Rational(1, 2))[0:2], sorted({p for p, _, _ in St.asintoti()["verticali"]})), (("minimo", 0), ("massimo", Rational(3, 4) - sp.log(2)), [1]))
    dist, Q = G.distanza_punto_piano("(3,-3,3)", "2*x-2*y+z=6", stampa=False)
    verifica("Q=(1,-1,2), d=3", (list(Q), dist), ([1, -1, 2], 3))
    verifica("piano per P,Q,O: x+y=0; area del triangolo 3 sqrt2/2", (G.str_piano(*G.piano_tre_punti("3,-3,3", "1,-1,2", "0,0,0", stampa=False)), G.area_triangolo("3,-3,3", "1,-1,2", "0,0,0", stampa=False)), ("x + y = 0", 3 * sqrt(2) / 2))


@tema("app_13_1_25", "Primo appello 13/1/2025 [A e B]")
def app_13_1_25():
    titolo("app 13/1/2025", "limite, z^3=2i, raccordo alpha, G(x), (x^2-1)e^-|x-1|, geometria")
    verifica("lim (3x^2+2x)/(1-e^-x) = 2", lim((3 * x ** 2 + 2 * x) / (1 - exp(-x)), x, 0), 2)
    sol = C.risolvi_equazione("z^3 = 2*i", stampa=False)
    verifica("z^3=2i: soluzioni sqrt3+i, -2i, -sqrt3+i (i-sqrt3 non e' soluzione)", C.complessi_uguali(sol, [sqrt(3) + sp.I, -2 * sp.I, -sqrt(3) + sp.I]), True)
    rr = SU.raccordo("1+a*(x^2-1)", "exp(1-x^2)", 1, ["a"], stampa=False)
    verifica("f continua per ogni a, derivabile sse a=-1", (rr["continua"], _valori(rr["derivabile"])), ("sempre (per ogni valore dei parametri)", [-1]))
    verifica("lim (f(x)-cos 2x)/sin(x^2), f ~ 1-x^2: 1", lim((1 - x ** 2 - sp.cos(2 * x)) / sp.sin(x ** 2), x, 0), 1)
    verifica("G(x)=int_{x^2}^x sin(1-t^2) dt: G'=sin(1-x^2)-2x sin(1-x^4)", sp.simplify(I_.funzione_integrale("sin(1-t^2)", "x^2", "x", stampa=False) - (sp.sin(1 - x ** 2) - 2 * x * sp.sin(1 - x ** 4))), 0)
    verifica("int_0^1 sqrt(1-cos x)/(e^x-1-x) dx diverge a +oo", I_.integrale("sqrt(1-cos(x))/(exp(x)-1-x)", 0, 1, stampa=False)["converge"], False)
    sol = I_.edo("y' + x*y = x", stampa=False)["soluzione"]
    verifica("y'+xy=x: y=C e^(-x^2/2)+1", sp.simplify(sol.rhs.subs(sp.Symbol("C1"), 2) - (2 * exp(-x ** 2 / 2) + 1)), 0)
    verifica("int x^2 y ds su semicirconferenza r=2, t in [-pi/2,pi/2] = 0", I_.integrale_di_linea("2*cos(t), 2*sin(t)", "x^2*y", "-pi/2", "pi/2", stampa=False), 0)
    verifica("int x^2 y ds su quarto di circonferenza r=2, t in [0,pi/2] = 16/3", I_.integrale_di_linea("2*cos(t), 2*sin(t)", "x^2*y", 0, "pi/2", stampa=False), Rational(16, 3))
    St = Studio((x ** 2 - 1) * exp(-Abs(x - 1)), x)
    M, m_ = 2 * (1 + sqrt(2)) * exp(-sqrt(2)), 2 * (1 - sqrt(2)) * exp(-2 + sqrt(2))
    verifica("f derivabile in x=1; Im f = [-2(sqrt2-1)e^(-2+sqrt2), 2(1+sqrt2)e^(-sqrt2)]", (_tipo_nodo(St, 1), St.immagine), ("derivabile", Interval(m_, M)))
    St = Studio((x ** 2 - 1) * exp(-Abs(1 + x)), x)
    verifica("[B] f=(x^2-1)e^-|1+x|: derivabile in -1, stessa immagine", (_tipo_nodo(St, -1), St.immagine), ("derivabile", Interval(m_, M)))
    verifica("r per (1,1,0),(2,2,1) e piano per p2=(1,2,1) ortogonale: x+y+z=4", G.str_piano(*G.piano_punto_normale("1,2,1", "1,1,1", stampa=False)), "x + y + z = 4")
    verifica("angolo fra (1,1,0) e (0,1,1): pi/3; area triangolo: 1/sqrt2", (G.angolo_vettori("(1,1,0)", "(0,1,1)", stampa=False), G.area_triangolo("1,1,0", "2,2,1", "1,2,1", stampa=False)), (pi / 3, sqrt(2) / 2))
    dist, _ = G.distanza_punto_piano("(1,1,0)", "x+y+z=4", stampa=False)
    verifica("d(p0, piano) = 2/sqrt3", dist, 2 * sqrt(3) / 3)


@tema("app_3_2_25", "Secondo appello 3/2/2025 [A]")
def app_3_2_25():
    titolo("app 3/2/2025", "limite e^3, |z|^3 z=16i, integrale razionale, 1-sqrt(x/(x+1)), curva non semplice")
    verifica("lim (n+1)^(3n)/(n^(3n)+n^4) = e^3", lim((n + 1) ** (3 * n) / (n ** (3 * n) + n ** 4), n, oo), exp(3))
    sol = C.risolvi_equazione("abs(z)^3*z = 16*i", stampa=False)
    verifica("|z|^3 z=16i: una sola soluzione, z=2i", C.complessi_uguali(sol, [2 * sp.I]), True)
    verifica("min di arctan(x+ln x-1) su [1,5] = 0", estremi_assoluti(sp.atan(x + sp.log(x) - 1), 1, 5, stampa=False)["min"][1], 0)
    verifica("int_3^4 (3x-4)/(x^2-3x+2) dx = ln3 + ln2", sp.simplify(I_.integrale("(3*x-4)/(x^2-3*x+2)", 3, 4, stampa=False)["valore"] - (sp.log(3) + sp.log(2))), 0)
    St = Studio(1 - sp.sqrt(x / (x + 1)), x)
    v, o, _ = _asint(St)
    verifica("D(f)=(-oo,-1) U [0,oo); asintoto verticale x=-1; y=0 orizzontale", (St.dominio, sorted({p for p, _ in v}), sorted({L for _, L in o})), (Union(Interval.open(-oo, -1), Interval(0, oo)), [-1], [0]))
    verifica("x=0 non derivabile (derivata destra -oo), massimo in x=0 (f=1)", (_tipo_nodo(St, 0), _estremo(St, 0)[0:2]),
             ("estremo del dominio con tangente verticale", ("massimo", 1)))
    gam = "t^2-1, t-t^3, sin(pi*t)"
    verifica("curva regolare ma non semplice: gamma(-1)=gamma(1)", I_.curva(gam, -2, 2, stampa=False)["regolare"], True)
    verifica("autointersezione per (t,u) = (-1, 1)", [round(v, 6) for v in I_.autointersezioni(gam, -2, 2, stampa=False)[0]], [-1.0, 1.0])
    verifica("piano per gamma(0) con r' e r'': pi y - z = 0", G.str_piano(*I_.piano_osculatore("t^2-1, t-t^3, sin(pi*t)", 0, stampa=False)), "pi*y - z = 0")


@tema("app_4_7_25", "Quarto appello 4/7/2025")
def app_4_7_25():
    titolo("app 4/7/2025", "limite con log^alpha, integrale di linea, retta-piano, cbrt(x-6)e^(-1/x), curva piana")
    o = SU.limite_esponente("exp(x^2-x)-x^2/2+x-1", "log(1+x^2)", "0", stampa=False)
    verifica("lim (e^(x^2-x)-x^2/2+x-1)/log^a(1+x^2) = 0 sse a<1", o["soglia"], 1)
    verifica("int x/(1+y^2) ds su quarto di circonferenza unitaria = pi/4", I_.integrale_di_linea("cos(t), sin(t)", "x/(1+y^2)", 0, "pi/2", stampa=False), pi / 4)
    r = G.posizione_rette("1,1,2", "1,-1,-2", "0,1,0", "1,2,-1", stampa=False)
    verifica("r: (1+t,1-t,2-2t) e piano x+2y-z=2: v.n=1 != 0 (incidenti, non perpendicolari)", (G.prodotti("1,-1,-2", "1,2,-1", stampa=False)[0], G.angolo_retta_piano("1,-1,-2", "x+2*y-z=2", stampa=False) != pi / 2), (1, True))
    verifica("int_{-oo}^0 e^(ax)/(e^x+1) converge sse a>0", I_.convergenza_parametro("exp(a*x)/(exp(x)+1)", "-oo", 0, "a", stampa=False), Interval.open(0, oo))
    St = Studio(sp.Pow(x - 6, Rational(1, 3)) * exp(-1 / x), x)
    verifica("f=cbrt(x-6)e^(-1/x): dominio R\\{0}, zero in 6, asintoto verticale x=0 (da sinistra)", (St.dominio, [z for z, _ in St.zeri()], sorted({(p, l) for p, l, _ in St.asintoti()["verticali"]})), (Union(Interval.open(-oo, 0), Interval.open(0, oo)), [6], [(0, "-")]))
    verifica("x=6 flesso a tangente verticale; max loc in -6, min loc in 3", (_tipo_nodo(St, 6), _estremo(St, -6)[0], _estremo(St, 3)[0]), ("flesso a tangente verticale", "massimo", "minimo"))
    c = I_.curva("2*sin(t)^2, t, 2*cos(t)^2-t", 0, "2*pi", stampa=False)
    verifica("curva (2sin^2 t, t, 2cos^2 t - t): regolare, non chiusa, piana (x+y+z=2)", (c["regolare"], c["chiusa"], c["piana"], I_.autointersezioni("2*sin(t)^2, t, 2*cos(t)^2-t", 0, "2*pi", stampa=False)), (True, False, True, []))
    P, d = I_.retta_tangente_curva("2*sin(t)^2, t, 2*cos(t)^2-t", 0, stampa=False)
    verifica("tangente in P=(0,0,2) parallela a (0,1,-1)", (list(P), list(d)), ([0, 0, 2], [0, 1, -1]))
    verifica("(a_n=(-1)^n (n-1)/n) limitata, |a_n| crescente, sup/inf non assunti",
             (lambda r_: (r_["sup"], r_["sup_att"], r_["inf"], r_["inf_att"]))(SU.successione("(-1)^n*(n-1)/n", 1, stampa=False)), (1, False, -1, False))
    sol = C.risolvi_equazione("(abs(z)^2+abs(z)+2)*(z*conj(z)-1) = 0", stampa=False)
    verifica("(|z|^2+|z|+2)(z conj z-1)=0: infinite soluzioni (|z|=1)", isinstance(sol, tuple), True)


@tema("app_5_7_24", "Quarto appello 5/7/2024 [A]")
def app_5_7_24():
    titolo("app 5/7/2024", "cbrt(x^3-x^2), limite log, distanza punto-piano, rette r,s e fascio di piani")
    St = Studio(sp.Pow(x ** 3 - x ** 2, Rational(1, 3)), x)
    verifica("zeri 0 e 1; asintoto obliquo y=x-1/3 (+-oo)", ([z for z, _ in St.zeri()], sorted({(m, q) for _, m, q in St.asintoti()["obliqui"]})), ([0, 1], [(1, -Rational(1, 3))]))
    verifica("x=0 cuspide; x=1 flesso a tangente verticale; minimo locale in 2/3", (_tipo_nodo(St, 0), _tipo_nodo(St, 1), _estremo(St, Rational(2, 3))[0]), ("cuspide", "flesso a tangente verticale", "minimo"))
    verifica("lim x log((1+x^2)/(2x+x^2)) = -2 (x->+oo)", lim(x * sp.log((1 + x ** 2) / (2 * x + x ** 2)), x, oo), -2)
    verifica("d(P=(4,1,-5), x-2y-3=0) = sqrt5/5", G.distanza_punto_piano("(4,1,-5)", "x-2*y-3=0", stampa=False)[0], sqrt(5) / 5)
    verifica("r (A,B) e s (piani) sghembe; distanza 4/sqrt5", (lambda r_: (r_["tipo"], r_["distanza"]))(G.posizione_rette("1,0,2", "2,4,-1", "1,0,0", "2,1,-1", stampa=False)), ("sghembe", 4 * sqrt(5) / 5))
    verifica("piano x-2y-1+l(y+z)=0 parallelo a r: l=2, cioe' x+2z-1=0", _valori(G.vettore_parallelo_piano("(2,4,-1)", "x-2*y-1+l*(y+z)=0", stampa=False)), [2])


@tema("app_9_2_24", "Primo appello 9/2/2024")
def app_9_2_24():
    titolo("app 9/2/2024", "e^(i pi/6)e^(2 pi i/3), Taylor, integrale con alpha, proiezione, arctan(1/x^2)+log(1+x^2), curva piana")
    w = C.analizza(exp(sp.I * pi / 6) * exp(2 * pi * sp.I / 3), stampa=False)
    verifica("z=e^(i 5pi/6)=(-sqrt3+i)/2", w["alg"], (-sqrt(3) + sp.I) / 2)
    verifica("lim (log(1+x)-x)/(e^(2x)-1-2x) = -1/4", lim((sp.log(1 + x) - x) / (exp(2 * x) - 1 - 2 * x), x, 0), -Rational(1, 4))
    T2 = sp.series(x * sp.cos(pi * x), x, 1, 3).removeO()
    verifica("Taylor di x cos(pi x) in x0=1 ordine 2: -1-(x-1)+pi^2/2 (x-1)^2", sp.expand(T2 - (-1 - (x - 1) + pi ** 2 / 2 * (x - 1) ** 2)), 0)
    verifica("int_0^oo (1-e^(-x^2))/x^a converge sse 1<a<3", I_.convergenza_parametro("(1-exp(-x^2))/x^a", 0, "oo", "a", stampa=False), Interval.open(1, 3))
    verifica("proiezione di P=(2,-3,1) su r:(1+t,2-t,1-2t) e' (2,1,-1)", list(G.distanza_punto_retta("(2,-3,1)", "1,2,1", "1,-1,-2", stampa=False)[1]), [2, 1, -1])
    verifica("angolo fra (1,0,1) e (2,2,1): pi/4", G.angolo_vettori("(1,0,1)", "(2,2,1)", stampa=False), pi / 4)
    St = Studio(sp.atan(1 / x ** 2) + sp.log(1 + x ** 2), x)
    verifica("f pari, limite in 0 = pi/2, minimi globali in +-1 con f=pi/4+log2", (_estremo(St, 1)[0::2], _estremo(St, -1)[0::2], St.info[0]["sx"]), (("minimo", True), ("minimo", True), pi / 2))
    c = I_.curva("2*t+t^2, 2*t-t^2, 1-2*t", 0, 1, stampa=False)
    verifica("curva (2t+t^2,2t-t^2,1-2t): piana (x+y+2z=2), regolare; int (1-z) ds = 10 sqrt5/3 - 2 sqrt3",
             (c["piana"], c["regolare"], sp.simplify(I_.integrale_di_linea("2*t+t^2, 2*t-t^2, 1-2*t", "1-z", 0, 1, stampa=False) - (10 * sqrt(5) / 3 - 2 * sqrt(3)))), (True, True, 0))


@tema("app_14_6_24", "Appello 14/6/2024 [A]")
def app_14_6_24():
    titolo("app 14/6/2024", "f a tratti cos(pi e^x) / (2x-1)e^(-x^2)")
    f = sp.Piecewise((sp.cos(pi * exp(x)), x < 0), ((2 * x - 1) * exp(-x ** 2), True))
    St = Studio(f, x)
    verifica("f continua in 0 (f(0)=-1) con punto angoloso, f'-=0, f'+=2", (_tipo_nodo(St, 0), [d["dsx"] for d in St.info], [d["ddx"] for d in St.info]), ("punto angoloso", [0], [2]))
    v, o, _ = _asint(St)
    verifica("asintoti orizzontali y=1 (-oo) e y=0 (+oo)", sorted(o, key=str), sorted([("-oo", 1), ("+oo", 0)], key=str))
    verifica("minimo globale in 0 (-1), massimo locale in 1; Im f = [-1,1)", (_estremo(St, 0)[0::2], _estremo(St, 1)[0], St.immagine), (("minimo", True), "massimo", Interval.Ropen(-1, 1)))


@tema("app_16_6_23", "Appello 16/6/2023, 30/1/2023, gennaio 2022")
def app_altri_2022_23():
    titolo("app 2022-23", "cbrt((x+1)^5/x^2), e^(1/x)-1-x, cbrt((x+2)/(x^2+1))")
    St = Studio(sp.Pow((x + 1) ** 5 / x ** 2, Rational(1, 3)), x)
    verifica("asintoto verticale x=0, obliquo y=x+5/3, minimo locale in 2/3", (sorted({p for p, _, _ in St.asintoti()["verticali"]}), sorted({(m, q) for _, m, q in St.asintoti()["obliqui"]}), _estremo(St, Rational(2, 3))[0]), ([0], [(1, Rational(5, 3))], "minimo"))
    St = Studio(exp(1 / x) - 1 - x, x)
    verifica("e^(1/x)-1-x: asintoto y=-x (+-oo), x=0 verticale da destra, esattamente 2 zeri", (sorted({(m, q) for _, m, q in St.asintoti()["obliqui"]}), [(p, l) for p, l, _ in St.asintoti()["verticali"]], len(St.zeri())), ([(-1, 0)], [(0, "+")], 2))
    St = Studio(sp.Pow((x + 2) / (x ** 2 + 1), Rational(1, 3)), x)
    verifica("x=-2-sqrt5 minimo globale, x=-2+sqrt5 massimo globale, x=-2 non derivabile; y=0 asintoto", (_estremo(St, -2 - sqrt(5))[0::2], _estremo(St, -2 + sqrt(5))[0::2], _tipo_nodo(St, -2)), (("minimo", True), ("massimo", True), "flesso a tangente verticale"))


@tema("app_gen_2022", "Appelli 2022: 31/1, 7/7 e 7/9")
def app_2022():
    titolo("app 2022", "|z|=z+1, e^((i+2)^2), sin x/(1-cos x)^a, int arctan, Taylor, curva, rette, x/(1+x^2)-arctan x")
    sol = C.risolvi_equazione("abs(z) = z + 1", stampa=False)
    verifica("|z|=z+1: soluzione reale z=-1/2", C.complessi_uguali(sol, [-Rational(1, 2)]), True)
    w = C.analizza(exp((sp.I + 2) ** 2), stampa=False)
    verifica("e^((i+2)^2): |z|=e^3, arg = 4 - 2 pi (non 0, non pi/2)", (w["mod"], sp.N(w["arg_principale"], 6)), (exp(3), sp.N(4 - 2 * pi, 6)))
    verifica("sin x/(1-cos x)^a vale 0 sse a<1/2", SU.limite_esponente("sin(x)", "1-cos(x)", "0", stampa=False)["soglia"], Rational(1, 2))
    verifica("int_0^1 arctan x dx = (pi - log 4)/4", sp.simplify(I_.integrale("atan(x)", 0, 1, stampa=False)["valore"] - (pi - sp.log(4)) / 4), 0)
    T6 = sp.series(exp(1 - exp(2 * x ** 3)), x, 0, 7).removeO()
    verifica("P_6 di e^(1-e^(2x^3)) = 1-2x^3; x0=0 e' critico ma non estremo", sp.expand(T6 - (1 - 2 * x ** 3)), 0)
    verifica("curva (cos log t, sqrt2/2 sin log t, sqrt2/2 sin log t), t in [1,e^(2pi)]: lunghezza 2 pi", sp.simplify(I_.curva("cos(log(t)), sqrt(2)/2*sin(log(t)), sqrt(2)/2*sin(log(t))", 1, "exp(2*pi)", stampa=False)["lunghezza"]), 2 * pi)
    verifica("r (1+t,2+2t,3+3t) e r^ (1+t,2,3+3t): incidenti", G.posizione_rette("1,2,3", "1,2,3", "1,2,3", "1,0,3", stampa=False)["tipo"], "incidenti")
    St = Studio(x / (1 + x ** 2) - sp.atan(x), x)
    verifica("f dispari, asintoti y=+-pi/2, strettamente decrescente, nessun estremo (flesso orizzontale in 0)", (sorted({L for _, L in St.asintoti()["orizzontali"]}, key=float), [e[1] for e in St.estremi()]), ([-pi / 2, pi / 2], [0]))
    verifica("int_e^(e^2) (log x)^2 dx = 2e^2 - e", sp.simplify(I_.integrale("log(x)^2", "E", "exp(2)", stampa=False)["valore"] - (2 * sp.E ** 2 - sp.E)), 0)
    w = C.analizza(C.parse_c("(1+i)^3/(1-sqrt(3)*i)^4"), stampa=False)
    verifica("z=(1+i)^3/(1-sqrt3 i)^4: arg = pi/12, |z|<1", (w["arg_principale"], w["mod"] < 1), (pi / 12, True))


from sympy import Abs  # noqa: E402  (usata nei test sopra)
