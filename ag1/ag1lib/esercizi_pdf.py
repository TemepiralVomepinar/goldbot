"""I 40 esercizi del PDF "Esercizi AG1 - prima prova in itinere", risolti con i moduli del pacchetto
e confrontati con le soluzioni riportate nel PDF."""
import os
import random

import sympy as sp
from sympy import (Abs, I, Interval, Rational, S, Symbol, Union, arg, atan, cos, diff, exp, factorial, limit, log,
                   oo, pi, sin, sqrt, tan)
from sympy.calculus.util import continuous_domain

from .complessi import forma_esp, radici_n, risolvi_equazione
from .funzioni import Studio, asintoti, classifica_critico, classifica_discontinuita, studio_funzione
from .successioni import estremi_successione, riassumi_estremi
from .util import (OUT_DIR, k, lim, n, num, riga, registra, t, titolo, uguali, verifica, verifica_complessi, x, xp)
from .util import s as semplifica


# ================================================================ ESERCIZI ====
def es1():
    titolo(1, "A = { n/(2n+1) : n>=1 }  -> sup, inf, max, min")
    a = n / (2 * n + 1)
    riga("n/(2n+1) = 1/2 - 1/(2(2n+1)): intuitivamente crescente e -> 1/2")
    sup, sa, inf, ia = estremi_successione([(a, n, 1)])
    riassumi_estremi(sup, sa, inf, ia)
    riga("Giustificazione: n/(2n+1) < 1/2 <=> 2n < 2n+1 (vera); per eps>0, a_n > 1/2-eps <=> n > 1/(4eps)-1/2.")
    verifica("sup A = 1/2, non e' massimo", (sup, sa), (Rational(1, 2), False))
    verifica("inf A = min A = a_1 = 1/3", (inf, ia), (Rational(1, 3), True))


def es2():
    titolo(2, "A = { (-1)^n + 1/n : n>=1 }")
    parti = [(1 + 1 / (2 * k), k, 1), (-1 + 1 / (2 * k + 1), k, 0)]
    riga("n pari (n=2k): 1+1/(2k);  n dispari (n=2k+1): -1+1/(2k+1)")
    sup, sa, inf, ia = estremi_successione(parti)
    riassumi_estremi(sup, sa, inf, ia)
    verifica("sup A = max A = 3/2", (sup, sa), (Rational(3, 2), True))
    verifica("inf A = -1, non e' minimo", (inf, ia), (-1, False))


def es3():
    titolo(3, "B = { 1/n + 1/m : n,m >= 1 }")
    riga("1/n + 1/m e' decrescente in ciascuna variabile: massimo per n=m=1")
    mx = (1 / n + 1 / n).subs(n, 1)
    inf = lim(1 / n + 1 / n, n, oo)
    riga(f"max B = {mx}  (n=m=1);  inf B = lim(1/n+1/n) = {inf}, e 1/n+1/m > 0 quindi non e' minimo")
    verifica("sup B = max B = 2", mx, 2)
    verifica("inf B = 0 (non minimo)", inf, 0)


def es4():
    titolo(4, "Induzione: (a) somma dei quadrati, (b) 2^n >= n^2, (c) n^3 - n divisibile per 3")
    F = lambda m: m * (m + 1) * (2 * m + 1) / sp.Integer(6)
    riga("(a) base n=1:", sp.Sum(k ** 2, (k, 1, 1)).doit(), "=", F(1))
    passo_a = sp.simplify(F(n) + (n + 1) ** 2 - F(n + 1))
    riga("    passo: F(n) + (n+1)^2 - F(n+1) =", passo_a)
    ok_a = passo_a == 0 and sp.simplify(sp.summation(k ** 2, (k, 1, n)) - F(n)) == 0
    riga("(b) base n=4: 2^4 =", 2 ** 4, ">= 4^2 =", 16)
    riga("    passo: 2^(n+1) = 2*2^n >= 2n^2 >= (n+1)^2  <=>  n^2-2n-1>=0  <=> n >=",
         sp.N(1 + sqrt(2), 4), "-> vero per ogni n>=3")
    ok_b = all(2 ** m >= m ** 2 for m in range(4, 400)) and sp.solve(n ** 2 - 2 * n - 1 >= 0, n) is not None
    passo_c = sp.expand((n + 1) ** 3 - (n + 1) - (n ** 3 - n))
    riga("(c) base n=0: 0 divisibile per 3.  (n+1)^3-(n+1) - (n^3-n) =", passo_c, "=", sp.factor(passo_c),
         ": multiplo di 3")
    ok_c = sp.simplify(passo_c - 3 * n * (n + 1)) == 0 and all((m ** 3 - m) % 3 == 0 for m in range(0, 400))
    verifica("(a)(b)(c) verificate (passo induttivo + controllo numerico)", ok_a and ok_b and ok_c, True)


def es5():
    titolo(5, "A = {x^2-2x-3<0} ∩ {|x|>=1}")
    A = sp.solveset(x ** 2 - 2 * x - 3 < 0, x, S.Reals).intersect(sp.solveset(Abs(x) >= 1, x, S.Reals))
    riga("A =", A)
    riga(f"inf A = {A.inf} ({'minimo' if A.contains(A.inf) else 'non minimo'}), "
         f"sup A = {A.sup} ({'massimo' if A.contains(A.sup) else 'non massimo'})")
    verifica("A = [1,3)", A, Interval.Ropen(1, 3))


def es6():
    titolo(6, "(1+i)^10 e (3-i)/(1+2i) in forma algebrica")
    a = sp.expand_complex((1 + I) ** 10)
    b = sp.expand_complex(sp.simplify((3 - I) / (1 + 2 * I)))
    riga("1+i = sqrt2 e^(i pi/4)  =>  (1+i)^10 = 32 e^(i pi/2) =", a)
    riga("(3-i)/(1+2i) = (3-i)(1-2i)/5 =", b)
    verifica("(1+i)^10 = 32i", a, 32 * I)
    verifica("(3-i)/(1+2i) = (1-7i)/5", b, (1 - 7 * I) / 5)


def es7():
    titolo(7, "(a) z^3 = -8i;  (b) z^2 = 2i conj(z)   (forma esponenziale)")
    ra = radici_n(-8 * I, 3)
    riga("(a) -8i = 8 e^(-i pi/2):")
    for z, r, th in ra:
        riga(f"    z = {r} e^(i*({th})) = {sp.expand_complex(z)}")
    verifica_complessi("(a) radici = sqrt3-i, 2i, -sqrt3-i", [z for z, _, _ in ra],
                       [sqrt(3) - I, 2 * I, -sqrt(3) - I])
    riga("(b) z=a+ib: parte reale a^2-b^2-2b=0, parte immaginaria 2a(b-1)=0")
    sol = risolvi_equazione("z^2 = 2*i*conj(z)")
    verifica_complessi("(b) soluzioni = 0, -2i, sqrt3+i, -sqrt3+i", sol, [0, -2 * I, sqrt(3) + I, -sqrt(3) + I])


def es8():
    titolo(8, "z^8 = (2+i)^4  -> quante soluzioni?")
    phi = atan(Rational(1, 2))
    riga("2+i = sqrt5 e^(i phi), phi = arctg(1/2);  (2+i)^4 = 25 e^(4 i phi)")
    ra = radici_n(None, 8, r=25, phi=4 * phi)
    for z, r, th in ra:
        riga(f"    z = {r} e^(i*({th}))   ~ {sp.N(z, 6)}")
    w = (2 + I) ** 4
    ok = all(abs(num(z ** 8 - w)) < 1e-8 for z, _, _ in ra)
    riga(f"    in tutto {len(ra)} soluzioni, vertici di un ottagono regolare")
    verifica("8 soluzioni, tutte verificano z^8=(2+i)^4", (len(ra), ok), (8, True))


def es9():
    titolo(9, "Regioni nel piano di Gauss e z^2 = conj(z)")
    riga("(a) |z+1|<|z-1| : punti piu' vicini a -1 che a 1  ->  semipiano Re z < 0")
    riga("(b) Re(z^2)>0 <=> x^2>y^2 <=> |y|<|x|: due settori aperti |arg z|<pi/4 e |arg z - pi|<pi/4")
    riga("(c) corona circolare 1<=|z|<=2 limitata dall'angolo 0<=Arg z<=pi/3 (settore)")
    riga("(d) z^2 = conj(z):")
    sol = risolvi_equazione("z^2 = conj(z)")
    verifica_complessi("(d) soluzioni = 0, 1, -1/2 +- i sqrt3/2", sol,
                       [0, 1, -Rational(1, 2) + sqrt(3) / 2 * I, -Rational(1, 2) - sqrt(3) / 2 * I])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    os.makedirs(OUT_DIR, exist_ok=True)
    X, Y = np.meshgrid(np.linspace(-3, 3, 800), np.linspace(-3, 3, 800))
    R, TH = np.hypot(X, Y), np.arctan2(Y, X)
    regioni = [
        ("(a) |z+1| < |z-1|", np.hypot(X + 1, Y) < np.hypot(X - 1, Y)),
        ("(b) Re(z^2) > 0", X ** 2 - Y ** 2 > 0),
        ("(c) 1<=|z|<=2, 0<=Arg z<=pi/3", (R >= 1) & (R <= 2) & (TH >= 0) & (TH <= np.pi / 3)),
    ]
    fig, axs = plt.subplots(1, 4, figsize=(16, 4))
    for ax, (nome, m) in zip(axs[:3], regioni):
        ax.imshow(m, extent=(-3, 3, -3, 3), origin="lower", cmap="Blues", alpha=0.8)
        ax.set_title(nome, fontsize=10)
    pts = [complex(num(z)) for z in sol]
    axs[3].scatter([p.real for p in pts], [p.imag for p in pts], color="crimson")
    axs[3].set_xlim(-3, 3), axs[3].set_ylim(-3, 3), axs[3].set_title("(d) z^2 = conj(z)", fontsize=10)
    for ax in axs:
        ax.axhline(0, color="k", lw=0.6), ax.axvline(0, color="k", lw=0.6), ax.set_aspect("equal")
    path = os.path.join(OUT_DIR, "es09_piano_di_gauss.png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    riga("disegni salvati in:", path)


def es10():
    titolo(10, "z^2 - (3+i) z + (2+2i) = 0")
    z = Symbol("z")
    disc = sp.expand_complex((3 + I) ** 2 - 4 * (2 + 2 * I))
    sol = sp.solve(z ** 2 - (3 + I) * z + 2 + 2 * I, z)
    riga("Delta =", disc, "= (1-i)^2")
    riga("soluzioni:", sol)
    verifica_complessi("z = 2, 1+i", sol, [2, 1 + I])


def es11():
    titolo(11, "Dominio di f(x) = ln((x-1)/(x+2)) + sqrt(4-x^2)")
    c1 = sp.solveset((x - 1) / (x + 2) > 0, x, S.Reals)
    c2 = sp.solveset(4 - x ** 2 >= 0, x, S.Reals)
    dom = c1.intersect(c2)
    riga("(x-1)/(x+2) > 0:", c1)
    riga("4 - x^2 >= 0:", c2)
    riga("dominio =", dom)
    verifica("dominio = (1,2]", dom, Interval.Lopen(1, 2))


def es12():
    titolo(12, "f(x) = (e^x-1)/(e^x+1): invertibile, f^-1, Im f")
    f = (exp(x) - 1) / (exp(x) + 1)
    df = sp.simplify(diff(f, x))
    riga("f'(x) =", df, "> 0  =>  strettamente crescente  =>  iniettiva")
    y = Symbol("y", real=True)
    inv = sp.solve(sp.Eq(f, y), x)[0]
    inv = sp.simplify(inv)
    riga("f^-1(y) =", inv)
    lo, hi = lim(f, x, -oo), lim(f, x, oo)
    riga(f"lim x->-oo f = {lo}, lim x->+oo f = {hi}  =>  Im f = ({lo}, {hi})")
    verifica("f^-1(y) = ln((1+y)/(1-y)) (test in y=0.3)", inv.subs(y, Rational(3, 10)),
             log(Rational(13, 10) / Rational(7, 10)))
    verifica("Im f = (-1,1)", Interval.open(lo, hi), Interval.open(-1, 1))


def es13():
    titolo(13, "Limiti di successioni")
    a = lim((n ** 2 - 3 * n + 1) / (2 * n ** 2 + 5), n, oo)
    b = lim(sqrt(n ** 2 + n) - n, n, oo)
    c = lim((1 + Rational(2) / n) ** (3 * n), n, oo)
    riga("(a) termini dominanti:", a, "  (b) razionalizzando n/(sqrt(n^2+n)+n):", b, "  (c) (1+2/n)^(3n) = [..]^6:", c)
    verifica("(a) 1/2", a, Rational(1, 2))
    verifica("(b) 1/2", b, Rational(1, 2))
    verifica("(c) e^6", c, exp(6))


def es14():
    titolo(14, "Limiti con asintotici / Taylor")
    a = lim(n ** 2 * (exp(1 / n) - 1 - 1 / n), n, oo)
    b = lim(((n ** 2 + 1) / (n ** 2 - 2)) ** (n ** 2), n, oo)
    c = lim(n ** 2 * log(cos(1 / n)), n, oo)
    d = lim(n * (2 ** (1 / n) - 1), n, oo)
    riga("(a) e^(1/n)-1-1/n ~ 1/(2n^2):", a)
    riga("(b) forma 1^oo: exp(n^2 ln(1+3/(n^2-2))), n^2 * 3/(n^2-2) -> 3:", b)
    riga("(c) ln cos(1/n) ~ cos(1/n)-1 ~ -1/(2n^2):", c)
    riga("(d) 2^(1/n)-1 ~ ln2/n:", d)
    verifica("(a) 1/2", a, Rational(1, 2))
    verifica("(b) e^3", b, exp(3))
    verifica("(c) -1/2", c, -Rational(1, 2))
    verifica("(d) ln 2", d, log(2))


def es15():
    titolo(15, "Criteri del rapporto / radice / gerarchia degli infiniti")
    A = factorial(n) ** 2 / factorial(2 * n)
    r = sp.simplify(sp.combsimp(A.subs(n, n + 1) / A))
    la = lim(r, n, oo)
    riga(f"(a) a_(n+1)/a_n = {r} -> {la} < 1  =>  a_n -> 0")
    B = factorial(n + 1) / n ** n
    r2 = sp.simplify(sp.combsimp(B.subs(n, n + 1) / B))
    lb = lim(r2, n, oo)
    riga(f"(b) a_(n+1)/a_n = {r2} -> {lb} < 1  =>  a_n -> 0")
    lc = lim((3 ** n + n ** 5) ** (1 / n), n, oo)
    riga("(c) radice n-esima: 3*(1+n^5/3^n)^(1/n) ->", lc)
    ld = lim(n ** 10 / Rational(101, 100) ** n, n, oo)
    riga("(d) n^10 << 1.01^n (gerarchia degli infiniti) ->", ld)
    verifica("(a) rapporto -> 1/4, limite 0", (la, lim(A, n, oo)), (Rational(1, 4), 0))
    verifica("(b) rapporto -> 1/e, limite 0", (lb, lim(B, n, oo)), (exp(-1), 0))
    verifica("(c) 3", lc, 3)
    verifica("(d) 0", ld, 0)


def es16():
    titolo(16, "Limite (esistenza) di a_n, b_n, c_n")
    an = n * cos(n * pi) / (3 * n + 2)
    pari, dispari = lim(an.subs(n, 2 * k + 2), k, oo), lim(an.subs(n, 2 * k + 1), k, oo)
    riga(f"(a) pari -> {pari}, dispari -> {dispari}: i limiti sono diversi, NON ESISTE il limite")
    bn = n * cos(n * pi) / (3 * n ** 2 + 2)
    lb = lim(n / (3 * n ** 2 + 2), n, oo)
    riga(f"(b) |b_n| <= n/(3n^2+2) -> {lb}: per i carabinieri b_n -> {lb}")
    cn = (n ** 2 + sin(n)) / (n + 1)
    lc = lim((n ** 2 - 1) / (n + 1), n, oo)
    riga(f"(c) c_n >= (n^2-1)/(n+1) = n-1 -> {lc}: per confronto c_n -> +oo")
    verifica("(a) sottosuccessioni 1/3 e -1/3 (limite non esiste)", (pari, dispari), (Rational(1, 3), -Rational(1, 3)))
    verifica("(b) 0", lb, 0)
    verifica("(c) +oo", lc, oo)
    riga("controllo numerico b_n (n=10^5):", sp.N(bn.subs(n, 10 ** 5), 6), " c_n (n=10^6):", sp.N(cn.subs(n, 10 ** 6), 8))


def es17():
    titolo(17, "a_1 = sqrt2, a_(n+1) = sqrt(2+a_n): convergenza e limite")
    a = Symbol("a", positive=True)
    riga("Limitata: a_n < 2 per induzione (a_1<2; se a_n<2 allora a_(n+1)<sqrt4=2).")
    riga("Crescente: a_(n+1) > a_n <=> 2+a_n > a_n^2 <=> (a_n-2)(a_n+1) < 0, vero perche' 0<a_n<2.")
    L = Symbol("L")
    punti = sp.solve(sp.Eq(L, sqrt(2 + L)), L)
    riga("Monotona e limitata => converge a L con L = sqrt(2+L): L^2-L-2=0, soluzioni accettabili:", punti)
    val = sp.sqrt(2)
    for _ in range(40):
        val = sqrt(2 + val)
    riga("controllo numerico (40 iterazioni):", sp.N(val, 15))
    verifica("limite = 2", punti[0], 2)


def es18():
    titolo(18, "Limiti di funzioni (x->0)")
    a = lim((exp(2 * x) - 1 - 2 * x) / (x * sin(x)), x, 0)
    b = lim(log(1 + x ** 2) / (1 - cos(x)), x, 0)
    c = lim((tan(x) - x) / x ** 3, x, 0)
    riga("(a) num = 2x^2+o(x^2), den ~ x^2:", a)
    riga("(b) x^2 / (x^2/2):", b)
    riga("(c) tg x = x + x^3/3 + o(x^3):", c)
    verifica("(a) 2", a, 2)
    verifica("(b) 2", b, 2)
    verifica("(c) 1/3", c, Rational(1, 3))


def es19():
    titolo(19, "Limiti con Taylor / forme 1^oo")
    a = lim((cos(x) - exp(-x ** 2 / 2)) / x ** 4, x, 0)
    b = lim((1 + sin(x)) ** (1 / x), x, 0)
    c = lim(cos(x) ** (1 / x ** 2), x, 0)
    riga("(a) cos x = 1-x^2/2+x^4/24, e^(-x^2/2) = 1-x^2/2+x^4/8  ->", a)
    riga("(b) exp(ln(1+sin x)/x), ln(1+sin x) ~ x  ->", b)
    riga("(c) exp(ln cos x / x^2), ln cos x ~ -x^2/2  ->", c)
    verifica("(a) -1/12", a, -Rational(1, 12))
    verifica("(b) e", b, exp(1))
    verifica("(c) e^(-1/2)", c, exp(-Rational(1, 2)))


def es20():
    titolo(20, "Limiti a +oo / 0+")
    a = lim(sqrt(x ** 2 + 3 * x) - x, x, oo)
    b = lim((x ** 2 + exp(x)) / (x ** 3 + 3 ** x), x, oo)
    c = lim(x ** x, x, 0, "+")
    d = lim(log(x) ** 3 / sqrt(x), x, oo)
    riga("(a) razionalizzando 3x/(sqrt(x^2+3x)+x):", a)
    riga("(b) ~ (e/3)^x:", b)
    riga("(c) e^(x ln x):", c)
    riga("(d) gerarchia degli infiniti:", d)
    verifica("(a) 3/2", a, Rational(3, 2))
    verifica("(b) 0", b, 0)
    verifica("(c) 1", c, 1)
    verifica("(d) 0", d, 0)


def es21():
    titolo(21, "Asintoti di f(x) = x e^(1/x)")
    r = asintoti(x * exp(1 / x), x)
    verifica("verticale x=0 (da destra)", [(p, l) for p, l, _ in r["verticali"]], [(0, "+")])
    verifica("obliquo y = x+1 (a +oo e -oo)", [(m, q) for _, m, q in r["obliqui"]], [(1, 1), (1, 1)])


def es22():
    titolo(22, "Asintoti di f(x) = sqrt(x^2+2x) - x")
    r = asintoti(sqrt(x ** 2 + 2 * x) - x, x)
    ob = {nm: (m, q) for nm, m, q in r["obliqui"]}
    verifica("orizzontale y=1 a +oo", r["orizzontali"], [("+oo", 1)])
    verifica("obliquo y = -2x - 1 a -oo", ob.get("-oo"), (-2, -1))


def es23():
    titolo(23, "Continuita' in 0: trovare a, b")
    a, b = sp.symbols("a b", real=True)
    sx = lim((1 - cos(a * x)) / x ** 2, x, 0, "-")
    dx = lim(log(1 + b * x) / x, x, 0, "+")
    riga(f"limite sinistro = {sx},  limite destro = {dx},  f(0) = 2")
    sol = sp.solve([sp.Eq(sx, 2), sp.Eq(dx, 2)], [a, b], dict=True)
    riga("soluzioni (a,b):", [(s[a], s[b]) for s in sol])
    verifica("a = +-2, b = 2", sorted([(s[a], s[b]) for s in sol]), [(-2, 2), (2, 2)])


def es24():
    titolo(24, "Discontinuita' di f(x) = (x^2-1)/(|x-1|(x+2))")
    f = (x ** 2 - 1) / (Abs(x - 1) * (x + 2))
    dom = continuous_domain(f, x, S.Reals)
    riga("dominio:", dom)
    res = {}
    for p in (1, -2):
        sx, dx, tipo = classifica_discontinuita(f, p)
        riga(f"x = {p}: limite sinistro {sx}, limite destro {dx} -> discontinuita' {tipo}")
        res[p] = tipo
    verifica("x=1 salto (prima specie), x=-2 seconda specie",
             ("prima specie" in res[1], "seconda specie" in res[-2]), (True, True))


def es25():
    titolo(25, "(a) e^x + x = 3 ha una sola soluzione; (b) Im di x e^(-x^2)")
    g = exp(x) + x - 3
    riga(f"(a) g(0) = {g.subs(x, 0)} < 0, g(2) = {g.subs(x, 2)} ~ {sp.N(g.subs(x, 2), 4)} > 0: "
         "per gli zeri esiste una soluzione in (0,2); g' = e^x+1 > 0: strettamente crescente => unica")
    radice = sp.nsolve(g, x, 1)
    riga("    soluzione numerica x =", radice, " (esatta: 3 - W(e^3))")
    f = x * exp(-x ** 2)
    St = Studio(f, x)
    im, crit = St.immagine, [c for T in St.tratti for c in T.crit]
    riga("(b) f dispari, f -> 0 a +-oo; punti critici:", crit)
    riga("    Im f =", im)
    verifica("(a) esattamente una radice (numericamente)", abs(num(g.subs(x, radice))) < 1e-12, True)
    M = 1 / sqrt(2 * sp.E)
    verifica("(b) Im f = [-1/sqrt(2e), 1/sqrt(2e)]", im, Interval(-M, M))


def es26():
    titolo(26, "Derivate")
    d_a = sp.simplify(diff(log(x + sqrt(x ** 2 + 1)), x))
    d_b = sp.simplify(diff(xp ** xp, xp))
    d_c = sp.simplify(diff(sp.atan(sqrt(xp)), xp))
    d_d = sp.simplify(diff(exp(sin(x)) / (1 + x ** 2), x))
    riga("(a)", d_a)
    riga("(b)", d_b, "= x^x (ln x + 1)")
    riga("(c)", d_c)
    riga("(d)", d_d)
    verifica("(a) 1/sqrt(x^2+1)", sp.simplify(d_a - 1 / sqrt(x ** 2 + 1)), 0)
    verifica("(b) x^x (ln x+1)", sp.simplify(d_b - xp ** xp * (log(xp) + 1)), 0)
    verifica("(c) 1/((1+x) 2 sqrt x)", sp.simplify(d_c - 1 / ((1 + xp) * 2 * sqrt(xp))), 0)
    att = (exp(sin(x)) * cos(x) * (1 + x ** 2) - 2 * x * exp(sin(x))) / (1 + x ** 2) ** 2
    verifica("(d) (e^sin x cos x (1+x^2) - 2x e^sin x)/(1+x^2)^2", sp.simplify(d_d - att), 0)


def es27():
    titolo(27, "Derivabilita' con parametri / x^2 sin(1/x)")
    a, b = sp.symbols("a b", real=True)
    cont = sp.Eq(a + b, 2 + log(1))
    der = sp.Eq(diff(a * x ** 2 + b * x, x).subs(x, 1), diff(2 + log(x), x).subs(x, 1))
    sol = sp.solve([cont, der], [a, b], dict=True)[0]
    riga("(a) continuita': a+b = 2;  derivate: 2a+b = 1  ->", sol)
    h = Symbol("h", real=True)
    d0 = lim(h ** 2 * sin(1 / h) / h, h, 0)
    riga("(b) rapporto incrementale h sin(1/h) -> ", d0, " (carabinieri): f'(0) =", d0)
    fp = 2 * x * sin(1 / x) - cos(1 / x)
    l1 = lim(fp.subs(x, 1 / (2 * pi * k + 2 * pi)), k, oo)
    l2 = lim(fp.subs(x, 1 / (2 * pi * k + 3 * pi)), k, oo)
    riga(f"    per x != 0: f'(x) = 2x sin(1/x) - cos(1/x). Lungo x=1/(2 pi k) -> {l1}, "
         f"lungo x=1/((2k+1) pi) -> {l2}: il limite non esiste, f' NON e' continua in 0")
    verifica("(a) a=-1, b=3", (sol[a], sol[b]), (-1, 3))
    verifica("(b) f'(0)=0 e f' non continua (limiti -1 e +1)", (d0, l1, l2), (0, -1, 1))


def es28():
    titolo(28, "(a) tangente in e; (b) (f^-1)'(2); (c) punti angolosi di |x^2-1|")
    f = x * log(x)
    m = diff(f, x).subs(x, sp.E)
    ret = sp.simplify(f.subs(x, sp.E) + m * (x - sp.E))
    riga("(a) f(e) = e, f'(e) = ln e + 1 =", m, " -> tangente y =", ret)
    g = x ** 3 + x
    x0 = [r for r in sp.solve(g - 2, x) if r.is_real][0]
    inv = 1 / diff(g, x).subs(x, x0)
    riga(f"(b) f strettamente crescente; f(x0)=2 => x0 = {x0}; (f^-1)'(2) = 1/f'({x0}) = {inv}")
    riga("(c) |x^2-1|: x=+-1, derivate unilaterali:")
    pts = []
    for p in (1, -1):
        dd = diff(x ** 2 - 1, x).subs(x, p)
        # x^2-1 cambia segno in p: |g| = g da un lato e -g dall'altro
        d_sx, d_dx = -sp.sign(dd) * dd, sp.sign(dd) * dd
        riga(f"    in x={p}: f'_-({p}) = {d_sx}, f'_+({p}) = {d_dx}")
        pts.append((p, d_sx, d_dx))
    riga("    derivate unilaterali diverse: punti angolosi")
    verifica("(a) y = 2x - e", sp.simplify(ret - (2 * x - sp.E)), 0)
    verifica("(b) 1/4", inv, Rational(1, 4))
    verifica("(c) in x=1 e in x=-1: derivata sinistra -2, destra +2 (punti angolosi)", pts, [(1, -2, 2), (-1, -2, 2)])


def es29():
    titolo(29, "Lagrange / monotonia")
    riga("(a) Lagrange: sin a - sin b = cos(c)(a-b), |cos c|<=1 => |sin a - sin b| <= |a-b|")
    import random
    ok_a = all(abs(sp.sin(p) - sp.sin(q)) <= abs(p - q) + 1e-12 for p, q in
               [(random.uniform(-9, 9), random.uniform(-9, 9)) for _ in range(500)])
    riga("(b) g(x) = e^x-1-x: g' = e^x-1 <0 per x<0, >0 per x>0: minimo globale g(0)=0 => e^x >= 1+x")
    ok_b = all(exp(float(p)) >= 1 + float(p) - 1e-12 for p in [random.uniform(-9, 9) for _ in range(500)])
    h = sp.atan(xp) + sp.atan(1 / xp)
    dh = sp.simplify(diff(h, xp))
    riga("(c) h = arctg x + arctg(1/x): h' =", dh, " => h costante su (0,oo), h(1) =", sp.simplify(h.subs(xp, 1)))
    verifica("(a),(b) controllati anche numericamente su 500 casi", ok_a and ok_b, True)
    verifica("(c) h' = 0 e h = pi/2", (dh, sp.simplify(h.subs(xp, 1))), (0, pi / 2))


def es30():
    titolo(30, "Numero di soluzioni reali di x^3 - 3x + lambda = 0")
    g = x ** 3 - 3 * x
    crit = sp.solve(diff(g, x), x)
    riga("g(x) = x^3-3x:  g'=3(x^2-1); massimo locale g(-1) =", g.subs(x, -1), ", minimo locale g(1) =", g.subs(x, 1))
    riga("equazione g(x) = -lambda: 3 soluzioni se |lambda|<2, 2 se |lambda|=2, 1 se |lambda|>2")
    ris = {}
    for lam in (-3, -2, -1, 0, 1, 2, 3):
        ris[lam] = len(set(sp.real_roots(sp.Poly(x ** 3 - 3 * x + lam, x))))
    riga("conteggio numerico delle radici reali distinte:", ris)
    atteso = {lam: (3 if abs(lam) < 2 else 2 if abs(lam) == 2 else 1) for lam in ris}
    verifica("formula |lambda|<2:3, =2:2, >2:1 (controllo su 7 valori)", ris == atteso, True)


def es31():
    titolo(31, "de L'Hopital (verifica con Taylor)")
    a = lim((exp(x) - 1 - x) / x ** 2, x, 0)
    b = lim(log(x) / sqrt(x), x, oo)
    c = lim(x * log(x), x, 0, "+")
    riga("(a) 0/0 -> (e^x-1)/(2x) -> e^x/2:", a, "   Taylor: e^x-1-x = x^2/2+o(x^2)")
    riga("(b) oo/oo -> (1/x)/(1/(2 sqrt x)) = 2/sqrt x:", b)
    riga("(c) x ln x = ln x/(1/x) -> (1/x)/(-1/x^2) = -x:", c)
    verifica("(a) 1/2", a, Rational(1, 2))
    verifica("(b) 0", b, 0)
    verifica("(c) 0", c, 0)


def es32():
    titolo(32, "Teorema di Fermat")
    riga("Enunciato: se f e' definita in un intorno di x0, ha un estremo locale in x0 ed e' derivabile in x0, "
         "allora f'(x0) = 0.")
    riga("Dimostrazione (x0 massimo locale): per h>0 piccolo (f(x0+h)-f(x0))/h <= 0, quindi f'_+(x0) <= 0;")
    riga("    per h<0 il rapporto e' >= 0, quindi f'_-(x0) >= 0. Poiche' f e' derivabile f'_+ = f'_- = f'(x0),")
    riga("    quindi 0 <= f'(x0) <= 0, cioe' f'(x0) = 0. (minimo: analogo, o si applica a -f).")
    riga("Non vale il viceversa: f = x^3 ha f'(0) =", diff(x ** 3, x).subs(x, 0), "ma 0 non e' estremo (f e' crescente).")
    riga("Serve la derivabilita': f = |x| ha minimo in 0 ma f'_+(0) = 1, f'_-(0) = -1: f'(0) non esiste.")
    verifica("esempi: x^3 (f'(0)=0, strettamente crescente) e |x| (derivate unilaterali -1, 1)",
             (diff(x ** 3, x).subs(x, 0), lim(Abs(x) / x, x, 0, "-"), lim(Abs(x) / x, x, 0, "+")), (0, -1, 1))


def es33():
    titolo(33, "Maclaurin al terzo ordine di e^x sin x e limite")
    f = exp(x) * sin(x)
    s = sp.series(f, x, 0, 4).removeO()
    L = lim((f - x - x ** 2) / x ** 3, x, 0)
    riga("e^x sin x =", s, "+ o(x^3)")
    riga("limite =", L)
    verifica("sviluppo x + x^2 + x^3/3", sp.expand(s - (x + x ** 2 + x ** 3 / 3)), 0)
    verifica("limite 1/3", L, Rational(1, 3))


def es34():
    titolo(34, "Limiti con Taylor")
    a = lim((log(1 + x) - x + x ** 2 / 2) / x ** 3, x, 0)
    b = lim((sqrt(1 + x) - 1 - x / 2) / x ** 2, x, 0)
    riga("(a) ln(1+x) = x - x^2/2 + x^3/3 + o(x^3):", a)
    riga("(b) (1+x)^(1/2) = 1 + x/2 - x^2/8 + o(x^2):", b)
    verifica("(a) 1/3", a, Rational(1, 3))
    verifica("(b) -1/8", b, -Rational(1, 8))


def es35():
    titolo(35, "Classificare il punto critico x=0")
    res = []
    for nome, f in (("f = cos x - 1 + x^2/2", cos(x) - 1 + x ** 2 / 2), ("g = sin x - x + x^3/6", sin(x) - x + x ** 3 / 6)):
        ordine, c, tipo = classifica_critico(f)
        riga(f"{nome} = {c}*x^{ordine} + o(x^{ordine})  ->  {tipo}")
        res.append((ordine, c, tipo))
    verifica("(a) x^4/24: minimo locale", res[0], (4, Rational(1, 24), "minimo locale"))
    verifica("(b) x^5/120: nessun estremo", res[1], (5, Rational(1, 120), "nessun estremo (flesso a tangente orizzontale)"))


def es36():
    titolo(36, "e^0.1 con T_2(0.1) e resto di Lagrange")
    T2 = sp.Rational(1) + Rational(1, 10) + Rational(1, 2) * Rational(1, 100)
    riga("T_2(0.1) = 1 + 0.1 + 0.005 =", T2, "=", sp.N(T2))
    R2 = lambda e: e / 6 * Rational(1, 1000)
    bound = R2(Rational(111, 100))
    riga(f"R_2 = e^xi/3! * 0.1^3 con 0<xi<0.1: 0 < R_2 < e^0.1/6*10^-3 < 1.11/6*10^-3 = {sp.N(bound, 4)} < 2e-4")
    riga(f"quindi {sp.N(T2)} < e^0.1 < {sp.N(T2 + 2 * Rational(1, 10 ** 4), 6)};  valore vero e^0.1 = {sp.N(exp(Rational(1, 10)), 10)}")
    vero = exp(Rational(1, 10))
    verifica("T_2(0.1) = 1.105", T2, Rational(1105, 1000))
    verifica("1.105 < e^0.1 < 1.1052", bool(T2 < vero < T2 + Rational(2, 10 ** 4)), True)


def es37():
    titolo(37, "Studio di f(x) = x e^(-x)")
    r = studio_funzione(x * exp(-x), x, nome="f", png="es37_x_exp_meno_x.png", finestra=(-3, 8))
    verifica("Im f = (-oo, 1/e]", r.immagine, Interval(-oo, exp(-1)))


def es38():
    titolo(38, "Studio di f(x) = ln x / x; confronto e^pi e pi^e")
    f = log(x) / x
    r = studio_funzione(f, x, nome="f", png="es38_ln_x_su_x.png", finestra=(0.01, 12))
    riga("Per x>=e f e' strettamente decrescente e pi > e: ln(pi)/pi < ln(e)/e = 1/e, cioe' e ln pi < pi,")
    riga("quindi pi^e < e^pi.  Controllo numerico: pi^e =", sp.N(pi ** sp.E, 8), ", e^pi =", sp.N(sp.E ** pi, 8))
    verifica("Im f = (-oo, 1/e]", r.immagine, Interval(-oo, exp(-1)))
    verifica("pi^e < e^pi", bool(pi ** sp.E < sp.E ** pi), True)


def es39():
    titolo(39, "Studio di f(x) = x e^(1/x)")
    r = studio_funzione(x * exp(1 / x), x, nome="f", png="es39_x_exp_1_su_x.png", finestra=(-6, 6))
    verifica("Im f = (-oo,0) U [e,+oo)", r.immagine, Union(Interval.open(-oo, 0), Interval(sp.E, oo)))


def es40():
    titolo(40, "Studio di f(x) = (x^2-1) e^(-|x|)")
    f = (x ** 2 - 1) * exp(-Abs(x))
    r = studio_funzione(f, x, nome="f", png="es40_x2m1_exp_meno_abs_x.png", finestra=(-8, 8))
    M = (2 + 2 * sqrt(2)) * exp(-1 - sqrt(2))
    riga(f"massimi in x = +-(1+sqrt2), f = 2(1+sqrt2)e^(-1-sqrt2) ~ {sp.N(M, 4)};  minimo globale f(0) = -1; "
         "x=0 punto angoloso (f'+ = 1, f'- = -1)")
    ang = [d for d in r.info if d["c"] == 0][0]
    verifica("x=0 punto angoloso con derivate -1 e 1", (ang["tipo"], ang["dsx"], ang["ddx"]), ("punto angoloso", -1, 1))
    verifica("Im f = [-1, 2(1+sqrt2) e^(-1-sqrt2)]", r.immagine, Interval(-1, M))


ESERCIZI = {i: globals()[f"es{i}"] for i in range(1, 41)}
