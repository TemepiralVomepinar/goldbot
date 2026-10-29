# TEORIA.PY - Formulario AG1: derivate, limiti, studio di funzione, complessi,
# teoremi, Taylor, integrali, EDO, curve e geometria, sup/inf (Casio fx-CG50)

# Formulario e teoria per AG1 (testo senza accenti, per lo schermo piccolo)
PAGINE = {}

PAGINE["1 derivate"] = """DERIVATE
(x^a)'=a x^(a-1)
(e^x)'=e^x  (a^x)'=a^x ln a
(ln x)'=1/x  (log_a x)'=1/(x ln a)
(sen x)'=cos x  (cos x)'=-sen x
(tg x)'=1+tg^2 x = 1/cos^2 x
(arctg x)'=1/(1+x^2)
(arcsen x)'=1/sqrt(1-x^2)
(arccos x)'=-1/sqrt(1-x^2)
(sh x)'=ch x  (ch x)'=sh x
(|x|)'=sgn x  (x!=0)
(fg)'=f'g+fg'
(f/g)'=(f'g-fg')/g^2
(f(g))'=f'(g)*g'
(f^-1)'(y)=1/f'(x), y=f(x)
f^g = e^(g ln f)
Retta tangente in x0:
y=f(x0)+f'(x0)(x-x0)"""

PAGINE["2 limiti"] = """LIMITI NOTEVOLI (x->0)
sen x / x -> 1
tg x / x -> 1
(1-cos x)/x^2 -> 1/2
(e^x - 1)/x -> 1
ln(1+x)/x -> 1
((1+x)^a - 1)/x -> a
(a^x - 1)/x -> ln a
arctg x / x -> 1
(1+x)^(1/x) -> e
(1+1/n)^n -> e
(1+a/n)^n -> e^a
ASINTOTICI (x->0, u->0):
sen u ~ u ; tg u ~ u
1-cos u ~ u^2/2
e^u-1 ~ u ; ln(1+u) ~ u
(1+u)^a-1 ~ a u
a^u-1 ~ u ln a
MAI sostituire nelle somme!
Forme: 0/0 oo/oo 0*oo oo-oo
1^oo 0^0 oo^0: e^(g ln f)"""

PAGINE["3 infiniti"] = """GERARCHIA INFINITI
(ln n)^b << n^a << c^n
<< n! << n^n   (c>1,a,b>0)
sqrt[n](n)->1  sqrt[n](n!)->oo
n^a/c^n->0 ; c^n/n!->0
CRITERI successioni a_n>0
a(n+1)/a_n -> l  oppure
radice n-esima di a_n -> l:
 l<1 => a_n->0
 l>1 => a_n->+oo
 l=1 => non si sa
CONFRONTO (carabinieri):
a<=b<=c, a,c->L => b->L
Limitata*infinitesima->0
Monotona => ha limite
Crescente limitata => converge
a_n~b_n se a_n/b_n->1
(~ solo in prodotti/quozienti)
x^x -> 1 (x->0+)
x ln x -> 0 (x->0+)
ln x / x^a -> 0 (x->oo)"""

PAGINE["4 studio f"] = """STUDIO DI FUNZIONE
1 DOMINIO: den!=0, radici
  pari>=0, ln>0, arcsen
  in [-1,1], abs
2 simmetrie: pari/dispari
3 zeri e segno
4 LIMITI al bordo e
  ASINTOTI:
  verticali: lim=oo in x0
  orizz: lim x->oo f = L
  obliqui: m=lim f/x,
  q=lim (f-mx) (finiti)
5 f' e suo dominio
  non derivabilita':
  angoloso (f'- != f'+)
  cuspide (+oo/-oo)
  tg verticale: f'->oo
  stesso segno = flesso
6 MONOTONIA: segno f'
  f'=0 : punti critici
  max/min locali
7 f'': convessa f''>0
  flessi: f'' cambia segno
8 IMMAGINE: estremi,
  limiti, Weierstrass+
  valori intermedi
9 n. zeri: monotonia +
  teorema degli zeri
10 GRAFICO coerente"""

PAGINE["5 complessi"] = """NUMERI COMPLESSI
z=a+ib  |z|=sqrt(a^2+b^2)
conj z=a-ib  z*conj z=|z|^2
1/z = conj z/|z|^2
z=r(cos t+i sen t)=r e^(it)
arg: t=arctg(b/a) se a>0
 a<0: +pi ; a=0: +-pi/2
(disegna il punto!)
z1 z2: r1 r2, t1+t2
z1/z2: r1/r2, t1-t2
DE MOIVRE: z^n=r^n e^(int)
RADICI z^n=w=R e^(ip):
 z_k=R^(1/n) e^(i(p+2k pi)/n)
 k=0..n-1 (n punti, poligono
 regolare)
Equazioni: z=x+iy oppure
modulo e argomento:
 r^a=..., a t=... +2k pi
Re z=(z+conj z)/2
Im z=(z-conj z)/(2i)
|z+w|<=|z|+|w|
|z-z0|<r : disco
|z-a|=|z-b| : asse segm.
Re z>0 : semipiano"""

PAGINE["6 teoremi"] = """TEOREMI (f su [a,b])
WEIERSTRASS: f continua su
[a,b] => ha max e min
ZERI: f continua,
f(a)f(b)<0 => esiste c con
f(c)=0
VALORI INTERMEDI: f continua
assume ogni valore fra
f(a) e f(b)
FERMAT: x0 estremo locale,
f derivabile in x0 =>
f'(x0)=0 (non viceversa:
x^3 ; serve derivabile:|x|)
ROLLE: f(a)=f(b) =>
esiste c: f'(c)=0
LAGRANGE: esiste c:
f(b)-f(a)=f'(c)(b-a)
=> f'>=0 crescente
CAUCHY: (f(b)-f(a))/(g(b)-g(a))
=f'(c)/g'(c)
DE L'HOPITAL: 0/0 o oo/oo,
se esiste lim f'/g' allora
lim f/g = lim f'/g'
derivabile => continua
Unicita' del limite
Permanenza del segno"""

PAGINE["7 taylor"] = """TAYLOR (centro x0)
f(x)=sum f^(k)(x0)/k! (x-x0)^k
 + o((x-x0)^n)  [Peano]
Resto di Lagrange:
R_n=f^(n+1)(xi)/(n+1)!
 *(x-x0)^(n+1), xi fra x0,x
MACLAURIN (x0=0):
e^x=1+x+x^2/2+x^3/6+..
sen x=x-x^3/6+x^5/120
cos x=1-x^2/2+x^4/24
ln(1+x)=x-x^2/2+x^3/3
arctg x=x-x^3/3+x^5/5
(1+x)^a=1+ax+a(a-1)x^2/2
1/(1-x)=1+x+x^2+..
CLASSIFICARE x0 critico:
primo termine non nullo
c(x-x0)^k:
 k pari: c>0 min, c<0 max
 k dispari: nessun estremo"""

PAGINE["8 integrali"] = """INTEGRALI
int x^a=x^(a+1)/(a+1)
int 1/x=ln|x|
int e^x=e^x ; int a^x=a^x/ln a
int sen=-cos ; int cos=sen
int 1/cos^2=tg x
int 1/(1+x^2)=arctg x
int 1/sqrt(1-x^2)=arcsen x
Per parti:
int f g'=fg-int f' g
Sostituzione: t=g(x)
Razionali: frazioni
 semplici; x^2+bx+c:
 completa il quadrato
Teor. FONDAMENTALE:
F(x)=int_a^x f => F'=f
int_a^b f=G(b)-G(a)
(int_u(x)^v(x) f)'=
 f(v)v'-f(u)u'
MEDIA: esiste c:
 media=f(c)
IMPROPRI:
int_1^oo 1/x^p conv sse p>1
int_0^1 1/x^p conv sse p<1
confronto/asintotico f~g
e^(-ax) all'inf: a>0
Area fra curve: int|f-g|"""

PAGINE["9 edo"] = """EQUAZIONI DIFFERENZIALI
LINEARE 1o ordine:
y'+a(x)y=b(x)
A=primitiva di a
y=e^(-A) (C + int b e^A)
SEPARABILI: y'=g(x)h(y)
 int dy/h(y)=int g dx
 (y con h(y)=0: costanti)
Cauchy y(x0)=y0: fissa C
Es: y'=4x^3 y, y(1)=-1:
 y=-e^(x^4-1)
y'=y+x, y(0)=0:
 y=e^x-x-1
Comportamento in x0: y'(x0)
dall'equazione; y'' derivando
 (min se y''>0)
2o ordine a coeff costanti:
 y''+py'+qy=0: radici di
 l^2+pl+q=0 :
 reali l1,l2: C1e^(l1x)+C2e^(l2x)
 doppia: (C1+C2x)e^(lx)
 complesse a+-ib:
 e^(ax)(C1cos bx+C2sen bx)"""

PAGINE["A curve/geom"] = """CURVE r(t), t in [a,b]
regolare: r'(t)!=0
semplice: r iniettiva
chiusa: r(a)=r(b)
piana: det[r',r'',r''']=0
retta tg: r(t0)+s r'(t0)
lunghezza = int |r'| dt
int_gamma f ds =
 int f(r(t)) |r'(t)| dt
GEOMETRIA R^3
u.v=|u||v|cos t
u x v: area parallelogr.
piano ax+by+cz=d,
 normale n=(a,b,c)
piano per 3 punti:
 n=PQ x PR
retta: P+t d
d(P,piano)=|n.P-d|/|n|
d(P,retta)=|(P-P0)xd|/|d|
d(r,s sghembe)=
 |(P2-P1).(d1xd2)|/|d1xd2|
r,s: d1xd2=0 parallele;
 (P2-P1).(d1xd2)=0
 incidenti; altrimenti
 sghembe
volume=|u.(v x w)|
u,v,w complanari <=> =0"""

PAGINE["B insiemi"] = """SUP / INF / INDUZIONE
sup A=minimo dei
maggioranti; inf A=
massimo dei minoranti
L=sup A <=> (i) a<=L per
ogni a (ii) per ogni e>0
esiste a>L-e
sup in A => max
Completezza di R: A non
vuoto, limitato sup. =>
esiste sup
Esempi:
n/(2n+1): sup 1/2 non max
 min=1/3 (n=1)
(-1)^n+1/n: max 3/2,
 inf -1 non min
1/n+1/m: max 2, inf 0
INDUZIONE: base P(n0) e
passo P(n)=>P(n+1)
sqrt2 irrazionale: p^2=2q^2
 => p,q pari: assurdo
Bernoulli (1+x)^n>=1+nx
 x>=-1
2^n>=n^2 per n>=4
Funzioni: iniettiva,
 monotona, inversa
 simmetrica rispetto a y=x
 ln=inv(e^x), arctg:R->(-pi/2,pi/2)"""

def stampa(chiave):
    righe = PAGINE[chiave].split("\n")
    i = 0
    while i < len(righe):
        for r in righe[i:i + 11]:
            print(r)
        i += 11
        if i < len(righe):
            input("[EXE] segue")

def main():
    chiavi = sorted(PAGINE.keys())
    while True:
        print("FORMULARIO AG1")
        for k in chiavi:
            print(k)
        s = input("lettera/numero (0=esci): ").strip().lower()
        if s == "0":
            break
        for k in chiavi:
            if k.lower().startswith(s) and s != "":
                stampa(k)
                input("[EXE]")
                break

main()
