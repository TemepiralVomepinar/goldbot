# COMPL.PY - Numeri complessi (Casio fx-CG50)
# forma/modulo/argomento, De Moivre, radici n-esime, equazioni anche con
# conj(z), abs(z), re(z), im(z); regioni del piano di Gauss (mappa a caratteri).
# Nelle espressioni: z = variabile, i = unita' immaginaria.
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

# ------------------------------------------------ numeri complessi (classe C)
class C:
    def __init__(self, a=0.0, b=0.0):
        self.a = float(a)
        self.b = float(b)

    def __add__(s, o):
        o = cv(o)
        return C(s.a + o.a, s.b + o.b)

    def __radd__(s, o):
        return s.__add__(o)

    def __sub__(s, o):
        o = cv(o)
        return C(s.a - o.a, s.b - o.b)

    def __rsub__(s, o):
        return cv(o).__sub__(s)

    def __mul__(s, o):
        o = cv(o)
        return C(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)

    def __rmul__(s, o):
        return s.__mul__(o)

    def __truediv__(s, o):
        o = cv(o)
        d = o.a * o.a + o.b * o.b
        return C((s.a * o.a + s.b * o.b) / d, (s.b * o.a - s.a * o.b) / d)

    def __rtruediv__(s, o):
        return cv(o).__truediv__(s)

    def __neg__(s):
        return C(-s.a, -s.b)

    def __lt__(s, o):
        return s.a < cv(o).a

    def __le__(s, o):
        return s.a <= cv(o).a

    def __gt__(s, o):
        return s.a > cv(o).a

    def __ge__(s, o):
        return s.a >= cv(o).a

    def __eq__(s, o):
        o = cv(o)
        return abs(s.a - o.a) < 1e-9 and abs(s.b - o.b) < 1e-9

    def __abs__(s):
        return sqrt(s.a * s.a + s.b * s.b)

    def __pow__(s, n):
        if isinstance(n, C):
            n = n.a
            if n == int(n):
                n = int(n)
        if isinstance(n, int):
            if n < 0:
                return C(1, 0).__truediv__(s.__pow__(-n))
            r = C(1, 0)
            for _ in range(n):
                r = r.__mul__(s)
            return r
        if isinstance(n, C):
            n = n.a
        if n == int(n):
            return s.__pow__(int(n))
        r, t = abs(s), atan2(s.b, s.a)
        n = float(n)
        return C(r ** n * cos(n * t), r ** n * sin(n * t))

def cv(o):
    return o if isinstance(o, C) else C(o, 0)

i = C(0, 1)

def conj(z):
    z = cv(z)
    return C(z.a, -z.b)

def re(z):
    return cv(z).a

def im(z):
    return cv(z).b

def arg(z):
    z = cv(z)
    return atan2(z.b, z.a)

_exp0, _sqrt0, _log0 = exp, sqrt, log

def exp(z):
    if isinstance(z, C):
        return C(_exp0(z.a) * cos(z.b), _exp0(z.a) * sin(z.b))
    return _exp0(z)

def sqrt(z):
    if isinstance(z, C):
        r, t = abs(z), atan2(z.b, z.a)
        return C(_sqrt0(r) * cos(t / 2), _sqrt0(r) * sin(t / 2))
    if z < 0:
        return C(0, _sqrt0(-z))
    return _sqrt0(z)

def log(z):
    if isinstance(z, C):
        return C(_log0(abs(z)), atan2(z.b, z.a))
    return _log0(z)

def cabs(z):
    return C(abs(cv(z)), 0)

def cre(z):
    return C(cv(z).a, 0)

def cim(z):
    return C(cv(z).b, 0)

def carg(z):
    z = cv(z)
    return C(atan2(z.b, z.a), 0)

def carg2(z):
    z = cv(z)
    t = atan2(z.b, z.a)
    return C(t if t >= 0 else t + 2 * pi, 0)

FN = {"abs": "cabs", "re": "cre", "im": "cim", "arg": "carg", "arg2": "carg2"}

def kwrap(s):
    # numeri e costanti diventano oggetti C (cosi' non servono operazioni 'riflesse')
    out = ""
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch.isdigit() or (ch == "." and i + 1 < n and s[i + 1].isdigit()):
            j = i
            while j < n and (s[j].isdigit() or s[j] == "."):
                j += 1
            if j + 1 < n and s[j] in "eE" and (s[j + 1].isdigit() or (s[j + 1] in "+-" and j + 2 < n and s[j + 2].isdigit())):
                j += 2
                while j < n and s[j].isdigit():
                    j += 1
            out += "C(" + s[i:j] + ")"
            i = j
        elif ch.isalpha() or ch == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            w = s[i:j]
            if w == "pi" or w == "e":
                out += "C(" + w + ")"
            elif w in FN:
                out += FN[w]
            else:
                out += w
            i = j
        else:
            out += ch
            i += 1
    return out

def cs(z, d=6):
    z = cv(z)
    a = 0.0 if abs(z.a) < 1e-12 else z.a
    b = 0.0 if abs(z.b) < 1e-12 else z.b
    return ("%." + str(d) + "g%+." + str(d) + "gi") % (a, b)

def pol(z):
    z = cv(z)
    r = abs(z)
    t = atan2(z.b, z.a)
    return r, t

def dai_numeri():
    a = num(input("Re = "))
    b = num(input("Im = "))
    return C(a, b)

def forma():
    z = dai_numeri()
    r, t = pol(z)
    print("z =", cs(z))
    print("|z| = %s" % fr(r))
    print("Arg in (-pi,pi] = %s" % fr(t))
    t2 = t if t >= 0 else t + 2 * pi
    print("arg in [0,2pi) = %s" % fr(t2))
    print("z = %s * e^(i*(%s))" % (ric(r, 1e-6), ric(t, 1e-6)))
    print("coniugato:", cs(conj(z)), "  1/z:", cs(cv(1) / z))

def operazioni():
    print("z1:")
    z1 = dai_numeri()
    op = input("operazione (+ - * / ^): ").strip()
    if op == "^":
        n = int(num(input("n intero: ")))
        r = z1 ** n
        print("z1^n =", cs(r))
        rr, tt = pol(z1)
        print("De Moivre: |z|^n=%s, arg=n*theta=%s" % (ric(rr ** n, 1e-6), ric(n * tt, 1e-6)))
        return
    print("z2:")
    z2 = dai_numeri()
    if op == "+":
        r = z1 + z2
    elif op == "-":
        r = z1 - z2
    elif op == "*":
        r = z1 * z2
    else:
        r = z1 / z2
    print("risultato:", cs(r))
    rr, tt = pol(r)
    print("|.|=%s Arg=%s" % (fr(rr), fr(tt)))

def radici():
    print("w:")
    w = dai_numeri()
    n = int(num(input("n (z^n=w): ")))
    r, t = pol(w)
    rho = r ** (1.0 / n)
    print("|w|=%s arg w=%s -> %d radici" % (fr(r), fr(t), n))
    print("raggio %s, angoli (arg w + 2k*pi)/n" % fr(rho))
    for k in range(n):
        th = (t + 2 * pi * k) / n
        z = C(rho * cos(th), rho * sin(th))
        print("k=%d: %s" % (k, cs(z)))
        print("   = %s * e^(i*%s)" % (ric(rho, 1e-6), ric(th, 1e-6)))

def quadratica():
    print("az^2+bz+c=0, coefficienti complessi")
    print("a:")
    A = dai_numeri()
    print("b:")
    B = dai_numeri()
    print("c:")
    Cc = dai_numeri()
    D = B * B - A * Cc * 4
    print("Delta =", cs(D))
    s = sqrt(D)
    z1 = (-B + s) / (A * 2)
    z2 = (-B - s) / (A * 2)
    print("z1 =", cs(z1))
    print("z2 =", cs(z2))
    print("verifica:", cs(A * z1 * z1 + B * z1 + Cc))

def equazione():
    print("Equazione E(z)=0 in z. Usa:")
    print("z, i, conj(z), abs(z), re(z), im(z), exp(z)")
    print("es: z**2-2*i*conj(z)   abs(z-1)-conj(z)+i")
    print("(per A=B scrivi A-B)")
    s = input("E(z)= ")
    E = eval("lambda z:" + kwrap(conv(s)))

    def Fv(a, b):
        w = cv(E(C(a, b)))
        return w.a, w.b
    sol = []
    for ia in range(-4, 5):
        for ib in range(-4, 5):
            a, b = ia * 0.9 + 0.13, ib * 0.9 - 0.11
            for _ in range(60):
                try:
                    f1, f2 = Fv(a, b)
                    h = 1e-7
                    fa1, fa2 = Fv(a + h, b)
                    fb1, fb2 = Fv(a, b + h)
                except:
                    break
                j11, j21 = (fa1 - f1) / h, (fa2 - f2) / h
                j12, j22 = (fb1 - f1) / h, (fb2 - f2) / h
                det = j11 * j22 - j12 * j21
                if abs(det) < 1e-14:
                    break
                da = (-f1 * j22 + f2 * j12) / det
                db = (-f2 * j11 + f1 * j21) / det
                a, b = a + da, b + db
                if abs(da) + abs(db) < 1e-13:
                    break
            try:
                f1, f2 = Fv(a, b)
            except:
                continue
            if abs(f1) + abs(f2) < 1e-8 and abs(a) < 1e3 and abs(b) < 1e3:
                if abs(a) < 3e-4 and abs(b) < 3e-4:
                    a, b = 0.0, 0.0      # radice multipla in 0: Newton converge piano
                if not any(abs(a - p) + abs(b - q) < 2e-3 for p, q in sol):
                    sol.append((a, b))
    sol.sort()
    print("soluzioni trovate:", len(sol))
    for a, b in sol:
        z = C(a, b)
        r, t = pol(z)
        print(cs(z), "  |z|=%s arg=%s" % (ric(r, 1e-6), ric(t, 1e-6)))
    print("(se ci sono infinite soluzioni: usa 'regione')")

def regione():
    print("Condizione su z (True/False), es:")
    print("abs(z+1)<abs(z-1)")
    print("1<=abs(z)<=2 and 0<=arg(z)<=pi/3")
    print("re(z**2)>0   arg: (-pi,pi]")
    print("arg2(z): in [0,2pi)")
    s = input("cond= ")
    P = eval("lambda z:" + kwrap(conv(s)))
    R = leggi("raggio finestra", 3.0)
    W, H = 31, 15
    print("finestra [-%g,%g]^2 ('#' = nella regione)" % (R, R))
    for r in range(H):
        y = R - 2 * R * r / (H - 1.0)
        riga = ""
        for c in range(W):
            x = -R + 2 * R * c / (W - 1.0)
            try:
                ok = P(C(x, y))
            except:
                ok = False
            if ok:
                riga += "#"
            elif abs(y) < R / (H - 1.0):
                riga += "-"
            elif abs(x) < R / (W - 1.0):
                riga += "|"
            else:
                riga += "."
        print(riga)
    while True:
        t = input("punto da testare 'a,b' (invio=fine): ").strip()
        if t == "":
            break
        a, b = t.split(",")
        z = C(num(a), num(b))
        print(cs(z), "APPARTIENE" if P(z) else "NON appartiene")

def main():
    menu("NUMERI COMPLESSI",
         ("1 forma: |z|, arg, exp",
          "2 operazioni, potenze",
          "3 radici n-esime z^n=w",
          "4 az^2+bz+c=0",
          "5 equazione in z, conj, |z|",
          "6 regione piano di Gauss",
          "0 esci"),
         {1: forma, 2: operazioni, 3: radici, 4: quadratica, 5: equazione, 6: regione})

main()
