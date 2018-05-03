from datetime import datetime
from pony.orm import (Database, PrimaryKey, Required, Optional, Set, sql_debug)
from .spojeni import pripojit

db = Database("postgres", **pripojit)

class DbAkce(db.Entity):
    """evidence toho, co student v aplikací dělá: logIn, logOut"""
    _table_ = 'Akce'
    id = PrimaryKey(int, column='idAkce', auto=True)
    cas = Required(datetime)
    typAkce = Required(str, 10, column='typAkce')
    student = Required('DbStudent')


class DbVysledekTestu(db.Entity):
    _table_ = 'VysledekTestu'
    id = PrimaryKey(int, column='idVTestu', auto=True)
    jmeno = Optional(str)
    casZahajeni = Required(datetime, column='casZ')
    casUkonceni = Optional(datetime, column='casU')
    limit = Optional(str)
    pokus = Optional(int)
    boduVysledek = Optional(float, column='bVysledek', default=0)
    boduMax = Optional(float, column='bMax', default=0)
    typHodnoceni = Optional(int, column='tHodnoceni', default=0)
    hodnoceni = Optional(str)
    znamka = Optional(str)
    test = Optional('DbTest')
    otazky = Set('DbVyslednaOtazka')
    student = Optional('DbStudent')
    vysledneOdpovedi = Set('DbVyslednaOdpoved')


class DbTest(db.Entity):
    """Jeden konkrétní test. """
    _table_ = 'Test'
    id = PrimaryKey(int, column='idTest', auto=True)
    jmeno = Required(str, 80)
    zobrazenoOd = Optional(datetime, column='ZobOd')
    zobrazenoDo = Optional(datetime, column='ZobDo')
    limit = Optional(str)
    pokusu = Optional(int)
    maxOtazek = Optional(int, column='mOtazek')
    nahodny = Optional(bool, default=False)
    skryty = Optional(bool, default=False)
    typHodnoceni = Optional(int, column='tHodnoceni', default=0)
    hodnoceni = Optional(str)
    vysledkyTestu = Set(DbVysledekTestu)
    otazky = Set('DbOtazkaTestu')
    ucitel = Required('DbUcitel')
    tridy = Set('DbTridyTestu')


class DbOtazka(db.Entity):
    """Obecná otázka:
* V obecne_zadani se dá specifikovat rozsah náhodného čísla.
* typ_otazky: Otevřená, Uzavřená,  Ciselna"""
    _table_ = 'Otazka'
    id = PrimaryKey(int, column='idOtazka', auto=True)
    jmeno = Required(str, 80)
    obecneZadani = Optional(str, column='oZadani', nullable=True)
    bodu = Optional(float, default=1)
    hodnotit = Optional(int, default=1)
    zaokrouhlit = Optional(int, default=2)
    tolerance = Optional(float, default=0)
    ucitel = Required('DbUcitel')
    odpovedi = Set('DbOdpoved')
    otazkyTestu = Set('DbOtazkaTestu')


class DbVyslednaOtazka(db.Entity):
    """Vazební tabulka mezi výsledkem testu a otázkami testu. 

Obsahuje znovu (redundantně) zadání a odpověď. Je to proto, že otázku může učitel editovat a není možné hodnotit odpověď na změněnou otázku. Dále se řeší problém, kdy je v otázce náhodné číslo: je nutno uchovat konkretní zadání i očekávaný výsledek """
    _table_ = 'VyslednaOtazka'
    id = PrimaryKey(int, column='idVOtazka', auto=True)
    jmeno = Optional(str)
    puvodniZadani = Optional(str)
    konkretniZadani = Required(str, column='kZadani')
    bodu = Optional(float)
    boduVysledek = Optional(float, column='bVysledek')
    hodnotit = Optional(int, default=1)
    zaokrouhlit = Optional(int, default=2)
    tolerance = Optional(float, default=0)
    vyslednaOdpoved = Set('DbVyslednaOdpoved')
    vysledekTestu = Optional(DbVysledekTestu, column='vTestu')
    puvodniOtazka = Optional(int, column='pOtazka')


class DbUcitel(db.Entity):
    """Každý jeden učitel, který tvoří testy."""
    _table_ = 'Ucitel'
    id = PrimaryKey(int, column='idUcitel', auto=True)
    login = Required(str, 20)
    jmeno = Optional(str, 40)
    prijmeni = Optional(str)
    hash = Required(str, 196, default="123")
    admin = Optional(bool, default=False)
    testy = Set(DbTest)
    otazky = Set(DbOtazka)


class DbSlovnik(db.Entity):
    _table_ = 'Slovnik'
    id = PrimaryKey(int, column='idSlovnik', auto=True)
    slovo1 = Optional(str, 128)
    slovo2 = Optional(str, 128)
    kategorie = Optional(str, 128)
    jazyk = Optional(str, 128)


class DbTridy(db.Entity):
    _table_ = 'Tridy'
    id = PrimaryKey(int, column='idTridy', auto=True)
    poradi = Optional(int)
    nazev = Required(str, 128)
    rokUkonceni = Optional(int, column='rokUkonceni')
    studenti = Set('DbStudent')
    tridyTestu = Set('DbTridyTestu')


class DbOdpoved(db.Entity):
    _table_ = 'Odpoved'
    id = PrimaryKey(int, column='idOdpoved', auto=True)
    odpoved = Required(str)
    typ = Required(str, 1)
    otazka = Required(DbOtazka)


class DbStudent(db.Entity):
    """Každý jeden student, který se může účastnit testů."""
    _table_ = 'Student'
    id = PrimaryKey(int, column='idStudent', auto=True)
    login = Optional(str)
    jmeno = Optional(str)
    prijmeni = Optional(str)
    hash = Optional(str, default="123")
    akce = Set(DbAkce)
    vysledkyTestu = Set(DbVysledekTestu)
    trida = Optional(DbTridy)


class DbVyslednaOdpoved(db.Entity):
    _table_ = 'VyslednaOdpoved'
    id = PrimaryKey(int, column='idVOdpoved', auto=True)
    ocekavanaOdpoved = Optional(str, column='ocOdpoved')
    odpoved = Optional(str)
    typ = Optional(str)
    vysledekTestu = Optional(DbVysledekTestu, column='vTestu')
    vyslednaOtazka = Optional(DbVyslednaOtazka, column='vOtazka')


class DbOtazkaTestu(db.Entity):
    _table_ = 'OtazkaTestu'
    id = PrimaryKey(int, column='idOTestu', auto=True)
    poradi = Optional(int)
    pocet = Optional(int, default=1)
    test = Required(DbTest)
    otazka = Required(DbOtazka)


class DbTridyTestu(db.Entity):
    _table_ = 'TridyTestu'
    id = PrimaryKey(int, column='idTrTestu', auto=True)
    test = Optional(DbTest)
    trida = Optional(DbTridy)
    
sql_debug(True)
db.generate_mapping(create_tables=True)
