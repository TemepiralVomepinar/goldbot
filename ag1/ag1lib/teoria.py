"""Domande di teoria ricorrenti negli appelli: definizioni, enunciati e dimostrazioni."""
import textwrap

T = {}


def _add(chiave, titolo, enunciato, dimostrazione=None, alias=()):
    T[chiave] = dict(titolo=titolo, enunciato=enunciato, dimostrazione=dimostrazione, alias=tuple(alias))


# ============================================================== definizioni ==
_add("continuita", "Funzione continua in x0",
     "f: [a,b] -> R, x0 in (a,b). f e' continua in x0 se per ogni eps>0 esiste delta>0 tale che\n"
     "|x - x0| < delta  =>  |f(x) - f(x0)| < eps.   Equivalentemente lim_{x->x0} f(x) = f(x0).",
     alias=("continua",))
_add("derivabilita", "Funzione derivabile in x0",
     "f e' derivabile in x0 se esiste FINITO il limite del rapporto incrementale\n"
     "f'(x0) = lim_{h->0} [f(x0+h) - f(x0)] / h.\n"
     "Teorema: derivabile in x0 => continua in x0.",
     "f(x0+h) - f(x0) = h * [f(x0+h)-f(x0)]/h  ->  0 * f'(x0) = 0 per h -> 0, quindi f(x0+h) -> f(x0).",
     alias=("derivabile", "derivata"))
_add("integrabilita", "Funzione integrabile (Riemann) in [a,b]",
     "f: [a,b] -> R limitata. Per una partizione P = {a=x0<...<xn=b} sia m_i = inf_{[x_{i-1},x_i]} f, M_i = sup, e\n"
     "s(f,P) = sum m_i (x_i - x_{i-1}) (somma inferiore),  S(f,P) = sum M_i (x_i - x_{i-1}) (somma superiore).\n"
     "f e' integrabile se sup_P s(f,P) = inf_P S(f,P); il valore comune e' l'integrale di f su [a,b].\n"
     "Equivalente: per ogni eps>0 esiste P con S(f,P) - s(f,P) < eps.\n"
     "Sono integrabili: le funzioni continue su [a,b], le monotone, le limitate con un numero finito di discontinuita'.",
     alias=("integrabile", "integrale", "riemann"))
_add("limite_successione", "Limite di una successione",
     "a_n -> L (L reale) se per ogni eps>0 esiste N tale che |a_n - L| < eps per ogni n > N.\n"
     "a_n -> +oo se per ogni M>0 esiste N tale che a_n > M per ogni n > N. (analogo per -oo).",
     alias=("limite", "successioni"))
_add("monotona", "Successione monotona",
     "(a_n) e' crescente se a_n <= a_(n+1) per ogni n (strettamente se <); decrescente se a_n >= a_(n+1).\n"
     "Monotona = crescente o decrescente.", alias=("successione monotona",))
_add("sup_inf", "Estremo superiore/inferiore",
     "M e' maggiorante di A se a <= M per ogni a in A. sup A = minimo dei maggioranti (+oo se A illimitato sup.);\n"
     "inf A = massimo dei minoranti. Caratterizzazione: L = sup A  <=>  (i) a <= L per ogni a in A e\n"
     "(ii) per ogni eps>0 esiste a in A con a > L - eps.  max A esiste  <=>  sup A appartiene ad A.\n"
     "Assioma di completezza: ogni A non vuoto, superiormente limitato, ha estremo superiore in R.",
     alias=("estremo", "supremo", "completezza", "maggiorante"))

# ================================================================== teoremi ==
_add("fermat", "Teorema di Fermat",
     "Sia f definita in un intorno di x0, derivabile in x0, con un estremo relativo (massimo o minimo locale) in x0.\n"
     "Allora f'(x0) = 0.\n"
     "(Non vale il viceversa: f = x^3, f'(0)=0 ma 0 non e' estremo.  Serve la derivabilita': f=|x| ha minimo in 0 ma f'(0) non esiste.)",
     "Sia x0 punto di massimo locale: per h > 0 piccolo f(x0+h) - f(x0) <= 0, quindi il rapporto incrementale\n"
     "(f(x0+h)-f(x0))/h <= 0 e al limite f'_+(x0) <= 0. Per h < 0 il rapporto e' >= 0, quindi f'_-(x0) >= 0.\n"
     "Poiche' f e' derivabile, f'_+(x0) = f'_-(x0) = f'(x0): 0 <= f'(x0) <= 0, cioe' f'(x0) = 0.\n"
     "Il caso di minimo si ottiene applicando il precedente a -f.")
_add("rolle", "Teorema di Rolle",
     "f continua in [a,b], derivabile in (a,b), f(a) = f(b). Allora esiste c in (a,b) con f'(c) = 0.",
     "Per Weierstrass f ha massimo M e minimo m in [a,b]. Se M = m f e' costante e f' = 0 ovunque.\n"
     "Altrimenti, poiche' f(a) = f(b), almeno uno fra M e m e' assunto in un punto c interno ad (a,b):\n"
     "per Fermat f'(c) = 0.")
_add("lagrange", "Teorema di Lagrange (valor medio)",
     "f continua in [a,b], derivabile in (a,b). Allora esiste c in (a,b) tale che\n"
     "f(b) - f(a) = f'(c) (b - a).\n"
     "Conseguenze: f' = 0 su un intervallo => f costante; f' >= 0 => f crescente; f' > 0 => strettamente crescente.",
     "Sia g(x) = f(x) - f(a) - [(f(b)-f(a))/(b-a)] (x - a). g e' continua in [a,b], derivabile in (a,b), g(a) = 0 = g(b).\n"
     "Per Rolle esiste c con g'(c) = 0, cioe' f'(c) - (f(b)-f(a))/(b-a) = 0.\n"
     "Monotonia: se f' >= 0 e x1 < x2, f(x2)-f(x1) = f'(c)(x2-x1) >= 0.", alias=("valor medio", "valor_medio"))
_add("cauchy", "Teorema di Cauchy",
     "f, g continue in [a,b], derivabili in (a,b), g' != 0 in (a,b). Esiste c in (a,b) con\n"
     "[f(b)-f(a)] / [g(b)-g(a)] = f'(c)/g'(c).  (Da qui si ricava il teorema di de L'Hopital.)",
     "h(x) = f(x)[g(b)-g(a)] - g(x)[f(b)-f(a)] verifica h(a) = h(b); si applica Rolle a h.")
_add("zeri", "Teorema degli zeri (esistenza degli zeri)",
     "f continua in [a,b] con f(a) f(b) < 0. Allora esiste c in (a,b) con f(c) = 0.",
     "Supponiamo f(a) < 0 < f(b). Sia a0 = a, b0 = b e m il punto medio: se f(m) = 0 si ha finito; se f(m) < 0 pongo [a1,b1] = [m,b0],\n"
     "altrimenti [a1,b1] = [a0,m]. Iterando si ottengono intervalli annidati [a_n,b_n] di lunghezza (b-a)/2^n con f(a_n) < 0 < f(b_n).\n"
     "a_n e' crescente e limitata, b_n decrescente e limitata, hanno lo stesso limite c (completezza di R).\n"
     "Per continuita' f(c) = lim f(a_n) <= 0 e f(c) = lim f(b_n) >= 0 (permanenza del segno), quindi f(c) = 0.",
     alias=("bolzano", "esistenza degli zeri"))
_add("valori_intermedi", "Teorema dei valori intermedi",
     "f continua in [a,b]. Allora f assume tutti i valori compresi fra f(a) e f(b); piu' in generale l'immagine di un intervallo\n"
     "tramite una funzione continua e' un intervallo. Cioe' per ogni y fra f(a) e f(b) esiste c in [a,b] con f(c) = y.",
     "Se y = f(a) o y = f(b) e' ovvio. Altrimenti sia g(x) = f(x) - y: g e' continua e g(a) g(b) < 0 (y e' strettamente fra\n"
     "f(a) e f(b)). Per il teorema degli zeri esiste c in (a,b) con g(c) = 0, cioe' f(c) = y.",
     alias=("valori intermedi", "intermedi"))
_add("weierstrass", "Teorema di Weierstrass",
     "f continua in [a,b] (intervallo chiuso e limitato). Allora f e' limitata e ha massimo e minimo assoluti in [a,b]:\n"
     "esistono x1, x2 in [a,b] con f(x1) <= f(x) <= f(x2) per ogni x. (Fallisce su intervalli aperti o illimitati.)",
     "(Cenno) Sia M = sup f (eventualmente +oo): esiste (x_n) con f(x_n) -> M; per Bolzano-Weierstrass una sottosuccessione converge\n"
     "a x2 in [a,b]; per continuita' f(x2) = M, quindi M e' finito ed e' un massimo.", alias=("massimo e minimo",))
_add("unicita_limite", "Unicita' del limite",
     "Se a_n -> L e a_n -> L' allora L = L'.  (Vale anche per le funzioni.)",
     "Per assurdo L != L'; sia eps = |L-L'|/2 > 0. Esistono N1, N2 con |a_n - L| < eps per n > N1 e |a_n - L'| < eps per n > N2.\n"
     "Per n > max(N1,N2): |L-L'| <= |L-a_n| + |a_n-L'| < 2 eps = |L-L'|, assurdo.", alias=("unicita", "unicità"))
_add("permanenza_segno", "Permanenza del segno",
     "Se a_n -> L > 0 allora a_n > 0 definitivamente (anzi a_n > L/2). Se a_n >= 0 definitivamente e a_n -> L, allora L >= 0.",
     "Si prende eps = L/2: per n > N, a_n > L - L/2 = L/2 > 0. Seconda parte: se fosse L < 0, applicando la prima a -a_n -> -L > 0\n"
     "si avrebbe a_n < 0 definitivamente, assurdo.")
_add("confronto", "Teorema del confronto (carabinieri)",
     "Se a_n <= b_n <= c_n definitivamente e a_n -> L, c_n -> L allora b_n -> L.  Se a_n <= b_n e a_n -> +oo allora b_n -> +oo.",
     "Dato eps, definitivamente L - eps < a_n <= b_n <= c_n < L + eps, cioe' |b_n - L| < eps. Seconda parte: a_n > M => b_n >= a_n > M.",
     alias=("carabinieri",))
_add("monotone", "Limite delle successioni monotone",
     "Una successione monotona ha sempre limite: se crescente a_n -> sup{a_n} (finito se limitata, +oo altrimenti);\n"
     "se decrescente a_n -> inf{a_n}.  Quindi monotona e limitata => convergente.",
     "Sia a_n crescente e L = sup a_n < oo. Dato eps, per la caratterizzazione del sup esiste N con a_N > L - eps;\n"
     "per n > N: L - eps < a_N <= a_n <= L, cioe' |a_n - L| < eps. Se L = +oo: per ogni M esiste a_N > M e quindi a_n > M per n > N.",
     alias=("successione monotona", "limiti di successioni monotone"))
_add("bernoulli", "Disuguaglianza di Bernoulli (induzione)",
     "Per x >= -1 e n intero: (1+x)^n >= 1 + n x.",
     "Base n=0 (o 1): ok. Passo: (1+x)^(n+1) = (1+x)^n (1+x) >= (1+nx)(1+x) = 1 + (n+1)x + n x^2 >= 1 + (n+1)x\n"
     "(si usa 1+x >= 0). Principio di induzione: base + passo.", alias=("induzione",))
_add("radice2", "sqrt(2) e' irrazionale",
     "sqrt(2) non appartiene a Q.",
     "Per assurdo sqrt2 = p/q con p,q primi tra loro. Allora p^2 = 2q^2, quindi p^2 e' pari e dunque p e' pari: p = 2k.\n"
     "Allora 4k^2 = 2q^2, cioe' q^2 = 2k^2, quindi anche q e' pari: assurdo (p,q primi tra loro).", alias=("irrazionale", "sqrt(2)"))
_add("demoivre", "Formula di De Moivre",
     "Per z = rho (cos t + i sen t) e n intero positivo: z^n = rho^n (cos nt + i sen nt).\n"
     "Radici n-esime: z^n = w = r e^(i phi) ha esattamente n soluzioni z_k = r^(1/n) e^(i (phi + 2 k pi)/n), k = 0..n-1,\n"
     "vertici di un poligono regolare di n lati inscritto nella circonferenza di raggio r^(1/n).",
     "Induzione su n. n=1 ovvio. Se vale per n: z^(n+1) = z^n z = rho^(n+1)(cos nt + i sen nt)(cos t + i sen t)\n"
     "= rho^(n+1)[(cos nt cos t - sen nt sen t) + i (sen nt cos t + cos nt sen t)] = rho^(n+1)(cos(n+1)t + i sen(n+1)t)\n"
     "per le formule di addizione.  Radici: z = rho e^(it): z^n = w <=> rho^n = r e n t = phi + 2k pi; k e k+n danno lo stesso punto.",
     alias=("de moivre", "moivre", "radici"))
_add("ftic", "Teorema fondamentale del calcolo integrale (Torricelli-Barrow)",
     "f continua in [a,b]. (1) La funzione integrale F(x) = int_a^x f(t) dt e' derivabile in [a,b] e F'(x) = f(x).\n"
     "(2) Se G e' una primitiva qualsiasi di f: int_a^b f(x) dx = G(b) - G(a).",
     "(1) Per h > 0: [F(x+h) - F(x)]/h = (1/h) int_x^(x+h) f(t) dt = f(c_h) con c_h in [x,x+h] (media integrale).\n"
     "Per h -> 0, c_h -> x e per continuita' f(c_h) -> f(x). (Analogo per h < 0.)\n"
     "(2) F e G sono primitive di f sull'intervallo: (F - G)' = 0, quindi F - G = costante (Lagrange). Allora\n"
     "int_a^b f = F(b) - F(a) = G(b) - G(a) (si usa F(a) = 0).",
     alias=("fondamentale", "torricelli", "barrow", "teorema fondamentale"))
_add("media_integrale", "Teorema della media integrale",
     "f continua in [a,b]. Esiste c in [a,b] tale che (1/(b-a)) int_a^b f(x) dx = f(c).",
     "Per Weierstrass m = min f <= f(x) <= max f = M. Per la monotonia dell'integrale m(b-a) <= int_a^b f <= M(b-a),\n"
     "quindi la media integrale e' un valore in [m,M]. Per il teorema dei valori intermedi e' assunta da f in qualche c.",
     alias=("media",))
_add("edo_lineare", "Soluzione generale di un'equazione lineare del primo ordine",
     "y'(x) + a(x) y(x) = b(x), con a, b continue in un intervallo I. Sia A(x) una primitiva di a. Tutte e sole le soluzioni sono\n"
     "y(x) = e^(-A(x)) [ C + int b(x) e^(A(x)) dx ],  C in R. Con il dato y(x0) = y0 la soluzione e' unica.",
     "Moltiplicando per e^(A): (y e^A)' = y' e^A + a y e^A = b e^A. Quindi y soddisfa l'equazione <=> (y e^A)' = b e^A\n"
     "<=> y e^A = C + int b e^A (due primitive differiscono per una costante) <=> y = e^(-A)(C + int b e^A).\n"
     "Es.: y' = 4x^3 y, y(1)=-1: A = -x^4, y = C e^(x^4), C e = -1: y = -e^(x^4 - 1).",
     alias=("edo", "lineare", "primo ordine", "equazione differenziale"))
_add("distanza_punto_piano", "Distanza di un punto da un piano",
     "Piano pi: ax + by + cz = d, punto P0 = (x0,y0,z0): d(P0, pi) = |a x0 + b y0 + c z0 - d| / sqrt(a^2 + b^2 + c^2).\n"
     "Distanza punto-retta: d(P, r) = |(P - P0) x v| / |v|.  Distanza fra rette sghembe: |(P2-P1)·(v1 x v2)| / |v1 x v2|.",
     "La retta per P0 ortogonale a pi e' P0 + t n, n = (a,b,c). Interseca pi per t* = (d - n·P0)/|n|^2. Il piede e' H = P0 + t* n\n"
     "e d = |P0 H| = |t*| |n| = |d - n·P0|/|n|.", alias=("punto piano", "distanza"))
_add("derivata_integrale", "Funzione integrale",
     "Se f e' continua, G(x) = int_{u(x)}^{v(x)} f(t) dt ha derivata G'(x) = f(v(x)) v'(x) - f(u(x)) u'(x) (teorema fondamentale + derivata composta).",
     alias=("funzione integrale",))
_add("hopital", "Teorema di de L'Hopital",
     "f, g derivabili vicino a x0 (x0 anche +-oo), g' != 0, e lim f/g e' 0/0 o oo/oo. Se esiste lim f'/g' (finito o infinito), allora\n"
     "esiste lim f/g e coincide con lim f'/g'.", alias=("hopital", "l'hopital"))
_add("taylor", "Formula di Taylor",
     "f derivabile n volte in x0: f(x) = sum_{k=0}^n f^(k)(x0)/k! (x-x0)^k + o((x-x0)^n)   (resto di Peano).\n"
     "Se f e' (n+1) volte derivabile: resto di Lagrange R_n = f^(n+1)(xi)/(n+1)! (x-x0)^(n+1), xi fra x0 e x.\n"
     "Maclaurin: e^x = 1+x+x^2/2+x^3/6+..., sen x = x - x^3/6 + x^5/120..., cos x = 1 - x^2/2 + x^4/24...,\n"
     "ln(1+x) = x - x^2/2 + x^3/3..., (1+x)^a = 1 + a x + a(a-1)/2 x^2 + ..., arctg x = x - x^3/3 + ...", alias=("maclaurin",))
_add("convessita", "Derivata seconda e convessita'",
     "f due volte derivabile in un intervallo: f'' >= 0 <=> f convessa; f'' <= 0 <=> concava.\n"
     "Un punto di flesso e' un punto in cui f cambia convessita' (f''(x0) = 0 e cambio di segno).",
     alias=("flesso", "concavita"))
_add("rapporto_radice", "Criteri del rapporto e della radice (successioni)",
     "a_n > 0. Se a_(n+1)/a_n -> l (oppure (a_n)^(1/n) -> l): se l < 1 allora a_n -> 0; se l > 1 allora a_n -> +oo; se l = 1 non si conclude.\n"
     "Gerarchia degli infiniti: (ln n)^b << n^a << c^n << n! << n^n  (c>1, a,b>0).", alias=("rapporto", "radice"))
_add("improprio", "Integrali impropri: criteri di convergenza",
     "int_1^(+oo) 1/x^p dx converge <=> p > 1;  int_0^1 1/x^p dx converge <=> p < 1.\n"
     "Confronto: 0 <= f <= g e int g converge => int f converge. Confronto asintotico: f ~ g (positive) => stesso carattere.\n"
     "Assoluta convergenza => convergenza. Esponenziali: int_0^(+oo) e^(-ax) dx converge <=> a > 0.",
     alias=("impropri", "convergenza"))
_add("curve", "Lunghezza di una curva e integrale curvilineo",
     "r: [a,b] -> R^n di classe C^1 e' regolare se r'(t) != 0. Lunghezza L = int_a^b |r'(t)| dt;\n"
     "integrale di linea di f su gamma: int_gamma f ds = int_a^b f(r(t)) |r'(t)| dt (non dipende dalla parametrizzazione).\n"
     "Retta tangente in r(t0): r(t0) + s r'(t0).  La curva e' piana se det[r', r'', r'''] = 0; chiusa se r(a) = r(b).",
     alias=("lunghezza", "linea", "curvilineo"))


def cerca(testo):
    q = testo.lower().strip()
    ris = []
    for k, v in T.items():
        chiavi = [k, v["titolo"].lower()] + [a.lower() for a in v["alias"]]
        if any(q in c or c in q for c in chiavi):
            ris.append(k)
    return ris


def mostra(chiave, dimostrazione=True):
    v = T[chiave]
    print(f"\n=== {v['titolo']} ===")
    print(textwrap.indent(v["enunciato"], "  "))
    if dimostrazione and v["dimostrazione"]:
        print("  --- Dimostrazione ---")
        print(textwrap.indent(v["dimostrazione"], "  "))


def teoria(argomento=None):
    """Senza argomento elenca gli argomenti; con argomento mostra enunciato e dimostrazione (ricerca per parola chiave)."""
    if not argomento:
        print("Argomenti disponibili (usa la parola chiave o l'alias):")
        for k, v in T.items():
            print(f"  {k:22s} {v['titolo']}")
        return []
    trovati = cerca(argomento)
    if not trovati:
        print(f"nessun argomento per '{argomento}'. Usa `teoria` senza argomenti per l'elenco.")
        return []
    for k in trovati:
        mostra(k)
    return trovati
