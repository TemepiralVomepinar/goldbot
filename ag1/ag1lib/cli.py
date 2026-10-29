"""Interfaccia a riga di comando unificata."""
import argparse
import sys

import sympy as sp

from . import util
from .util import ESITI, parse, riga, x


def _esercizi_pdf(args):
    from . import esercizi_pdf as E
    scelti = args.esercizi or list(E.ESERCIZI)
    sbagliati = [i for i in scelti if i not in E.ESERCIZI]
    if sbagliati:
        sys.exit(f"esercizi inesistenti: {sbagliati} (1-40)")
    if args.lista:
        util.SOLO_TITOLO[0] = True
        for fn in E.ESERCIZI.values():
            try:
                fn()
            except util.FineTitolo:
                pass
        print("\n(usa i numeri come argomenti: python ag1_solver.py 14 25)")
        return 0
    import contextlib
    import io
    for i in scelti:
        if args.test:
            with contextlib.redirect_stdout(io.StringIO()):
                E.ESERCIZI[i]()
        else:
            E.ESERCIZI[i]()
    return _riepilogo("soluzioni del PDF")


def _riepilogo(cosa):
    tot = len(ESITI)
    ko = [(e, l) for e, l, ok in ESITI if not ok]
    print(f"\n{'=' * 74}\nRIEPILOGO: {tot - len(ko)}/{tot} risultati coincidono con le {cosa}")
    for e, l in ko:
        print(f"  NON coincide: es. {e}: {l}")
    return 1 if ko else 0


def _temi(args):
    from . import temi
    import contextlib
    import io
    if args.lista:
        for k_, v in temi.TEMI.items():
            print(f"{k_:28s} {v['descr']}")
        return 0
    scelti = args.nomi or list(temi.TEMI)
    for nome in scelti:
        if nome not in temi.TEMI:
            sys.exit(f"tema inesistente: {nome}. Usa 'temi --lista'.")
        if args.silenzioso:
            with contextlib.redirect_stdout(io.StringIO()):
                temi.TEMI[nome]["fn"]()
        else:
            temi.TEMI[nome]["fn"]()
    return _riepilogo("soluzioni dei temi d'esame")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(
        prog="ag1_solver.py",
        description="Risolutore di Analisi e Geometria 1: esercizi del PDF, temi d'esame e esercizi nuovi dello stesso tipo.",
        epilog="Esempi:  ag1_solver.py esercizi 14 25 | ag1_solver.py studio 'x*exp(-abs(x))' | "
               "ag1_solver.py geo posizione-rette '1,0,1;1,1,0' '0,1,1;1,0,1' | ag1_solver.py teoria fermat")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("esercizi", help="i 40 esercizi del PDF (con confronto)")
    s.add_argument("esercizi", nargs="*", type=int)
    s.add_argument("--test", action="store_true")
    s.add_argument("--lista", action="store_true")
    s.set_defaults(fn=_esercizi_pdf)

    s = sub.add_parser("temi", help="esercizi dei temi d'esame degli anni precedenti (con confronto)")
    s.add_argument("nomi", nargs="*")
    s.add_argument("--lista", action="store_true")
    s.add_argument("--silenzioso", action="store_true")
    s.set_defaults(fn=_temi)

    s = sub.add_parser("studio", help="studio completo di funzione (|.|, radici, tratti: 'Piecewise((e1, x<0), (e2, True))')")
    s.add_argument("expr")
    s.add_argument("--finestra", type=float, nargs=2, default=(-6, 6))
    s.add_argument("--breve", action="store_true", help="senza derivata seconda")

    s = sub.add_parser("limite", help="limite di funzione o successione")
    s.add_argument("expr")
    s.add_argument("--var", default="x")
    s.add_argument("--punto", default="0")
    s.add_argument("--dir", choices=["+", "-", "+-"], default=None)

    s = sub.add_parser("ordine", help="primo termine non nullo dello sviluppo di Taylor (ordine di infinitesimo)")
    s.add_argument("expr")
    s.add_argument("--punto", default="0")

    s = sub.add_parser("limite-param", help="limite con parametro: quando e' finito / quando vale V")
    s.add_argument("expr")
    s.add_argument("--param", default="a")
    s.add_argument("--var", default="x")
    s.add_argument("--punto", default="0")
    s.add_argument("--valore", default=None)

    s = sub.add_parser("limite-esp", help="lim N(x)/D(x)^a al variare dell'esponente a: limite-esp 'sin(x)' '1-cos(x)'")
    s.add_argument("num")
    s.add_argument("base")
    s.add_argument("--punto", default="0")

    s = sub.add_parser("estremi", help="massimo e minimo assoluti di f su [a,b]")
    s.add_argument("expr")
    s.add_argument("a")
    s.add_argument("b")

    s = sub.add_parser("successione", help="limite, monotonia, sup/inf/max/min di a_n")
    s.add_argument("expr")
    s.add_argument("--n0", type=int, default=1)

    s = sub.add_parser("ricorrenza", help="a_(n+1) = f(a_n) con a1 (usa 'a' per a_n)")
    s.add_argument("f")
    s.add_argument("a1")

    s = sub.add_parser("insieme", help="sup/inf/max/min di un insieme reale: 'x^2-2*x-3<0 and abs(x)>=1', 'cos(pi/(x-1)) = -1'")
    s.add_argument("cond")

    s = sub.add_parser("famiglia", help="unione/intersezione di intervalli I_n=(a_n,b_n)")
    s.add_argument("an")
    s.add_argument("bn")
    s.add_argument("--n0", type=int, default=1)
    s.add_argument("--chiuso-sx", action="store_true")
    s.add_argument("--chiuso-dx", action="store_true")

    s = sub.add_parser("raccordo", help="f=f1 per x<x0, f2 per x>=x0 con parametri: continuita'/derivabilita'")
    s.add_argument("f1")
    s.add_argument("f2")
    s.add_argument("--x0", default="0")
    s.add_argument("--param", nargs="+", default=["a"])

    s = sub.add_parser("derivata", help="derivata (anche di ordine superiore) semplificata")
    s.add_argument("expr")
    s.add_argument("--ordine", type=int, default=1)

    s = sub.add_parser("taylor", help="sviluppo di Taylor/Maclaurin")
    s.add_argument("expr")
    s.add_argument("--ordine", type=int, default=3)
    s.add_argument("--punto", default="0")

    s = sub.add_parser("asintoti", help="asintoti di una funzione")
    s.add_argument("expr")

    s = sub.add_parser("complesso", help="forme di un numero complesso: modulo, argomento, Re, Im")
    s.add_argument("expr")
    s = sub.add_parser("eq-complessa", help="equazione in C: 'z^3 = 8*i', 'abs(z-1) = conj(z) - i' (piu' eq con ';')")
    s.add_argument("eq")
    s = sub.add_parser("radici", help="radici n-esime di un numero complesso")
    s.add_argument("w")
    s.add_argument("n", type=int)
    s = sub.add_parser("regione", help="regione del piano di Gauss: 'abs(z+1)<abs(z-1)', '1<=abs(z)<=2 and 0<=arg(z)<=pi/3'")
    s.add_argument("cond")
    s.add_argument("--R", type=float, default=4.0)
    s.add_argument("--arg-0-2pi", action="store_true", help="arg in [0,2pi) invece di (-pi,pi]")
    s.add_argument("--punti", nargs="*", default=[])

    s = sub.add_parser("integrale", help="integrale indefinito/definito/improprio: integrale 'expr' [a b]")
    s.add_argument("expr")
    s.add_argument("a", nargs="?")
    s.add_argument("b", nargs="?")
    s = sub.add_parser("conv-param", help="per quali valori del parametro converge l'integrale improprio")
    s.add_argument("expr")
    s.add_argument("a")
    s.add_argument("b")
    s.add_argument("--param", default="a")
    s = sub.add_parser("area", help="area fra due curve su [a,b]")
    s.add_argument("f1")
    s.add_argument("f2")
    s.add_argument("a")
    s.add_argument("b")
    s = sub.add_parser("funzione-integrale", help="G(x)=int_u(x)^v(x) f(t) dt: G'(x)")
    s.add_argument("f")
    s.add_argument("u")
    s.add_argument("v")
    s = sub.add_parser("edo", help="equazione differenziale: edo \"y' = y + x\" [--x0 0 --y0 0]")
    s.add_argument("eq")
    s.add_argument("--x0", default=None)
    s.add_argument("--y0", default=None)

    s = sub.add_parser("curva", help="curva r(t): regolarita', lunghezza, chiusa, piana: curva 'cos(t),sin(t),t' 0 pi")
    s.add_argument("r")
    s.add_argument("t0")
    s.add_argument("t1")
    s = sub.add_parser("semplice", help="autointersezioni di una curva (curva non semplice)")
    s.add_argument("r")
    s.add_argument("t0")
    s.add_argument("t1")
    s = sub.add_parser("osculatore", help="piano per r(t0) contenente r'(t0) e r''(t0)")
    s.add_argument("r")
    s.add_argument("t0")
    s = sub.add_parser("tangente", help="retta tangente a una curva in t0")
    s.add_argument("r")
    s.add_argument("t0")
    s = sub.add_parser("linea", help="integrale di linea di f(x,y,z) lungo r(t): linea 'cos(t),sin(t)' 'x^2*y' 0 pi")
    s.add_argument("r")
    s.add_argument("f")
    s.add_argument("t0")
    s.add_argument("t1")

    s = sub.add_parser("geo", help="geometria in R^3 (vedi `geo --help`)")
    s.add_argument("op")
    s.add_argument("args", nargs="*")
    s.add_argument("--angolo", default=None, help="valore dell'angolo per trovare il parametro (es. pi/3)")

    s = sub.add_parser("teoria", help="enunciati e dimostrazioni (senza argomento: elenco)")
    s.add_argument("argomento", nargs="*")

    # compatibilita' con la vecchia sintassi: `ag1_solver.py 14 25`, `ag1_solver.py --test`
    if argv and all(t_.isdigit() or t_ in ("--test", "--lista") for t_ in argv):
        ns = argparse.Namespace(esercizi=[int(t_) for t_ in argv if t_.isdigit()],
                                test="--test" in argv, lista="--lista" in argv)
        return _esercizi_pdf(ns)
    a = p.parse_args(argv)
    if a.cmd is None:
        p.print_help()
        return 0
    if hasattr(a, "fn"):
        return a.fn(a)
    return _esegui(a)


def _esegui(a):
    from . import complessi as C
    from . import funzioni as F
    from . import geometria as G
    from . import integrali as I_
    from . import successioni as S
    from .teoria import teoria

    c = a.cmd
    if c == "studio":
        F.studio_funzione(parse(a.expr, Piecewise=sp.Piecewise), x, png="studio.png", finestra=tuple(a.finestra),
                          completo=not a.breve)
    elif c == "limite":
        S.limite(a.expr, a.var, a.punto, a.dir)
    elif c == "limite-esp":
        S.limite_esponente(a.num, a.base, a.punto)
    elif c == "estremi":
        F.estremi_assoluti(parse(a.expr), parse(a.a), parse(a.b))
    elif c == "ordine":
        p_, c_ = S.ordine_infinitesimo(a.expr, x, parse(a.punto))
        riga(f"primo termine non nullo: {c_}*(x - {a.punto})^{p_}   (ordine {p_}, coefficiente {c_})")
        riga(f"=> {a.expr} ~ {c_}*(x-{a.punto})^{p_}: lim (expr)/(x-{a.punto})^q e' finito e non nullo solo per q = {p_}")
    elif c == "limite-param":
        S.limite_parametro(a.expr, a.param, a.var, a.punto, a.valore)
    elif c == "successione":
        S.successione(a.expr, a.n0)
    elif c == "ricorrenza":
        S.ricorrenza(a.f, a.a1)
    elif c == "insieme":
        S.estremi_insieme(S.insieme_reale(a.cond))
    elif c == "famiglia":
        r = S.famiglia_intervalli(a.an, a.bn, a.n0, not a.chiuso_sx, not a.chiuso_dx)
        riga("UNIONE di tutti gli intervalli:", r["unione"])
        riga("INTERSEZIONE di tutti gli intervalli:", r["intersezione"])
    elif c == "raccordo":
        S.raccordo(a.f1, a.f2, a.x0, a.param)
    elif c == "derivata":
        riga(sp.simplify(sp.diff(parse(a.expr), x, a.ordine)))
    elif c == "taylor":
        riga(sp.series(parse(a.expr), x, parse(a.punto), a.ordine + 1))
    elif c == "asintoti":
        F.asintoti(parse(a.expr), x)
    elif c == "complesso":
        C.analizza(C.parse_c(a.expr))
    elif c == "eq-complessa":
        C.risolvi_equazione(a.eq)
    elif c == "radici":
        C.stampa_radici(C.parse_c(a.w), a.n)
    elif c == "regione":
        C.stampa_regione(a.cond, a.R, a.arg_0_2pi, a.punti)
    elif c == "integrale":
        I_.integrale(a.expr, a.a, a.b)
    elif c == "conv-param":
        I_.convergenza_parametro(a.expr, a.a, a.b, a.param)
    elif c == "area":
        I_.area_tra_curve(a.f1, a.f2, a.a, a.b)
    elif c == "funzione-integrale":
        I_.funzione_integrale(a.f, a.u, a.v)
    elif c == "edo":
        I_.edo(a.eq, parse(a.x0) if a.x0 is not None else None, parse(a.y0) if a.y0 is not None else None)
    elif c == "curva":
        I_.curva(a.r, a.t0, a.t1)
    elif c == "semplice":
        I_.autointersezioni(a.r, a.t0, a.t1)
    elif c == "osculatore":
        I_.piano_osculatore(a.r, a.t0)
    elif c == "tangente":
        I_.retta_tangente_curva(a.r, a.t0)
    elif c == "linea":
        I_.integrale_di_linea(a.r, a.f, a.t0, a.t1)
    elif c == "geo":
        return _geo(a, G)
    elif c == "teoria":
        teoria(" ".join(a.argomento) if a.argomento else None)
    return 0


GEO_AIUTO = """operazioni geo (punti/vettori come 'x,y,z'; retta come 'P;d' = punto;direzione; piano come equazione '2*x+y-2*z=-5';
i parametri (a, alpha, t...) sono ammessi ovunque):
  retta-punti P Q                    retta per due punti
  retta-piani EQ1 EQ2                retta intersezione di due piani
  piano-punti P Q R                  piano per tre punti
  piano-normale P n                  piano per P ortogonale a n
  piano-retta-punto 'P;d' R          piano contenente la retta e il punto
  piano-due-rette 'P1;d1' 'P2;d2'    piano contenente due rette (incidenti/parallele)
  piano-punti-parallelo P Q d        piano per P e Q parallelo alla direzione d
  retta-perp-incidente P 'P0;d'      retta per P ortogonale e incidente alla retta data
  retta-ortogonale P EQ              retta per P ortogonale al piano
  posizione-rette 'P1;d1' 'P2;d2'    incidenti/parallele/sghembe (+ intersezione, distanza, angolo)
  dist-punto-piano P EQ              distanza e proiezione ortogonale
  dist-punto-retta P 'P0;d'          distanza e piede della perpendicolare
  dist-piani EQ1 EQ2                 distanza fra piani paralleli
  angolo u v [--angolo pi/3]         angolo fra vettori (e valore del parametro per cui vale --angolo)
  angolo-retta-piano d EQ   |  angolo-piani EQ1 EQ2
  area-triangolo P Q R   |  misto u v w (complanarita', volume)   |  prodotti u v
  ortogonali u v [w]  |  paralleli u v  |  complanari u v w      (valori dei parametri)
  parallelo-piano v EQ               valori per cui il vettore e' parallelo al piano
  appartiene P EQ                    valori per cui il punto sta nel piano"""


def _geo(a, G):
    op, ar = a.op, a.args
    rd = lambda s_: s_.split(";")
    if op in ("aiuto", "help"):
        print(GEO_AIUTO)
    elif op == "retta-punti":
        G.retta_per_punti(*ar)
    elif op == "retta-piani":
        G.retta_da_piani(*ar)
    elif op == "piano-punti":
        G.piano_tre_punti(*ar)
    elif op == "piano-normale":
        G.piano_punto_normale(*ar)
    elif op == "piano-retta-punto":
        G.piano_retta_punto(*rd(ar[0]), ar[1])
    elif op == "piano-due-rette":
        G.piano_due_rette(*rd(ar[0]), *rd(ar[1]))
    elif op == "piano-punti-parallelo":
        G.piano_punti_parallelo(*ar)
    elif op == "retta-perp-incidente":
        G.retta_perp_incidente(ar[0], *rd(ar[1]))
    elif op == "retta-ortogonale":
        G.retta_ortogonale_piano(*ar)
    elif op == "posizione-rette":
        G.posizione_rette(*rd(ar[0]), *rd(ar[1]))
    elif op == "dist-punto-piano":
        G.distanza_punto_piano(*ar)
    elif op == "dist-punto-retta":
        G.distanza_punto_retta(ar[0], *rd(ar[1]))
    elif op == "dist-piani":
        G.distanza_piani(*ar)
    elif op == "angolo":
        G.angolo_vettori(ar[0], ar[1], uguale_a=a.angolo)
    elif op == "angolo-retta-piano":
        G.angolo_retta_piano(*ar)
    elif op == "angolo-piani":
        G.angolo_piani(*ar)
    elif op == "area-triangolo":
        G.area_triangolo(*ar)
    elif op == "misto":
        G.prodotto_misto(*ar)
    elif op == "prodotti":
        G.prodotti(*ar)
    elif op in ("ortogonali", "paralleli", "complanari"):
        G.condizioni(op, ar)
    elif op == "parallelo-piano":
        G.vettore_parallelo_piano(*ar)
    elif op == "appartiene":
        G.appartenenza(*ar)
    else:
        print(GEO_AIUTO)
        return 1
    return 0
