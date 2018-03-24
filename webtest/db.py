# -*- coding: utf8 -*-
# Soubor:  wtdb.py
# Datum:   22.02.2015 18:42
# Autor:   Marek Nožka, nozka <@t> spseol <d.t> cz
# Autor:   Marek Nožka, marek <@t> tlapicka <d.t> net
# Licence: GNU/GPL
# Úloha:   Knihovna s definicí databáze:
#          https://editor.ponyorm.com/user/tlapicka/WebTest
############################################################################
from datetime import datetime
from pony.orm import (Database, PrimaryKey, Required, Optional, Set, sql_debug)
import webtest.spojeni

db = Database("postgres", **webtest.spojeni.DB)

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
    casZahajeni = Required(datetime, column='casZ')
    casUkonceni = Optional(datetime, column='casU')
    boduVysledek = Optional(float, column='bVysledek')
    boduMax = Optional(float, column='bMax')
    hodnoceni = Optional(str)
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
    skryty = Optional(bool)
    hodnoceni = Optional(str)
    vysledkyTestu = Set(DbVysledekTestu)
    ucitel = Required('DbUcitel')
    otazky = Set('DbOtazkaTestu')


class DbOtazka(db.Entity):
    """Obecná otázka:
* V obecne_zadani se dá specifikovat rozsah náhodného čísla.
* typ_otazky: Otevřená, Uzavřená,  Ciselna"""
    _table_ = 'Otazka'
    id = PrimaryKey(int, column='idOtazka', auto=True)
    jmeno = Required(str, 80)
    typOtazky = Optional(str, 1, column='typOtazky', sql_type='char')
    obecneZadani = Optional(str, column='oZadani', nullable=True)
    bodu = Optional(float, default=1)
    hodnotit = Optional(int, default=1)
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
    hash = Required(str, 196)
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


class DbZnamky(db.Entity):
    _table_ = 'Znamky'
    id = PrimaryKey(int, column='idZnamky', auto=True)
    nazev = Required(str, 128)
    hodnoceni = Required(str, 128)


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
    hash = Optional(str)
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
    test = Required(DbTest)
    otazka = Required(DbOtazka)
    
sql_debug(True)
db.generate_mapping(create_tables=True)
