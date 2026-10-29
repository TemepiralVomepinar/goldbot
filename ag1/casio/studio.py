# STUDIO.PY - Studio numerico di funzione (Casio fx-CG50)
# Scrivi f(x) come: x*exp(-x)  sqrt(x**2-1)/(x-2)  ln(x)/x  cbrt(x-6)*exp(-1/x)
# ^ = potenza, ln=log naturale, sen, tg, arctg, abs(), cbrt() radice cubica reale
# Se eval non funziona sulla calcolatrice: modifica la riga "def F" qui sotto.
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

def F(x):
    return x * exp(-x)

def val(x):
    try:
        r = float(F(x))
    except:
        return None
    if r != r or abs(r) > 1e150:
        return None
    return r

def setf():
    global F
    s = input("f(x)= ")
    if s.strip() == "":
        return
    try:
        F = eval("lambda x:" + conv(s))
        F(1.0)
    except Exception:
        pass
    print("f(x)=", s)

def d1(x, h=None):
    h = h or 1e-5 * max(1.0, abs(x))
    a, b = val(x + h), val(x - h)
    if a is None or b is None:
        return None
    return (a - b) / (2 * h)

def d2(x, h=None):
    h = h or 1e-3 * max(1.0, abs(x))
    a, b, c = val(x + h), val(x), val(x - h)
    if a is None or b is None or c is None:
        return None
    return (a - 2 * b + c) / (h * h)

def bis(g, a, b):
    ga = g(a)
    for _ in range(80):
        m = (a + b) / 2
        gm = g(m)
        if gm is None or ga is None:
            return m
        if gm == 0:
            return m
        if ga * gm < 0:
            b = m
        else:
            a, ga = m, gm
    return (a + b) / 2

def radici(g, a, b, N=400, tol=1e-4):
    out = []
    prev = None
    for i in range(N + 1):
        x = a + (b - a) * i / N
        y = g(x)
        if y is None:
            prev = None
            continue
        r = None
        if y == 0:
            r = x
        elif prev is not None and prev[1] * y < 0:
            r = bis(g, prev[0], x)
            gr = g(r)
            if gr is None or abs(gr) > tol:
                print("(salto/polo vicino a x=%s: non e' uno zero)" % ric(r, 1e-5))
                r = None
        if r is not None:
            out.append(r)
        prev = (x, y)
    return out

def big(x):
    try:
        return abs(float(F(x)))
    except ZeroDivisionError:
        return 1e300
    except:
        return 0.0

def picco(l, r):
    # posizione del massimo di |f| in [l,r] (polo)
    for _ in range(70):
        m1 = l + (r - l) / 3
        m2 = r - (r - l) / 3
        if big(m1) < big(m2):
            l = m1
        else:
            r = m2
    return (l + r) / 2

def salto(l, r):
    # localizza un salto di f fra l e r
    for _ in range(60):
        m = (l + r) / 2
        a, b, c = val(l), val(m), val(r)
        if a is None or b is None or c is None:
            break
        if abs(b - a) > abs(c - b):
            r = m
        else:
            l = m
    return (l + r) / 2

def rotture(a, b, N=600):
    # bordi del dominio, poli e salti in [a,b]
    xs = [a + (b - a) * i / N for i in range(N + 1)]
    ys = [val(x) for x in xs]
    out = []
    for i in range(N):
        if (ys[i] is None) != (ys[i + 1] is None):
            out.append(bordo(xs[i], xs[i + 1]))
    fin = [y for y in ys if y is not None and abs(y) < 1e3]
    rng = (max(fin) - min(fin)) if fin else 0
    dl = []
    for i in range(N):
        if ys[i] is not None and ys[i + 1] is not None:
            dl.append(abs(ys[i + 1] - ys[i]))
        else:
            dl.append(0)
    for i in range(1, N):
        y = ys[i]
        if y is None or ys[i - 1] is None or ys[i + 1] is None:
            continue
        if abs(y) > 1e3 and abs(y) >= abs(ys[i - 1]) and abs(y) >= abs(ys[i + 1]):
            out.append(picco(xs[i - 1], xs[i + 1]))
        elif (abs(y) < 1e3 and abs(ys[i + 1]) < 1e3 and dl[i] > 0.02 * rng
              and dl[i] > 10 * max(dl[i - 1], dl[i + 1] if i + 1 < N else 0) + 1e-12):
            out.append(salto(xs[i], xs[i + 1]))
    u = []
    for t in sorted(out):
        if not u or abs(t - u[-1]) > 1e-6 * max(1, abs(t)):
            u.append(t)
    return u

def partiz(a, b, extra):
    p = sorted([a, b] + extra + rotture(a, b))
    u = []
    for t in p:
        if not u or abs(t - u[-1]) > 1e-9 * max(1, abs(t)):
            u.append(t)
    return u

def segno_int(g, p, q):
    # segno di g su (p,q) campionando 5 punti; 0 se misto
    ss = []
    for k in (1, 2, 3, 4, 5):
        y = g(p + (q - p) * k / 6.0)
        if y is not None and y != 0:
            ss.append(1 if y > 0 else -1)
    if not ss:
        return None
    return ss[0] if all(t == ss[0] for t in ss) else 0

def iv(a, b):
    return "(%s, %s)" % (ric(a), ric(b))

def leggi_int(a_def, b_def):
    s = input("da [%g]: " % a_def).strip()
    a = num(s) if s else a_def
    s = input("a  [%g]: " % b_def).strip()
    b = num(s) if s else b_def
    return a, b

def tabella():
    a, b = leggi_int(-3, 3)
    p = input("passo [0.5]: ").strip()
    p = num(p) if p else 0.5
    x = a
    while x <= b + 1e-12:
        y = val(x)
        print("%.4g" % x, "->", "n.d." if y is None else "%.6g" % y)
        x += p

def bordo(p, q):
    # p e q con diverso stato (definita / non definita): trova il confine
    dp = val(p) is not None
    for _ in range(60):
        m = (p + q) / 2
        if (val(m) is not None) == dp:
            p = m
        else:
            q = m
    return (p + q) / 2

def dominio():
    a, b = leggi_int(-10, 10)
    N = 400
    stato = None
    ini = a
    xp = a
    for i in range(N + 1):
        x = a + (b - a) * i / N
        d = val(x) is not None
        if stato is None:
            stato = d
        elif d != stato:
            c = bordo(xp, x)
            print(("DEF" if stato else "n.d."), "da " + ric(ini) + " a " + ric(c))
            stato, ini = d, c
        xp = x
    print(("DEF" if stato else "n.d."), "da " + ric(ini) + " a " + ric(b))
    print("(punti isolati e confini a occhio: controlla)")

def zeri_segno():
    a, b = leggi_int(-5, 5)
    z = radici(val, a, b, 600, 1e-6)
    print("zeri:", [ric(t) for t in z] if z else "nessuno")
    pts = partiz(a, b, z)
    for i in range(len(pts) - 1):
        s = segno_int(val, pts[i], pts[i + 1])
        if s is not None:
            print("f", {1: ">0", -1: "<0", 0: "cambia segno (polo?)"}[s], "in " + iv(pts[i], pts[i + 1]))

def derivate():
    x = num(input("x0: "))
    v = val(x)
    a, b = d1(x), d2(x)
    print("f(x0)=", v)
    print("f'(x0)~", a)
    print("f''(x0)~", b)
    if a is not None and v is not None:
        print("tangente: y=%.6g*x+%.6g" % (a, v - a * x))

def estremi():
    a, b = leggi_int(-5, 5)
    cr = radici(d1, a, b, 800, 1e-3)
    pts = partiz(a, b, cr)
    rr = [t for t in pts[1:-1] if t not in cr]
    if rr:
        print("bordi/poli/salti in:", [ric(t, 1e-5) for t in rr])
    print("punti stazionari:", [ric(t) for t in cr] if cr else "nessuno")
    for c in cr:
        h = 1e-3 * max(1.0, abs(c))
        l, r = d1(c - h), d1(c + h)
        if l is None or r is None:
            continue
        t = "MAX" if (l > 0 and r < 0) else ("MIN" if (l < 0 and r > 0) else "flesso orizz.")
        c0 = 0.0 if abs(c) < 1e-6 else c
        print(t, "x=%s f=%s" % (ric(c0), fr(val(c0))))
    for i in range(len(pts) - 1):
        s = segno_int(d1, pts[i], pts[i + 1])
        if s is not None:
            print({1: "crescente", -1: "decrescente", 0: "misto(salto?)"}[s], "in " + iv(pts[i], pts[i + 1]))

def flessi():
    a, b = leggi_int(-5, 5)
    z = radici(d2, a, b, 800, 1e-2)
    print("flessi (f''=0):", [ric(t) for t in z] if z else "nessuno")
    for t in z:
        print("  x=%s f=%s" % (ric(t), fr(val(t))))
    pts = partiz(a, b, z)
    for i in range(len(pts) - 1):
        s = segno_int(d2, pts[i], pts[i + 1])
        if s is not None:
            print({1: "convessa", -1: "concava", 0: "misto(salto?)"}[s], "in " + iv(pts[i], pts[i + 1]))

def limite_a(x0, lato):
    # restituisce lista di valori avvicinandosi a x0 da lato (+1/-1) oppure all'infinito
    out = []
    for k in (1, 2, 3, 4, 5, 6, 7, 8):
        if abs(x0) == INF:
            X = (1.0 if x0 > 0 else -1.0) * 10.0 ** (k + 1)
        else:
            X = x0 + lato * 10.0 ** (-k)
        try:
            y = float(F(X))
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
    for i in range(len(ys) - 2, 0, -1):
        if abs(ys[i] - ys[i + 1]) < 1e-5 * max(1.0, abs(ys[i])):
            return "L = " + fr(ys[i + 1] if i == len(ys) - 2 else ys[i])
    if abs(a) > 1e4:
        return "+inf" if a > 0 else "-inf"
    return "non chiaro (oscilla/lento)"

def retta(m, q):
    ms, qs = ric(m, 1e-6), ric(q, 1e-5)
    t = "x" if ms == "1" else ("-x" if ms == "-1" else ms + "*x")
    if qs == "0":
        return t
    return t + ("-" + qs[1:] if qs[0] == "-" else "+" + qs)

def limiti():
    s = input("x0 (numero, oo, -oo): ")
    x0 = num(s)
    if abs(x0) == INF:
        v = limite_a(x0, 0)
        for X, y in v[::2]:
            print("x=%.3g f=%s" % (X, "n.d." if y is None else "%.8g" % y))
        print("limite:", stima(v))
        a1, a2 = (1e7, 2e7) if x0 > 0 else (-1e7, -2e7)
        f1, f2 = val(a1), val(a2)
        if f1 is not None and f2 is not None:
            m = (f2 - f1) / (a2 - a1)
            mr = float(eval(conv(ric(m, 1e-6)))) if ric(m, 1e-6)[0] in "-0123456789" and "pi" not in ric(m, 1e-6) else m
            q = f1 - mr * a1
            if abs(m) < 1e-6:
                print("asintoto orizzontale y=", fr(v[-1][1]))
            elif abs(q) < 1e8 and abs(m) < 1e6:
                print("asintoto obliquo y=" + retta(mr, q))
            else:
                print("nessun asintoto (cresce piu' di una retta)")
    else:
        for lato, nome in ((-1, "sx"), (1, "dx")):
            v = limite_a(x0, lato)
            for X, y in v[::3]:
                print(nome, "x=%.9g f=%s" % (X, "n.d." if y is None else "%.8g" % y))
            print(" -> limite", nome, ":", stima(v))
        y0 = val(x0)
        print("f(x0)=", "n.d." if y0 is None else fr(y0))

def nonderiv():
    x0 = num(input("x0: "))
    y0 = val(x0)
    if y0 is None:
        print("f non definita in x0")
        return
    res = []
    for h in (1e-4, 1e-6, 1e-8):
        a, b = val(x0 + h), val(x0 - h)
        if a is None or b is None:
            print("f non definita da un lato")
            return
        res.append(((a - y0) / h, (y0 - b) / h))
    dp, dm = res[-1]
    print("deriv. dx ~", res[0][0], res[1][0], res[2][0])
    print("deriv. sx ~", res[0][1], res[1][1], res[2][1])
    big = lambda t: abs(t) > 1e3
    if big(dp) or big(dm):
        if big(dp) and big(dm):
            print("TG VERTICALE" if sgn(dp) == sgn(dm) else "CUSPIDE", "(flesso se stesso segno)")
        else:
            print("tangente verticale da un lato")
    elif abs(dp - dm) < 1e-3:
        print("DERIVABILE, f'(x0)~", fr((dp + dm) / 2))
    else:
        print("PUNTO ANGOLOSO: f'-=%s f'+=%s" % (ric(dm), ric(dp)))

def immagine():
    a, b = leggi_int(-10, 10)
    N = 2000
    mn = mx = None
    for i in range(N + 1):
        x = a + (b - a) * i / N
        y = val(x)
        if y is None:
            continue
        if mn is None or y < mn[1]:
            mn = (x, y)
        if mx is None or y > mx[1]:
            mx = (x, y)
    if mn is None:
        print("f mai definita")
        return
    print("min ~", fr(mn[1]), "in x~%.5g" % mn[0])
    print("max ~", fr(mx[1]), "in x~%.5g" % mx[0])
    print("(se il valore e' agli estremi o alle")
    print(" singolarita' guarda i limiti: Im f)")

def soluzioni():
    a, b = leggi_int(-5, 5)
    c = num(input("c (f(x)=c): "))
    g = lambda x: (None if val(x) is None else val(x) - c)
    z = radici(g, a, b, 1000, 1e-6)
    print("n. soluzioni:", len(z))
    for t in z:
        print("  x=", ric(t))

def grafico():
    a, b = leggi_int(-5, 5)
    try:
        from casioplot import set_pixel, show_screen, clear_screen
    except:
        print("casioplot non disponibile")
        return
    W, H = 384, 192
    xs = [a + (b - a) * i / (W - 1) for i in range(W)]
    ys = [val(x) for x in xs]
    ok = sorted([y for y in ys if y is not None])
    if not ok:
        return
    lo, hi = ok[int(len(ok) * 0.03)], ok[int(len(ok) * 0.97)]
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    pad = (hi - lo) * 0.1
    lo, hi = lo - pad, hi + pad
    clear_screen()
    if lo < 0 < hi:
        py = int((hi - 0) / (hi - lo) * (H - 1))
        for px in range(W):
            set_pixel(px, py, (150, 150, 150))
    if a < 0 < b:
        px = int((0 - a) / (b - a) * (W - 1))
        for py in range(H):
            set_pixel(px, py, (150, 150, 150))
    for i in range(W):
        y = ys[i]
        if y is not None and lo <= y <= hi:
            set_pixel(i, int((hi - y) / (hi - lo) * (H - 1)), (0, 0, 255))
    show_screen()
    print("x in [%.3g, %.3g]  y in [%.3g, %.3g]" % (a, b, lo, hi))

MENU = (
    "1 tabella valori",
    "2 dominio (n.d.)",
    "3 zeri e segno",
    "4 f', f'' e tangente",
    "5 estremi/monotonia",
    "6 flessi/convessita'",
    "7 limiti+asintoti",
    "8 non derivabilita'",
    "9 min/max/immagine",
    "10 f(x)=c: n.soluz.",
    "11 grafico",
    "12 cambia f(x)",
    "0 esci",
)
AZ = {1: tabella, 2: dominio, 3: zeri_segno, 4: derivate, 5: estremi, 6: flessi,
      7: limiti, 8: nonderiv, 9: immagine, 10: soluzioni, 11: grafico, 12: setf}

def main():
    print("STUDIO FUNZIONE")
    setf()
    while True:
        for r in MENU:
            print(r)
        try:
            s = input("scelta: ").strip()
            if s == "0":
                break
            if s and int(s) in AZ:
                AZ[int(s)]()
                input("[EXE]")
        except Exception as e:
            print("errore:", e)

main()
