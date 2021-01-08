'''
Profesor/ica ste informatike u osnovnoj školi. Kako biste svojim ucenicima
olakšali nastavu na daljinu, odnosno skori povratak u školske klupe, osmislite
jednostavan jezik koji podržava:

 jedan brojevni i jedan stringovni tip te jednostavna pridruživanja (varijabla
poprima vrijednost izraza odgovarajuceg tipa),

 izraze koji sadrže brojevne operacije (cetiri osnovne operacije, usporedbe
<; >;;;=; 6= koje vracaju broj, pretvaranje u string) te stringovne operacije
(konkatenacija, test jednakosti koji vraca broj, pretvaranje u broj),

 grananja (sa i bez „inace”) i ogranicene petlje (donja i gornja granica su
zadane brojevnim izrazima),

 unos (s tipkovnice u brojevne i stringovne varijable), ispis (prijelaza u novi
red i vrijednosti izraza) te

 jednu vrstu komentara (linijski ili višelinijski).

'''
import fractions
from pj import  *

class TT(enum.Enum):
    MANJE, JEDNAKO, JMANJE, JVECE, VECE, RAZLICITO = '<', '=', '<=', '>=', '>', '!='
    JJEDNAKO, MMANJE, VVECE = '==', '<<', '>>'
    NAVODNIK = '"'
    PLUS, MINUS, PUTA, KROZ = '+', '-', '*', '/'
    IZRACUN, BUSPOREDI, SUSPOREDI, UBROJ, KONK, PRIDRUZI, HELP, USTRING = 'izracun', 'busporedi', 'susporedi', 'ubroj', 'konk', 'pridruzi', 'help', 'ustring'
    FOR, IF, ELSE, ENDL = 'for', 'if', 'else', 'endl'
    COUT, CIN = 'cout', 'cin'
    PPLUS, JPLUS = '++', '+='
    TZAREZ, ZAREZ = ';', ','
    VOTV, VZATV, OTV, ZATV = '{}()'
    class BROJ(Token):
        def vrijednost(self, mem):
            return int(self.sadržaj)
    class STRING(Token):
        def vrijednost(self, mem):
            s = self.sadržaj[1:-1]
            return s
    class IME(Token):
        def vrijednost(self, mem):
            return pogledaj(mem, self)
    class KOMENTAR(Token):
        def vrijednost(self):
            s = self.sadržaj[2:0]
            return s#treba odsjeci prva dva znaka, jer prva dva znaka su /*

def l_lex(kod):
    lex = Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace():
            lex.zanemari()
        elif znak == '<':
            if lex.slijedi('<'):
                yield lex.token(TT.MMANJE)
            elif lex.slijedi('='):
                yield lex.token(TT.JMANJE)
            else:
                yield lex.token(TT.MANJE)
        elif znak == '>':
            if lex.slijedi('>'):
                yield lex.token(TT.VVECE)
            elif lex.slijedi('='):
                yield lex.token(TT.JVECE)
            else:
                yield lex.token(TT.VECE)
        elif znak == '/':
            if lex.slijedi('*'):
                lex.pročitaj_do('\n')
                yield lex.token(TT.KOMENTAR)
            else:
                yield lex.token(TT.KROZ)
        elif znak == '+':
            if lex.slijedi('+'):
                yield lex.token(TT.PPLUS)
            elif lex.slijedi('='):
                yield lex.token(TT.JPLUS)
            else:
                yield lex.token(TT.PLUS)
        elif znak == '=':
            if lex.slijedi("="):
                yield lex.token(TT.JJEDNAKO)
            else:
                yield lex.token(TT.JEDNAKO)
        elif znak == '!':
            if lex.slijedi("="):
                yield lex.token(TT.RAZLICITO)
            else:
                raise lex.greška("U ovom jeziku znak ! ne moze stajati sam")
        elif znak == '"':
            while True:
                z = lex.čitaj()
                if not z:
                    raise lex.greška("Nezavrseni string")
                elif z == '"':
                    yield lex.token(TT.STRING)
                    break
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            p = lex.sadržaj
            if p == '0' or p[0] != '0':
                yield lex.token(TT.BROJ)
            else:
                raise lex.greška('Jedino je baza 10 podrzana')
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            yield lex.literal(TT.IME)
        else:
            yield lex.literal(TT)

'''
Beskontekstna gramatika
start -> naredba naredbe
naredbe -> " " | naredba naredbe
naredba -> KOMENTAR | petlja | ispis TZAREZ | grananje | upis |
            izracun | busporedi | susporedi | ubroj | konk |
            pridruzi | HELP | ustring
else -> ELSE OTV ZATV naredba | ELSE OTV ZATV VOTV naredbe VZATV
petlja -> for naredba | for VOTV naredbe VZATV
ispis -> COUT varijable | COUT varijable MMANJE ENDL TZAREZ
varijable -> " " | MMANJE IME varijable
grananje -> if naredba | if VOTV naredbe VZATV | if VOTV naredbe VZATV else
if -> IF OTV IME operator_usporedbe BROJ ZATV
upis -> CIN VVECE IME
izracun -> IZRACUN OTV izraz ZATV
busporedi -> BUSPOREDI OTV BROJ operator_usporedbe BROJ ZATV
susporedi -> SUSPOREDI OTV STRING operator_usporedbe STRING ZATV
ubroj -> UBROJ OTV STRING ZATV | UBROJ OTV IME ZATV
ustring -> USTRING OTV BROJ ZATV | USTRING OTV IME ZATV
konk -> KONK OTV STRING ZAREZ STRING ZATV
for -> FOR OTV IME JEDNAKO BROJ TZAREZ IME MANJE BROJ TZAREZ IME
        inkrement ZATV
operator_usporedbe -> MANJE | JMANJE | VECE | JVECE | JJEDNAKO | RAZLICITO
inkrement -> PPLUS | JPLUS BROJ
izraz -> clan | izraz PLUS clan | izraz MINUS clan
clan -> faktor | clan PUTA faktor | clan KROZ faktor | MINUS clan | clan faktor
faktor -> BROJ | OTV izraz ZATV
pridruzi -> PRIDRUZI OTV IME ZAREZ drugaPridruzi ZATV
drugaPridruzi ->  STRING | BROJ | izracun | busporedi | susporedi | ubroj | konk | IME

'''

class LVParser(Parser):
    def start(self):
        naredbe = []
        while not self >> E.KRAJ:
            naredbe.append(self.naredba())
        return Program(naredbe)
    def naredba(self):
        if self >> TT.KOMENTAR:#ako naletis na komentar, zanemari ga
            return self.komentar()
        elif self >> TT.FOR:
            return self.petlja()
        elif self >> TT.IF:
            return self.grananje()
        elif self >> TT.COUT:
            return self.ispis()
        elif self >> TT.CIN:
            return self.upis()
        elif self >> TT.IZRACUN:
            return self.izracun()
        elif self >> TT.BUSPOREDI:
            return self.busporedi()
        elif self >> TT.SUSPOREDI:
            return self.susporedi()
        elif self >> TT.UBROJ:
            return self.ubroj()
        elif self >> TT.USTRING:
            return self.ustring()
        elif self >> TT.KONK:
            return self.konkatenacija()
        elif self >> TT.PRIDRUZI:
            return self.pridruzi()
        elif self >> TT.HELP:
            return self.help()
        else:
            raise self.greška()

    def pridruzi(self):
        self.pročitaj(TT.OTV)
        var = self.pročitaj(TT.IME)
        self.pročitaj(TT.ZAREZ)
        drugaStrana = self.drugaPridruzi()
        self.pročitaj(TT.ZATV)
        return Pridruzi(var, drugaStrana)

    def drugaPridruzi(self):
        if self >> TT.BROJ:
            return self.zadnji
        elif self >> TT.STRING:
            return self.zadnji
        elif self >> TT.IME:
            return self.zadnji
        elif self >> TT.IZRACUN:
            return self.izracun()
        elif self >> TT.BUSPOREDI:
            return self.busporedi()
        elif self >> TT.SUSPOREDI:
            return self.susporedi()
        elif self >> TT.UBROJ:
            return self.ubroj()
        elif self >> TT.USTRING:
            return self.ustring()
        elif self >> TT.KONK:
            return self.konkatenacija()
        else:
            raise self.greška('U ovom jeziku, ne mozete to pridruziti')

    def komentar(self):
        k = self.zadnji.vrijednost()
        return Komentar(k)
    def petlja(self):
        self.pročitaj(TT.OTV)
        var = self.pročitaj(TT.IME)
        self.pročitaj(TT.JEDNAKO)
        pocetak = self.pročitaj(TT.BROJ)
        self.pročitaj(TT.TZAREZ)
        var2 = self.pročitaj(TT.IME)
        if var != var2:
            raise SemantičkaGreška('U ovom jeziku nisu podrzane razlicite varijable u for petlji')
        self.pročitaj(TT.MANJE)
        granica = self.pročitaj(TT.BROJ)
        self.pročitaj(TT.TZAREZ)
        var3 = self.pročitaj(TT.IME)
        if var != var3:
            raise SemantičkaGreška('U ovom jeziku nisu podrzane razlicite varijable u for petlji')
        if self >> TT.PPLUS:
            inkrement = nenavedeno
        elif self >> TT.JPLUS:
            inkrement = self.pročitaj(TT.BROJ)
        self.pročitaj(TT.ZATV)

        if self >> TT.VOTV:
            blok = []
            while not self >> TT.VZATV:
                blok.append(self.naredba())
        else:
            blok = [self.naredba()]
        return Petlja(var, pocetak, granica, inkrement, blok)
    def grananje(self):
        self.pročitaj(TT.OTV)
        var = self.pročitaj(TT.IME)
        operator = self.pročitaj(TT.MANJE, TT.VECE, TT.JJEDNAKO, TT.JMANJE, TT.JVECE, TT.RAZLICITO)
        broj = self.pročitaj(TT.BROJ)
        self.pročitaj(TT.ZATV)
        flagElse = False
        blokElse = []
        if self >> TT.VOTV:
            blok = []
            while not self >> TT.VZATV: blok.append(self.naredba())
            if self >> TT.ELSE:
                flagElse = True
                if self >> TT.VOTV:
                    blokElse = []
                    while not self >> TT.VZATV:
                        blokElse.append(self.naredba())
                else:
                    blokElse = [self.naredba()]
        else:
            blok = [self.naredba()]
        return Grananje(var, operator, broj, blok, flagElse, blokElse)

    def help(self):
        return Help()

    def ispis(self):
        varijable = []
        noviRed = False
        while self >> TT.MMANJE:
            if self >> TT.STRING:
                varijable.append(self.zadnji)
            elif self >> TT.BROJ:
                varijable.append(self.zadnji)
            elif self >> TT.IME:
                varijable.append(self.zadnji)
            elif self >> TT.ENDL:
                noviRed = True
                break
        self.pročitaj(TT.TZAREZ)
        return Ispis(varijable, noviRed)

    def upis(self):
        self.pročitaj(TT.VVECE)
        var = self.pročitaj(TT.IME)
        self.pročitaj(TT.TZAREZ)
        return Upis(var)
    def busporedi(self):
        self.pročitaj(TT.OTV)
        broj1 = self.pročitaj(TT.BROJ)
        op = self.pročitaj(TT.MANJE, TT.VECE, TT.JJEDNAKO, TT.JMANJE, TT.JVECE, TT.RAZLICITO)
        broj2 = self.pročitaj(TT.BROJ)
        self.pročitaj(TT.ZATV)
        return Usporedi(broj1, broj2, op)
    def susporedi(self):
        self.pročitaj(TT.OTV)
        string1 = self.pročitaj(TT.STRING)
        op = self.pročitaj(TT.MANJE, TT.VECE, TT.JJEDNAKO, TT.JMANJE, TT.JVECE, TT.RAZLICITO)
        string2 = self.pročitaj(TT.STRING)
        self.pročitaj(TT.ZATV)
        return Usporedi(string1, string2, op)
    def ubroj(self):
        self.pročitaj(TT.OTV)
        string = self.pročitaj(TT.STRING, TT.IME)
        self.pročitaj(TT.ZATV)
        return UBroj(string)
    def ustring(self):
        self.pročitaj(TT.OTV)
        broj = self.pročitaj(TT.BROJ, TT.IME)
        self.pročitaj(TT.ZATV)
        return UString(broj)
    def konkatenacija(self):
        self.pročitaj(TT.OTV)
        string1 = self.pročitaj(TT.STRING)
        self.pročitaj(TT.ZAREZ)
        string2 = self.pročitaj(TT.STRING)
        self.pročitaj(TT.ZATV)
        return Konkateniraj(string1, string2)

    def izracun(self):
        self.pročitaj(TT.OTV)
        rezultat = self.izraz()
        self.pročitaj(TT.ZATV)
        return rezultat

    def izraz(self):
        trenutni = self.clan()
        while True:
            if self >> TT.PLUS:
                trenutni = Zbroj([trenutni, self.clan()])
            elif self >> TT.MINUS:
                clan = self.clan()
                trenutni = Zbroj([trenutni, Suprotan(clan)])
            else:
                break
        return trenutni

    def clan(self):
        if self >> TT.MINUS:
            return Suprotan(self.clan())
        trenutni = self.faktor()
        while True:
            if self >> TT.PUTA or self >= TT.OTV:
                trenutni = Umnozak([trenutni, self.faktor()])
            elif self >> TT.KROZ or self >= TT.OTV:
                trenutni = Kroz([trenutni, self.faktor()])
            else:
                return trenutni

    def faktor(self):
        if self >> TT.BROJ:
            return self.zadnji
        elif self >> TT.IME:
            return self.zadnji
        elif self >> TT.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(TT.ZATV)
            return u_zagradi
        else:
            raise self.greška()

nula = Token(TT.BROJ, '0')
jedan  = Token(TT.BROJ, '1')

class  Pridruzi(AST('var, drugaStrana')):
    def izvrši(self, mem):
        varijabla = self.var.sadržaj
        p = self.drugaStrana.vrijednost(mem)
        mem[varijabla] = p

class Komentar(AST('komentar')):
    def vrijednost(komentar, mem):
        return
    def izvrši(komentar, mem):
        return

class Suprotan(AST('od')):
    def vrijednost(izraz, mem):
        a = int(izraz.od.vrijednost(mem))
        return -a
    def izvrši(izraz, mem):
        a = int(izraz.od.vrijednost(mem))
        return -a

class Zbroj(AST('pribrojnici')):
    def vrijednost(izraz, mem):
        a, b = izraz.pribrojnici
        a = int(a.vrijednost(mem))
        b = int(b.vrijednost(mem))
        return a + b
    def izvrši(izraz, mem):
        a, b = izraz.pribrojnici
        a = int(a.vrijednost(mem))
        b = int(b.vrijednost(mem))
        return a + b

class Umnozak(AST('faktori')):
    def vrijednost(izraz, mem):
        a, b = izraz.faktori
        a = int(a.vrijednost(mem))
        b = int(b.vrijednost(mem))
        return a * b
    def izvrši(izraz, mem):
        a, b = izraz.faktori
        a = int(a.vrijednost(mem))
        b = int(b.vrijednost(mem))
        return a * b

class Kroz(AST('djelitelji')):
    def vrijednost(izraz, mem):
        a, b = izraz.djelitelji
        a = int(a.vrijednost(mem))
        b = int(b.vrijednost(mem))
        return a / b
    def izvrši(izraz, mem):
        a, b = izraz.djelitelji
        a = int(a.vrijednost(mem))
        b = int(b.vrijednost(mem))
        return a / b

class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        for naredba in self.naredbe:
            naredba.izvrši(memorija)

class Petlja(AST('var pocetak granica inkrement blok')):
    def izvrši(self, mem):
        v = self.var.sadržaj
        mem[v] = self.pocetak.vrijednost(mem)
        while mem[v] < self.granica.vrijednost(mem):
            for naredba in self.blok:
                naredba.izvrši(mem)
            inkr = self.inkrement
            if inkr is nenavedeno:
                inkr = 1
            else:
                inkr = inkr.vrijednost(mem)
            mem[v] += inkr

pomoc = open("pomocSJezikom.txt", "r")
class Help(AST('')):
    def izvrši(self, mem):
        print(pomoc.read())

class Ispis(AST('varijable noviRed')):
    def izvrši(self, mem):
        for varijabla in self.varijable:
            print(varijabla.vrijednost(mem), end=' ')
        if self.noviRed:
            print()

class Upis(AST('var')):
    def izvrši(self, mem):
        varijabla = input()
        try:
            varijabla = int(varijabla)
        except ValueError:
            varijabla = varijabla
        mem[self.var.sadržaj] = varijabla

class Grananje(AST('var operator broj blok flagElse blokElse')):
    def izvrši(self, mem):
        lijevo = self.var.vrijednost(mem)
        desno = self.broj.vrijednost(mem)
        op = self.operator
        flag = self.flagElse
        if op ^ TT.MANJE:
            if lijevo < desno:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            else:
                if flag == True:
                    for naredba in self.blokElse:
                        naredba.izvrši(mem)

        elif op ^ TT.VECE:
            if lijevo > desno:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            else:
                if flag == True:
                    for naredba in self.blokElse:
                        naredba.izvrši(mem)
        elif op ^ TT.JVECE:
            if lijevo >= desno:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            else:
                if flag == True:
                    for naredba in self.blokElse:
                        naredba.izvrši(mem)
        elif op ^ TT.JJEDNAKO:
            if lijevo == desno:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            else:
                if flag == True:
                    for naredba in self.blokElse:
                        naredba.izvrši(mem)
        elif op ^ TT.JMANJE:
            if lijevo <= desno:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            else:
                if flag == True:
                    for naredba in self.blokElse:
                        naredba.izvrši(mem)
        elif op ^ TT.RAZLICITO:
            if lijevo != desno:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            else:
                if flag == True:
                    for naredba in self.blokElse:
                        naredba.izvrši(mem)
        else:
            raise self.greška()

class Usporedi(AST('prvi drugi op')):
    def vrijednost(self, mem):
        return self.izvrši(mem)
    def izvrši(self, mem):
        lijevo = self.prvi.vrijednost(mem)
        desno = self.drugi.vrijednost(mem)
        op = self.op
        if op ^ TT.MANJE:
            return int(lijevo < desno)
        elif op ^ TT.VECE:
            return int(lijevo > desno)
        elif op ^ TT.JVECE:
            return int(lijevo >= desno)
        elif op ^ TT.JJEDNAKO:
            return int(lijevo == desno)
        elif op ^ TT.JMANJE:
            return int(lijevo <= desno)
        elif op ^ TT.RAZLICITO:
            return int(lijevo != desno)
        else:
            raise self.greška()

class UBroj(AST('string')):
    def vrijednost(self, mem):
        return self.izvrši(mem)
    def izvrši(self, mem):
        varijabla = self.string.vrijednost(mem)
        try:
            varijabla = int(varijabla)
        except ValueError:
            raise SemantičkaGreška('Nemoguće pretvoriti u broj')
        return varijabla
class UString(AST('broj')):
    def vrijednost(self, mem):
        return self.izvrši(mem)
    def izvrši(self, mem):
        return str(self.broj.vrijednost(mem))
class Konkateniraj(AST('string1 string2')):
    def vrijednost(self, mem):
        return self.izvrši(mem)
    def izvrši(self, mem):
        s1 = self.string1.vrijednost(mem)
        s2 = self.string2.vrijednost(mem)
        return s1 + s2

if __name__ == '__main__':


    ulaz = '''/*komentar: ispisuje hello world na ekran
                cout << "Hello World" << endl;
        '''
    ulaz2 = '''
    /*komentar: isprintaj prvih 100 brojeva, osim 30
    cout<<"isprintaj svaki treci broj do  100, osim 30"<<endl;
   for (i=0; i<100; i+=3){
        /* ako je i razlicit od 30, ispisi ga
        if(i!=30)cout << i << " ";
   }
   cout << endl;
                '''

    ulaz3 = '''/*komentar: crta mrezu tockica 10x10
    cout<<"crta mrezu tockica 10x10"<<endl;
/*crta redove
   for (i=0; i<10; i++){
    /*crta stupce
        for(j=0; j<10; j++){
        /*printa tockice
            cout << ". " ;
        }
        cout << endl;
   }
   cout << endl;'''

    ulaz4 = '''/*komentar: zadatak s operacijama nad stringovima
/*provjeravam da li se Jakov i Luccija isto zovu koristeci naredbu susporedi, koja vraca broj 0 ako brojevi nisu jednaki
    pridruzi(j, "Jakov")
    pridruzi(l, "Lucija")
    pridruzi(a, susporedi("Jakov" == "Lucija"))
    if (a==0) cout<<"Imena mojih prijatelja " << j<< " i "<< l <<" nisu ista"<<endl;
    /*Konkatenacijom pridruzujem lucijinom imenu njeno prezime
    pridruzi(lv, konk("Lucija", " Valentić"))
    cout<<"Puno ime moje kolegice, zvane " << l <<" je " << lv <<endl;
    /*pridruzujem imenu lucijine ulice broj njene adrese, pretvoren u string
    pridruzi(broj, ustring(2))
    pridruzi(adresa, "Tomašićeva")
    cout<<lv << " zivi na adresi "<< adresa <<" " <<broj;'''

    ulaz5 = '''/*komentar: crta kvadrat upisanih 10 znakova, po 10 u svakom redu, gdje samo prvi smije biti 0. Ako je drugdje dana 0, ispisuje prethodni znak.
    cout<<"crta kvadrat upisanih 10 znakova, po 10 u svakom redu, gdje samo prvi smije biti 0. Ako je drugdje dana 0, ispisuje prethodni znak"<<endl;
/*ucitava broj prvi put
/*crta prvi red
cin >> n;
 for(j=0; j<9; j++){
            cout << n << " " ;
        }
cout << endl;

/*crta drugih 9 stupaca
for (i=0; i<10; i++){
    /*ucitava novi broj
    cin >> novi;
    if (novi!= 0)pridruzi(n, novi)
    /*ispisuje novi redak
        for(j=0; j<9; j++){
            cout << n << " " ;
        }
        cout << endl;
   }
   cout << endl;'''


    #print(ulaz)
    print()

    tokeni = list(l_lex(ulaz))
    #print(*tokeni)#lekser
    print()

    cpp = LVParser.parsiraj(tokeni)
    cpp.izvrši()

    print()
