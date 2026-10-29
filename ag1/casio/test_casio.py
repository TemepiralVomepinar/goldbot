# Collaudo su PC (CPython) dei programmi per la Casio: python test_casio.py
# Esegue i programmi con input simulati e controlla i risultati dei temi d'esame.
import builtins
import contextlib
import io
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
ESITI = []


def carica(nome):
    src = open(os.path.join(QUI, nome)).read().rstrip()
    assert src.endswith("main()")
    ns = {"__name__": "casio_" + nome}
    exec(compile(src[:-len("main()")], nome, "exec"), ns)
    return ns


def esegui(fn, *inputs):
    it = iter(inputs)
    vecchio = builtins.input
    builtins.input = lambda p="": next(it)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn()
    finally:
        builtins.input = vecchio
    return buf.getvalue()


def ok(nome, testo, *attesi):
    mancanti = [a for a in attesi if a not in testo]
    ESITI.append(not mancanti)
    print(("OK   " if not mancanti else "FAIL ") + nome + ("" if not mancanti else "  mancano: %s\n%s" % (mancanti, testo)))


S = carica("studio.py")
esegui(S["setf"], "x*exp(-x)")
ok("studio x e^-x: max in 1", esegui(S["estremi"], "-3", "6"), "MAX x=1 f=0.367879")
ok("studio x e^-x: lim -oo = -inf", esegui(S["limiti"], "-oo"), "-inf")
ok("studio x e^-x: asintoto y=0", esegui(S["limiti"], "oo"), "asintoto orizzontale y= 0")
esegui(S["setf"], "sqrt(x^2-1)/(x-2)")
ok("studio sqrt(x^2-1)/(x-2): y=1 (+oo)", esegui(S["limiti"], "oo"), "L = 1", "asintoto orizzontale y= 1")
ok("studio sqrt(x^2-1)/(x-2): polo in 2", esegui(S["limiti"], "2"), "-inf", "+inf")
ok("studio sqrt(x^2-1)/(x-2): bordi -1,1,2", esegui(S["estremi"], "-5", "5"), "['-1', '1', '2']")
esegui(S["setf"], "exp(1/abs(x-1))*(x-1/4)")
ok("studio e^(1/|x-1|)(x-1/4): y=x+3/4", esegui(S["limiti"], "oo"), "y=x+3/4")
ok("studio e^(1/|x-1|)(x-1/4): y=x-5/4", esegui(S["limiti"], "-oo"), "y=x-5/4")
ok("studio e^(1/|x-1|)(x-1/4): min in 5/2", esegui(S["estremi"], "-3", "6"), "MIN x=5/2", "crescente in (5/2, 6)")
esegui(S["setf"], "atan(1/(1-x))-x/2")
t = esegui(S["estremi"], "-3", "6")
ok("studio arctg(1/(1-x))-x/2: min 0, max 2", t, "MIN x=0", "MAX x=2", "crescente in (0, 1)")
ok("studio arctg(1/(1-x))-x/2: asintoto y=-x/2", esegui(S["limiti"], "oo"), "y=-1/2*x")
esegui(S["setf"], "(x-1)^2*exp(-abs(x))")
ok("studio (x-1)^2 e^-|x|: angoloso in 0", esegui(S["nonderiv"], "0"), "PUNTO ANGOLOSO")
esegui(S["setf"], "abs(x)**(4/3)*cbrt(2-x)")
ok("studio x^(4/3) cbrt(2-x): max in 8/5", esegui(S["estremi"], "-3", "4"), "MAX x=8/5")
ok("studio: tg verticale in 2", esegui(S["nonderiv"], "2"), "TG VERTICALE")
esegui(S["setf"], "log(abs(x-1))+x**2+x")
ok("studio ln|x-1|+x^2+x: 3 zeri", esegui(S["soluzioni"], "-3", "3", "0"), "n. soluzioni: 3")

L = carica("limiti.py")
ok("limiti sin x/x = 1", esegui(L["lim_funzione"], "sin(x)/x", "0"), "limite dx : L = 1")
ok("limiti (1+2/x)^(3x) = e^6", esegui(L["lim_funzione"], "(1+2/x)**(3*x)", "oo"), "e^6")
ok("limiti ln(cos x)/(x sin 2x) = -1/4", esegui(L["lim_funzione"], "ln(cos(x))/(x*sin(2*x))", "0"), "-1/4")
ok("limiti (-1)^n n/(3n+2): non esiste", esegui(L["succ"], "(-1)**n*n/(3*n+2)", "1"), "NON esiste il limite")
ok("limiti (-1)^n(3n+2)/n^2 -> 0", esegui(L["succ"], "(-1)**n*(3*n+2)/n**2", "1"), "pari e dispari -> stesso valore")
ok("limiti sqrt(2+a) -> 2", esegui(L["ricorrenza"], "sqrt(2+a)", "sqrt(2)"), "punti fissi L=g(L): ['2', '2']")
ok("limiti ordine e^(2x^2)-cos 2x = 2", esegui(L["ordine"], "exp(2*x**2)-cos(2*x)", "0"), "p=2, c~4")
ok("limiti soglia sin x/(1-cos x)^a: 1/2", esegui(L["soglia"], "sin(x)", "1-cos(x)", "0"), "a < 1/2")
ok("limiti n^2(e^(a/n)-a/n-cos(1/n)) = 3: a=+-sqrt5",
   esegui(L["lim_par"], "x**2*(exp(a/x)-a/x-cos(1/x))", "oo", "3", "-6", "6"), "-sqrt(5)", "(=sqrt(5))")
ok("limiti (n!)^2/(2n)!: rapporto -> 1/4", esegui(L["rapporto"], "factorial(n)**2/factorial(2*n)"), "a_(n+1)/a_n=0.2520")

C = carica("compl.py")
ok("compl z^2=2i conj z: 4 soluzioni", esegui(C["equazione"], "z**2-2*i*conj(z)"), "soluzioni trovate: 4", "arg=5*pi/6")
ok("compl |z-1|=conj z-i: z=1-i", esegui(C["equazione"], "abs(z-1)-conj(z)+i"), "soluzioni trovate: 1", "1-1i")
ok("compl z^8=(2+i)^4: 8 soluzioni", esegui(C["equazione"], "z**8-(2+i)**4"), "soluzioni trovate: 8")
ok("compl |z|^2=z^3: 4 soluzioni", esegui(C["equazione"], "abs(z)**2-z**3"), "soluzioni trovate: 4")
ok("compl z^2(z^2+i)=0: 3 soluzioni", esegui(C["equazione"], "z**2*(z**2+i)"), "soluzioni trovate: 3")
ok("compl |z|^3 z=16i: z=2i", esegui(C["equazione"], "abs(z)**3*z-16*i"), "soluzioni trovate: 1", "0+2i")
ok("compl z^3=-8i: radici", esegui(C["radici"], "0", "-8", "3"), "1.73205-1i", "0+2i", "-1.73205-1i")
ok("compl (1+i)^10 = 32i", esegui(C["operazioni"], "1", "1", "^", "10"), "0+32i")
ok("compl z^2-(3+i)z+2+2i: 2 e 1+i", esegui(C["quadratica"], "1", "0", "-3", "-1", "2", "2"), "2+0i", "1+1i")
ok("compl forma -1+i", esegui(C["forma"], "-1", "1"), "3*pi/4", "sqrt(2)")
ok("compl regione 1<=|z|<=2, 0<=arg<=pi/3", esegui(C["regione"], "1<=abs(z)<=2 and 0<=arg(z)<=pi/3", "3", "1,1", ""), "APPARTIENE")
ok("compl regione |z-1|<1 contiene 0.5", esegui(C["regione"], "abs(z-1)<1", "3", "0.5,0", ""), "APPARTIENE")

E = carica("estremi.py")
ok("estremi n/(2n+1): sup 1/2 non max, min 1/3", esegui(E["estremi_succ"], "n/(2*n+1)", "1"), "SUP = 1/2  (limite, NON assunto", "INF = MIN = 1/3")
ok("estremi (-1)^n+1/n: max 3/2, inf -1", esegui(E["estremi_succ"], "(-1)**n+1/n", "1"), "SUP = MAX = 3/2", "INF = -1  (limite, NON assunto")
ok("estremi (-1)^n arctan n: +-pi/2", esegui(E["estremi_succ"], "(-1)**n*atan(n)", "1"), "SUP = pi/2", "INF = -pi/2")
ok("estremi x^2-2x-3<0 and |x|>=1: [1,3)", esegui(E["insieme"], "x**2-2*x-3<0 and abs(x)>=1", "-10", "10"), "[1 , 3)")
ok("estremi cos(pi/(x-1))+1=0: zeri di tocco", esegui(E["soluzioni"], "cos(pi/(x-1))+1", "1.1", "3"), "x = 2")
ok("estremi induzione 2^n>=n^2 falsa per n=3", esegui(E["induzione"], "2**n>=n**2", "1", "50"), "FALSA per n = [3]")
ok("estremi famiglia (1/n,2/n)", esegui(E["famiglia"], "1/n", "2/n", "1"), "UNIONE ~ da 0 a 2", "VUOTA", "MANCA")
ok("estremi max/min (x^2-1)e^-|x|", esegui(E["massimo_minimo"], "(x**2-1)*exp(-abs(x))", "-6", "6"), "MAX ~ 0.431843", "MIN ~ -1")

T = carica("taylor.py")
ok("taylor cos x-1+x^2/2: minimo (ordine 4)", esegui(T["classifica"], "cos(x)-1+x**2/2", "0"), "ordine 4", "MINIMO")
ok("taylor sen x-x+x^3/6: flesso (ordine 5)", esegui(T["classifica"], "sin(x)-x+x**3/6", "0"), "ordine 5", "NESSUN estremo")
ok("taylor x cos(pi x) in 1: c2=pi^2/2", esegui(T["poli"], "x*cos(pi*x)", "1", "2", "1.1"), "c2 = pi^2/2")
ok("taylor e^0.1 con T2 e resto", esegui(T["notevoli"], "1", "0.1", "2"), "T_2(0.1) = 1.105", "resto Lagrange <= 0.000184")

print("\nRIEPILOGO: %d/%d test superati" % (sum(ESITI), len(ESITI)))
sys.exit(0 if all(ESITI) else 1)
