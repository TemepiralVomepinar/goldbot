# LIMITI.PY - Limiti, successioni, ordini di infinitesimo (Casio fx-CG50)
# Espressioni: ^ potenza, ln, sen, tg, arctg, abs(), cbrt(), factorial(n), e, pi
# Successioni: usa la variabile n (es. (1+1/n)**n). Limiti: usa x.
from math import *
INF = float("inf")

def cbrt(v):
    return -((-v) ** (1.0 / 3)) if v < 0 else v ** (1.0 / 3)

def sgn(v):
    return 1 if v > 0 else (-1 if v < 0 else 0)

def conv(s):
    for a, b in (("^", "**"), ("arctg", "atan"), ("arcsen", "asin"),
                 ("arccos", "acos"), ("sen", "sin"), ("tg", "tan"), ("ln", "log")):
        s = s.replace(a, b)
    return s

def num(s):
    s = conv(s.strip())
    if s in ("oo", "+oo", "inf"):
        return INF
    if s in ("-oo", "-inf"):
        return -INF
    try:
        return float(s)
    except:
        return float(eval(s))

def ric(v, tol=1e-7):
    # riconosce v come frazione, multiplo di pi, pi^2, radice o potenza di e
    if v is None:
        return "n.d."
    if v != v or abs(v) > 1e12:
        return "%.6g" % v
    if abs(v) < tol:
        return "0"
    if abs(v - round(v)) < tol:
        return "%d" % round(v)
    for q in range(2, 13):
        p = round(v * q)
        if abs(v - p / q) < tol:
            return "%d/%d" % (p, q)
    for q in range(1, 13):
        p = round(v / pi * q)
        if p != 0 and abs(v - p * pi / q) < tol:
            k = "" if abs(p) == 1 else "%d*" % abs(p)
            return ("-" if p < 0 else "") + k + "pi" + ("/%d" % q if q > 1 else "")
    for q in range(1, 13):
        p = round(v / (pi * pi) * q)
        if p != 0 and abs(v - p * pi * pi / q) < tol:
            k = "" if abs(p) == 1 else "%d*" % abs(p)
            return ("-" if p < 0 else "") + k + "pi^2" + ("/%d" % q if q > 1 else "")
    for q in range(13, 121):
        p = round(v * q)
        if abs(v - p / q) < tol:
            return "%d/%d" % (p, q)
    for q in range(1, 31):
        p = round(v * v * q)
        if p > 0 and abs(v * v - p / q) < tol:
            r = "sqrt(%d/%d)" % (p, q) if q > 1 else "sqrt(%d)" % p
            return r if v > 0 else "-" + r
    if v > 0:
        l = log(v)
        for q in range(1, 7):
            p = round(l * q)
            if p != 0 and abs(l - p / q) < tol:
                if q == 1:
                    return "e" if p == 1 else "e^%d" % p
                return "e^(%d/%d)" % (p, q)
    return "%.6g" % v

def fr(v):
    if v is None:
        return "n.d."
    return "%.6g (=%s)" % (v, ric(v, 5e-7))

def mk(s, var="x"):
    return eval("lambda %s:%s" % (var, conv(s)))

def ev(f, *a):
    try:
        r = float(f(*a))
    except:
        return None
    if r != r or abs(r) > 1e150:
        return None
    return r

def leggi(prompt, d=None):
    s = input(prompt + (" [%g]: " % d if d is not None else ": ")).strip()
    if s == "" and d is not None:
        return d
    return num(s)

def _fact(n):
    r = 1
    for k in range(2, int(n) + 1):
        r *= k
    return r

try:
    factorial
except NameError:
    factorial = _fact

def argmax(v):
    j = 0
    for i in range(len(v)):
        if v[i] > v[j]:
            j = i
    return j

def argmin(v):
    j = 0
    for i in range(len(v)):
        if v[i] < v[j]:
            j = i
    return j

def pausa():
    input("[EXE]")

def menu(titolo, voci, azioni):
    print(titolo)
    while True:
        for r in voci:
            print(r)
        try:
            s = input("scelta: ").strip()
            if s == "0":
                break
            if s and int(s) in azioni:
                azioni[int(s)]()
                pausa()
        except Exception as e:
            print("errore:", e)

# ---------------------------------------------------------------- limiti
def valori_vicino(f, x0, lato):
    out = []
    for k in (1, 2, 3, 4, 5, 6, 7, 8):
        if abs(x0) == INF:
            X = (1.0 if x0 > 0 else -1.0) * 10.0 ** (k + 1)
        else:
            X = x0 + lato * 10.0 ** (-k)
        try:
            y = float(f(X))
        except:
            y = None
        out.append((X, y))
    return out

def stima(vs):
    ys = [y for (_, y) in vs if y is not None and y == y]
    if not ys:
        return "non definita vicino"
    a = ys[-1]
    if vs[-1][1] is None or vs[-1][1] != vs[-1][1]:
        if abs(a) > 1e3:
            return "+inf (overflow)" if a > 0 else "-inf (overflow)"
        return "non definita vicino"
    if len(ys) < 3:
        return "non definita vicino"
    b = ys[-2]
    if abs(a) > 1e5 and abs(a) > abs(b) * 1.5:
        return "+inf" if a > 0 else "-inf"
    for i in range(1, len(ys) - 2):
        # primo tratto stabile (3 valori consecutivi): evita il crollo finale per cancellazione
        if abs(ys[i] - ys[i + 1]) < 1e-5 * max(1.0, abs(ys[i])) and abs(ys[i + 1] - ys[i + 2]) < 1e-5 * max(1.0, abs(ys[i])):
            j = i + 2
            while j + 1 < len(ys) and abs(ys[j] - ys[j + 1]) < 1e-5 * max(1.0, abs(ys[j])):
                j += 1
            return "L = " + fr(ys[j])
    for i in range(len(ys) - 2, 0, -1):
        if abs(ys[i] - ys[i + 1]) < 1e-5 * max(1.0, abs(ys[i])):
            return "L = " + fr(ys[i + 1] if i == len(ys) - 2 else ys[i])
    if abs(a) > 1e4:
        return "+inf" if a > 0 else "-inf"
    return "non chiaro (oscilla/lento)"

def lim_funzione():
    f = mk(input("f(x)= "))
    x0 = num(input("x0 (num, oo, -oo): "))
    lati = [0] if abs(x0) == INF else [-1, 1]
    for lato in lati:
        v = valori_vicino(f, x0, lato)
        nome = "" if lato == 0 else ("sx " if lato < 0 else "dx ")
        for X, y in v[::2]:
            print(nome + "x=%.9g f=%s" % (X, "n.d." if y is None else "%.8g" % y))
        print(" -> limite " + nome + ":", stima(v))
    print("(forme 0/0, oo-oo: usa 'ordine')")

# ------------------------------------------------------------ successioni
def termini(f, n0, N):
    out = []
    for n in range(n0, n0 + N):
        out.append(ev(f, n))
    return out

def succ():
    f = mk(input("a_n= "), "n")
    n0 = int(num(input("n0 [1]: ") or "1"))
    print("primi:", [("%.5g" % y if y is not None else "n.d.") for y in termini(f, n0, 6)])
    v = []
    for k in (1, 2, 3, 4, 5, 6):
        n = 10 ** k
        v.append((n, ev(f, n)))
    for n, y in v:
        print("n=%d a_n=%s" % (n, "n.d." if y is None else "%.8g" % y))
    print("limite:", stima(v))
    N = 3000
    ys = termini(f, n0, N)
    if None in ys:
        print("a_n non definita per alcuni n")
        return
    inc = all(ys[i + 1] >= ys[i] - 1e-12 for i in range(N - 1))
    dec = all(ys[i + 1] <= ys[i] + 1e-12 for i in range(N - 1))
    stinc = all(ys[i + 1] > ys[i] for i in range(N - 1))
    stdec = all(ys[i + 1] < ys[i] for i in range(N - 1))
    print("monotona:", "STRETT. CRESC." if stinc else "crescente" if inc else
          "STRETT. DECR." if stdec else "decrescente" if dec else "no (non monotona)")
    imx = argmax(ys)
    imn = argmin(ys)
    print("max(primi %d)=%s per n=%d" % (N, ric(ys[imx], 1e-9), n0 + imx))
    print("min(primi %d)=%s per n=%d" % (N, ric(ys[imn], 1e-9), n0 + imn))
    M = 10 ** 6
    pa, di = ev(f, M), ev(f, M + 1)
    print("n pari  -> %s ; n dispari -> %s" % (ric(pa, 1e-4), ric(di, 1e-4)))
    if pa is not None and di is not None:
        if abs(pa - di) > 1e-4:
            print("limiti diversi: NON esiste il limite")
        else:
            print("pari e dispari -> stesso valore")

def ricorrenza():
    g = mk(input("g(a) con a_(n+1)=g(a_n): "), "a")
    a = num(input("a_1= "))
    s = [a]
    for _ in range(60):
        a = ev(g, a)
        if a is None:
            print("g non definita")
            break
        s.append(a)
    print("a1..a6:", ["%.6g" % t for t in s[:6]])
    print("a_60 ~", "%.10g" % s[-1] if s else "")
    print("andamento:", "crescente" if all(s[i + 1] >= s[i] - 1e-12 for i in range(len(s) - 1)) else
          "decrescente" if all(s[i + 1] <= s[i] + 1e-12 for i in range(len(s) - 1)) else "non monotona")
    h = lambda t: None if ev(g, t) is None else ev(g, t) - t
    xs = [-10 + 20 * i / 2000.0 for i in range(2001)]
    punti = []
    prev = None
    for t in xs:
        y = h(t)
        if y is None:
            prev = None
            continue
        if prev is not None and prev[1] * y <= 0:
            a1, b1 = prev[0], t
            for _ in range(60):
                m = (a1 + b1) / 2
                if h(a1) * h(m) <= 0:
                    b1 = m
                else:
                    a1 = m
            punti.append((a1 + b1) / 2)
        prev = (t, y)
    print("punti fissi L=g(L):", [ric(p, 1e-8) for p in punti])

def rapporto():
    f = mk(input("a_n (>0)= "), "n")
    for n in (10, 20, 40, 60):
        a, b = ev(f, n), ev(f, n + 1)
        if a is None or b is None or a == 0:
            print("n=%d: n.d." % n)
            continue
        r = b / a
        rad = None
        try:
            rad = a ** (1.0 / n)
        except:
            pass
        print("n=%d a_(n+1)/a_n=%.6g  a_n^(1/n)=%s" % (n, r, "n.d." if rad is None else "%.6g" % rad))
    print("l<1 -> a_n->0 ; l>1 -> a_n->+oo ; l=1 non si sa")

# ----------------------------------------------- ordine di infinitesimo
def ordine_in(f, x0, lato):
    h = lato * 0.01
    r = []
    for hh in (h, h / 2, h / 4):
        a, b = ev(f, x0 + hh), ev(f, x0 + 2 * hh)
        if a is None or b is None or a == 0 or b == 0:
            return None
        r.append(log(abs(b / a)) / log(2.0))
    p = r[-1]
    pr = round(p * 2) / 2.0
    hh = lato * 0.001
    c = ev(f, x0 + hh)
    c = None if c is None else c / abs(hh) ** pr
    return r, pr, c

def ordine():
    f = mk(input("f(x)= "))
    x0 = leggi("x0", 0.0)
    cs = []
    pr = None
    for lato in (1, -1):
        o = ordine_in(f, x0, lato)
        if o is None:
            print("lato", "dx" if lato > 0 else "sx", ": f nulla o n.d.")
            continue
        r, pr, c = o
        print("lato", "dx" if lato > 0 else "sx", ": p~", ["%.3f" % t for t in r])
        cs.append(c)
    if pr is not None:
        c = cs[0]
        if len(cs) == 2 and cs[0] is not None and cs[1] is not None and cs[0] * cs[1] > 0:
            c = (cs[0] + cs[1]) / 2.0      # la media cancella il termine di ordine successivo
        print("f ~ c*(x-x0)^p con p=%g, c~%s" % (pr, "n.d." if c is None else fr3(c)))
    print("(se p e' vicino a un intero/mezzo: ok)")

def fr3(c):
    return "%.4g (=%s)" % (c, ric(c, 3e-3))

def ordine_inf():
    f = mk(input("f(x)= "))
    r = []
    for X in (1e2, 1e3, 1e4):
        a, b = ev(f, X), ev(f, 2 * X)
        if a is None or b is None or a == 0 or b == 0:
            print("X=%g: n.d." % X)
            continue
        r.append(log(abs(b / a)) / log(2.0))
        print("X=%g  p~%.4f  tasso exp~%.3g" % (X, r[-1], log(abs(b / a)) / X))
    print("f ~ x^p se p stabile; se p cresce -> esponenziale")

def soglia():
    N = mk(input("N(x)= "))
    D = mk(input("D(x)= (base, ->0) "))
    x0 = leggi("x0", 0.0)
    oN = ordine_in(N, x0, 1)
    oD = ordine_in(D, x0, 1)
    if oN is None or oD is None:
        print("n.d.")
        return
    pN, pD = oN[1], oD[1]
    print("N ~ x^%g , D ~ x^%g" % (pN, pD))
    if pD > 0:
        s = pN / pD
        print("N/D^a ~ x^(%g - %g*a)" % (pN, pD))
        print("a < %s: limite 0" % ric(s))
        print("a = %s: limite finito !=0" % ric(s))
        print("a > %s: limite infinito" % ric(s))

# ---------------------------------------------------- limite con parametro
def lim_par():
    f = mk(input("f(x,a)= "), "x,a")
    x0 = num(input("x0 (num, oo): "))
    V = num(input("valore V [0]: ") or "0")
    A0, A1 = leggi("a da", -6.0), leggi("a a", 6.0)

    def L(a):
        if abs(x0) == INF:
            v1, v2 = ev(f, 1e3, a), ev(f, 1e4, a)
        else:
            v1, v2 = ev(f, x0 + 1e-3, a), ev(f, x0 + 1e-4, a)
        if v1 is None or v2 is None:
            return None
        return (10 * v2 - v1) / 9.0
    pts = []
    N = 240
    prev = None
    for i in range(N + 1):
        a = A0 + (A1 - A0) * i / N
        y = L(a)
        if y is None:
            prev = None
            continue
        y -= V
        if prev is not None and prev[1] * y <= 0 and abs(y - prev[1]) < 1e3:
            lo, hi = prev[0], a
            for _ in range(50):
                m = (lo + hi) / 2
                ym = L(m)
                if ym is None:
                    break
                if (L(lo) - V) * (ym - V) <= 0:
                    hi = m
                else:
                    lo = m
            pts.append((lo + hi) / 2)
        prev = (a, y)
    print("a tali che limite = %s:" % ric(V))
    for p in pts:
        print("  a ~", fr(p), " L(a)=", "%.6g" % L(p))
    if not pts:
        print("  nessuno in [%g,%g]" % (A0, A1))
    for a in (A0, 0.0, A1):
        print("L(%g) ~ %s" % (a, "n.d." if L(a) is None else "%.6g" % L(a)))

def confronto():
    f = mk(input("f(n)= "), "n")
    g = mk(input("g(n)= "), "n")
    for n in (10, 100, 1000, 10000):
        a, b = ev(f, n), ev(g, n)
        if a is None or b is None or b == 0:
            print("n=%d: n.d." % n)
            continue
        print("n=%d f/g=%.6g" % (n, a / b))
    print("f/g->0: f=o(g). Gerarchia:")
    print("ln n<n^a<b^n<n!<n^n")

def main():
    menu("LIMITI E SUCCESSIONI",
         ("1 lim f(x) x->x0",
          "2 successione a_n",
          "3 ricorrenza a(n+1)=g(a)",
          "4 rapporto/radice",
          "5 ordine infinitesimo",
          "6 ordine all'infinito",
          "7 N/D^a: soglia di a",
          "8 limite con parametro a",
          "9 confronto f/g",
          "0 esci"),
         {1: lim_funzione, 2: succ, 3: ricorrenza, 4: rapporto, 5: ordine,
          6: ordine_inf, 7: soglia, 8: lim_par, 9: confronto})

main()
