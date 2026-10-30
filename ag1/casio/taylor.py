# TAYLOR.PY - Derivate numeriche, Taylor, classificazione punti critici (Casio fx-CG50)
# f(x) come negli altri programmi. Le derivate sono numeriche (approssimate).
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

# ---------------------------------------------------- derivate numeriche
def der(f, x, k, h=None):
    # derivata k-esima (k=1..5) con differenze centrali; None se non calcolabile
    if h is None:
        h = {1: 1e-4, 2: 1e-3, 3: 1e-2, 4: 3e-2, 5: 6e-2}[k]
    if k == 1:
        c = ((1, 1), (-1, -1))
        d = 2 * h
    elif k == 2:
        c = ((1, 1), (0, -2), (-1, 1))
        d = h ** 2
    elif k == 3:
        c = ((2, 1), (1, -2), (-1, 2), (-2, -1))
        d = 2 * h ** 3
    elif k == 4:
        c = ((2, 1), (1, -4), (0, 6), (-1, -4), (-2, 1))
        d = h ** 4
    else:
        c = ((3, 1), (2, -4), (1, 5), (-1, -5), (-2, 4), (-3, -1))
        d = 2 * h ** 5
    s = 0.0
    for m, w in c:
        v = ev(f, x + m * h)
        if v is None:
            return None
        s += w * v
    return s / d

def derivate():
    f = mk(input("f(x)= "))
    x0 = leggi("x0", 0.0)
    print("f(x0) =", fr(ev(f, x0)))
    ds = []
    for k in (1, 2, 3, 4, 5):
        d = der(f, x0, k)
        ds.append(d)
        print("f^(%d)(x0) ~ %s" % (k, "n.d." if d is None else fr(d)))
    print("(valori ~0 entro 1e-3: sono zero)")
    return ds

def classifica():
    f = mk(input("f(x)= "))
    x0 = leggi("x0 (punto critico)", 0.0)
    for k in range(1, 6):
        d = der(f, x0, k)
        if d is None:
            print("derivata", k, "n.d.")
            return
        sc = max(1.0, abs(ev(f, x0) or 0))
        if abs(d) > 2e-3 * sc:
            if k == 1:
                print("f'(x0) =", fr(d), "-> NON e' stazionario")
            elif k % 2 == 0:
                print("prima derivata non nulla: ordine %d, valore %s" % (k, fr(d)))
                print("=> %s LOCALE" % ("MINIMO" if d > 0 else "MASSIMO"))
            else:
                print("prima derivata non nulla: ordine %d, valore %s" % (k, fr(d)))
                print("=> NESSUN estremo (flesso a tg orizzontale)")
            fct = 1
            for j in range(2, k + 1):
                fct *= j
            print("f(x) - f(x0) ~ %s * (x-x0)^%d" % (ric(d / fct, 2e-3 * abs(d / fct)), k))
            return
    print("derivate fino a 5 nulle: serve ordine maggiore")

# ------------------------------------------------- polinomio di Taylor
def poli():
    f = mk(input("f(x)= "))
    x0 = leggi("centro x0", 0.0)
    n = int(leggi("ordine n (1..5)", 2.0))
    x = leggi("calcola in x", x0 + 0.1)
    cs = []
    fct = 1
    for k in range(0, n + 1):
        if k == 0:
            cs.append(ev(f, x0))
        else:
            fct *= k
            d = der(f, x0, k)
            cs.append(None if d is None else d / fct)
    print("coefficienti c_k=f^(k)(x0)/k!:")
    for k, c in enumerate(cs):
        print(" c%d = %s" % (k, "n.d." if c is None else ric(c, 1e-4)))
    if None in cs:
        return
    T = sum(cs[k] * (x - x0) ** k for k in range(n + 1))
    fx = ev(f, x)
    print("T_%d(%g) = %.8g" % (n, x, T))
    print("f(%g)   = %s" % (x, "n.d." if fx is None else "%.8g" % fx))
    if fx is not None:
        print("errore = %.3g" % abs(fx - T))
    print("(coefficienti da derivate numeriche: approssimati)")

# ----------------------------------------- funzioni notevoli + resto
def notevoli():
    print("1 exp  2 sen  3 cos  4 ln(1+x)  5 arctg  6 (1+x)^a")
    sc = int(num(input("funzione: ")))
    x = leggi("x", 0.1)
    n = int(leggi("ordine n (Maclaurin)", 2.0))
    T = 0.0
    if sc == 1:
        f = lambda t: exp(t)
        T = sum(x ** k / factorial(k) for k in range(n + 1))
        R = exp(max(x, 0.0)) * abs(x) ** (n + 1) / factorial(n + 1)
    elif sc == 2:
        f = lambda t: sin(t)
        T = sum((-1) ** k * x ** (2 * k + 1) / factorial(2 * k + 1) for k in range(n // 2 + 1) if 2 * k + 1 <= n)
        R = abs(x) ** (n + 1) / factorial(n + 1)
    elif sc == 3:
        f = lambda t: cos(t)
        T = sum((-1) ** k * x ** (2 * k) / factorial(2 * k) for k in range(n // 2 + 1) if 2 * k <= n)
        R = abs(x) ** (n + 1) / factorial(n + 1)
    elif sc == 4:
        f = lambda t: log(1 + t)
        T = sum((-1) ** (k + 1) * x ** k / k for k in range(1, n + 1))
        R = abs(x) ** (n + 1) / ((n + 1) * (1 + min(0.0, x)) ** (n + 1))
    elif sc == 5:
        f = lambda t: atan(t)
        T = sum((-1) ** k * x ** (2 * k + 1) / (2 * k + 1) for k in range(n // 2 + 1) if 2 * k + 1 <= n)
        R = None
    else:
        a = num(input("a: "))
        f = lambda t: (1 + t) ** a
        T = 0.0
        c = 1.0
        for k in range(n + 1):
            if k > 0:
                c = c * (a - k + 1) / k
            T += c * x ** k
        R = None
    print("T_%d(%g) = %.10g" % (n, x, T))
    print("f(%g)   = %.10g" % (x, f(x)))
    print("errore vero = %.3g" % abs(f(x) - T))
    if R is not None:
        print("resto Lagrange <= %.3g" % R)
        print("=> %.8g < f < %.8g (se resto>0)" % (T - R, T + R))

def tabella():
    righe = (
        "SVILUPPI di MACLAURIN",
        "e^x = 1+x+x^2/2+x^3/6+x^4/24",
        "sen x = x - x^3/6 + x^5/120",
        "cos x = 1 - x^2/2 + x^4/24",
        "ln(1+x) = x - x^2/2 + x^3/3",
        "arctg x = x - x^3/3 + x^5/5",
        "(1+x)^a = 1+ax+a(a-1)/2 x^2",
        "1/(1-x) = 1+x+x^2+x^3",
        "tg x = x + x^3/3 + 2x^5/15",
        "sqrt(1+x)=1+x/2-x^2/8+x^3/16",
        "ch x=1+x^2/2+x^4/24",
        "sh x=x+x^3/6+x^5/120",
        "(resto Peano: + o(x^n))",
        "LIMITI NOTEVOLI (x->0)",
        "sen x/x->1  (1-cos x)/x^2->1/2",
        "tg x/x->1  (e^x-1)/x->1",
        "ln(1+x)/x->1  ((1+x)^a-1)/x->a",
        "(1+1/n)^n->e  (1+x)^(1/x)->e",
        "a^x-1 ~ x ln a",
    )
    for r in righe:
        print(r)

def main():
    menu("TAYLOR / DERIVATE",
         ("1 derivate f',..,f(5) in x0",
          "2 classifica punto critico",
          "3 polinomio di Taylor T_n",
          "4 notevoli + resto Lagrange",
          "5 tabella sviluppi",
          "0 esci"),
         {1: derivate, 2: classifica, 3: poli, 4: notevoli, 5: tabella})

main()
