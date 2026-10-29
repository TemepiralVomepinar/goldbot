# ESTREMI.PY - Insiemi, sup/inf/max/min, soluzioni, induzione (Casio fx-CG50)
# Successioni: variabile n. Funzioni/condizioni: variabile x.
# Condizioni: x**2-2*x-3<0 and abs(x)>=1   (and, or, <, <=, >, >=)
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

# ------------------------------------------------- sup / inf di {a_n}
def parti(f, n0, N):
    return [ev(f, n) for n in range(n0, n0 + N)]

def estremi_succ():
    f = mk(input("a_n= (variabile n) "), "n")
    n0 = int(leggi("n0", 1.0))
    N = 4000
    ys = parti(f, n0, N)
    if None in ys:
        print("a_n non definita per alcuni n")
        return
    L1, L2 = ev(f, 10 ** 6), ev(f, 10 ** 6 + 1)
    mx = argmax(ys)
    mn = argmin(ys)
    M, m = ys[mx], ys[mn]
    if L1 is None or L2 is None:
        Ls = Li = None
        print("limite: n.d.")
    else:
        Ls, Li = max(L1, L2), min(L1, L2)
        print("limiti (n pari/dispari ->): %s ; %s" % (ric(L1, 1e-4), ric(L2, 1e-4)))
    # sup
    if Ls is not None and Ls > M + 1e-9:
        print("SUP = %s  (limite, NON assunto: niente max)" % ric(Ls, 1e-4))
    else:
        print("SUP = MAX = %s  per n=%d" % (ric(M, 1e-9), n0 + mx))
    # inf
    if Li is not None and Li < m - 1e-9:
        print("INF = %s  (limite, NON assunto: niente min)" % ric(Li, 1e-4))
    else:
        print("INF = MIN = %s  per n=%d" % (ric(m, 1e-9), n0 + mn))
    # pari e dispari
    pa = [ys[i] for i in range(N) if (n0 + i) % 2 == 0]
    di = [ys[i] for i in range(N) if (n0 + i) % 2 == 1]
    print("pari: max=%s min=%s" % (ric(max(pa), 1e-6), ric(min(pa), 1e-6)))
    print("dispari: max=%s min=%s" % (ric(max(di), 1e-6), ric(min(di), 1e-6)))
    print("(se il valore e' agli estremi dei primi")
    print(" 4000 termini controlla il limite)")

# ------------------------------------- insieme definito da una condizione
def insieme():
    print("Condizione in x (True/False), es:")
    print("x**2-2*x-3<0 and abs(x)>=1")
    s = input("cond= ")
    P = eval("lambda x:" + conv(s))
    a, b = leggi("da", -10.0), leggi("a", 10.0)
    N = 4000

    def T(x):
        try:
            return bool(P(x))
        except:
            return False
    xs = [a + (b - a) * i / N for i in range(N + 1)]
    st = [T(x) for x in xs]
    inter = []
    ini = a if st[0] else None
    for i in range(N):
        if st[i] != st[i + 1]:
            lo, hi = xs[i], xs[i + 1]
            for _ in range(60):
                m = (lo + hi) / 2
                if T(m) == st[i]:
                    lo = m
                else:
                    hi = m
            c = (lo + hi) / 2
            if st[i]:
                inter.append((ini, c))
                ini = None
            else:
                ini = c
    if ini is not None:
        inter.append((ini, b))
    if not inter:
        print("insieme vuoto in [%g,%g]" % (a, b))
        return
    t = s.replace("<=", "L").replace(">=", "L").replace("==", "L")
    n_larghi = t.count("L")
    n_stretti = t.count("<") + t.count(">")

    def chiuso(c, bordo):
        if bordo:
            return False
        if n_larghi == 0:
            return False
        if n_stretti == 0:
            return True
        r = ric(c, 1e-6).replace("^", "**")
        try:
            c0 = float(eval(r))
            if abs(c0 - c) < 1e-6:
                return T(c0)
        except:
            pass
        return T(c)
    for lo, hi in inter:
        print("%s%s , %s%s" % ("[" if chiuso(lo, lo <= a + 1e-9) else "(", ric(lo, 1e-6),
                               ric(hi, 1e-6), "]" if chiuso(hi, hi >= b - 1e-9) else ")"))
    print("inf ~", ric(inter[0][0], 1e-6), " sup ~", ric(inter[-1][1], 1e-6))
    print("(estremi a/b della finestra: insieme illimitato)")
    print("max/min esistono se l'estremo e' chiuso [ ]")

# ------------------------------------------------- insieme delle soluzioni
def soluzioni():
    f = mk(input("g(x)=0, g(x)= "))
    a, b = leggi("da", -10.0), leggi("a", 10.0)
    N = 6000
    xs = [a + (b - a) * i / N for i in range(N + 1)]
    ys = [ev(f, x) for x in xs]
    sol = []
    for i in range(N):
        if ys[i] is None or ys[i + 1] is None:
            continue
        if ys[i] == 0:
            sol.append(xs[i])
        elif ys[i] * ys[i + 1] < 0:
            lo, hi = xs[i], xs[i + 1]
            for _ in range(60):
                m = (lo + hi) / 2
                if ev(f, lo) * ev(f, m) <= 0:
                    hi = m
                else:
                    lo = m
            r = (lo + hi) / 2
            if abs(ev(f, r)) < 1e-6:
                sol.append(r)
    for i in range(1, N):
        y0, y1, y2 = ys[i - 1], ys[i], ys[i + 1]
        if y0 is None or y1 is None or y2 is None or y1 == 0:
            continue
        if abs(y1) <= abs(y0) and abs(y1) <= abs(y2) and y0 * y1 >= 0 and y1 * y2 >= 0:
            lo, hi = xs[i - 1], xs[i + 1]
            for _ in range(100):
                m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
                v1, v2 = ev(f, m1), ev(f, m2)
                if v1 is None or v2 is None:
                    break
                if abs(v1) < abs(v2):
                    hi = m2
                else:
                    lo = m1
            r = (lo + hi) / 2
            v = ev(f, r)
            if v is not None and abs(v) < 1e-12 and not any(abs(r - s) < 1e-6 for s in sol):
                sol.append(r)
    sol.sort()
    print("soluzioni in [%g,%g]: %d" % (a, b, len(sol)))
    for s in sol[:12]:
        print("  x =", ric(s, 1e-7))
    if len(sol) > 12:
        print("  ... (%d in totale)" % len(sol))
    if sol:
        print("min=%s max=%s" % (ric(min(sol), 1e-6), ric(max(sol), 1e-6)))

# ------------------------------------------ max/min assoluti di f su [a,b]
def massimo_minimo():
    f = mk(input("f(x)= "))
    a, b = leggi("a", 0.0), leggi("b", 1.0)
    N = 20000
    best = None
    worst = None
    for i in range(N + 1):
        x = a + (b - a) * i / N
        y = ev(f, x)
        if y is None:
            continue
        if best is None or y > best[1]:
            best = (x, y)
        if worst is None or y < worst[1]:
            worst = (x, y)
    if best is None:
        print("f mai definita")
        return
    # raffina con sezione aurea locale
    def raf(x0, segno):
        l, r = max(a, x0 - (b - a) / N), min(b, x0 + (b - a) / N)
        for _ in range(80):
            m1, m2 = l + (r - l) / 3, r - (r - l) / 3
            v1, v2 = ev(f, m1), ev(f, m2)
            if v1 is None or v2 is None:
                break
            if segno * v1 < segno * v2:
                l = m1
            else:
                r = m2
        x = (l + r) / 2
        return x, ev(f, x)
    xb, yb = raf(best[0], 1)
    xw, yw = raf(worst[0], -1)
    print("MAX ~ %s in x ~ %s" % (fr(yb), ric(xb, 1e-6)))
    print("MIN ~ %s in x ~ %s" % (fr(yw), ric(xw, 1e-6)))
    print("f(a)=%s f(b)=%s" % (fr(ev(f, a)), fr(ev(f, b))))

# ------------------------------------------------------- induzione (test)
def induzione():
    print("P(n) booleana in n, es:")
    print("2**n>=n**2   sum(k*k for k in range(1,n+1))==n*(n+1)*(2*n+1)/6")
    print("(uguaglianze con floats: usa abs(A-B)<1e-9)")
    s = input("P(n)= ")
    P = eval("lambda n:" + conv(s))
    n0 = int(leggi("n0", 1.0))
    N = int(leggi("fino a", 200.0))
    ko = []
    for n in range(n0, N + 1):
        try:
            if not P(n):
                ko.append(n)
        except:
            ko.append(n)
        if len(ko) > 8:
            break
    if ko:
        print("P(n) FALSA per n =", ko)
    else:
        print("P(n) vera per n=%d..%d (non e' una dimostrazione!)" % (n0, N))
    print("Dim: base P(n0); passo: P(n)=>P(n+1)")

# ---------------------------------------------- famiglie di intervalli
def famiglia():
    fa = mk(input("estremo sx a_n= "), "n")
    fb = mk(input("estremo dx b_n= "), "n")
    n0 = int(leggi("n0", 1.0))
    N = 3000
    A = [ev(fa, n) for n in range(n0, n0 + N)]
    B = [ev(fb, n) for n in range(n0, n0 + N)]
    if None in A or None in B:
        print("n.d.")
        return
    La, Lb = ev(fa, 10 ** 6), ev(fb, 10 ** 6)
    print("a_n: min=%s max=%s lim~%s" % (ric(min(A), 1e-6), ric(max(A), 1e-6), ric(La, 1e-4)))
    print("b_n: min=%s max=%s lim~%s" % (ric(min(B), 1e-6), ric(max(B), 1e-6), ric(Lb, 1e-4)))
    lo = min(min(A), La) if La is not None else min(A)
    hi = max(max(B), Lb) if Lb is not None else max(B)
    il = max(max(A), La) if La is not None else max(A)
    ih = min(min(B), Lb) if Lb is not None else min(B)
    conn = all(max(A[i], A[i + 1]) <= min(B[i], B[i + 1]) for i in range(N - 1))
    print("UNIONE ~ da %s a %s%s" % (ric(lo, 1e-4), ric(hi, 1e-4),
          "" if conn else " (a pezzi: guarda gli intervalli)"))
    print("INTERSEZIONE ~ da %s a %s%s" % (ric(il, 1e-4), ric(ih, 1e-4),
          "  (VUOTA)" if il >= ih else ""))
    tocc = [max(A[i], A[i + 1]) for i in range(N - 1) if abs(max(A[i], A[i + 1]) - min(B[i], B[i + 1])) < 1e-12]
    if tocc:
        print("ATTENZIONE: intervalli che si toccano in x=%s:" % ric(tocc[0], 1e-6))
        print(" se aperti, quel punto MANCA dall'unione")
    print("estremi chiusi/aperti: vedi se il valore e'")
    print("assunto (min/max raggiunti) o solo limite")

def main():
    menu("INSIEMI, SUP/INF",
         ("1 sup/inf di {a_n}",
          "2 insieme da condizione",
          "3 soluzioni di g(x)=0",
          "4 max/min di f su [a,b]",
          "5 test induzione P(n)",
          "6 famiglia di intervalli",
          "0 esci"),
         {1: estremi_succ, 2: insieme, 3: soluzioni, 4: massimo_minimo,
          5: induzione, 6: famiglia})

main()
