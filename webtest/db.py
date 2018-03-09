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


class DbStudent(db.Entity):
    """Každý jeden student, který se může účastnit testů."""
    _table_ = 'Student'
    id = PrimaryKey(int, column='idStudent', auto=True)
    login = Required(str, 20)
    jmeno = Required(str, 40)
    hash = Required(str, 196)
    akce = Set('DbAkce')
    vysledkyTestu = Set('DbVysledekTestu')


class DbAkce(db.Entity):
    """evidence toho, co student v aplikací dělá:
* logIn
* logOut"""
    _table_ = 'Akce'
    id = PrimaryKey(int, column='idAkce', auto=True)
    cas = Required(datetime)
    student = Required(DbStudent)
    typAkce = Required(str, 10, column='typAkce')


class DbVysledekTestu(db.Entity):
    _table_ = 'VysledekTestu'
    id = PrimaryKey(int, column='idVTestu', auto=True)
    student = Required(DbStudent)
    test = Required('DbTest')
    casZahajeni = Required(datetime, column='casZ')
    casUkonceni = Optional(datetime, column='casU')
    odpovedi = Set('DbOdpoved')


class DbTest(db.Entity):
    """Jeden konkrétní test. """
    _table_ = 'Test'
    id = PrimaryKey(int, column='idTest', auto=True)
    jmeno = Required(str, 80)
    ucitel = Required('DbUcitel')
    otazkyTestu = Set('DbOtazkaTestu')
    vysledkyTestu = Set(DbVysledekTestu)
    zobrazenoOd = Optional(datetime, column='ZobOd')
    zobrazenoDo = Optional(datetime, column='ZobDo')
    limit = Optional(str)
    pokusu = Optional(int)
    skryty = Optional(bool)
    hodnoceni = Optional(str)


class DbOtazka(db.Entity):
    """Obecná otázka:
* V obecne_zadani se dá specifikovat rozsah náhodného čísla.
* typ_otazky: Otevřená, Uzavřená,  Ciselna"""
    _table_ = 'Otazka'
    id = PrimaryKey(int, column='idOtazka', auto=True)
    ucitel = Required('DbUcitel')
    jmeno = Optional(str, 80)
    typOtazky = Optional(str, 1, column='typOtazky', sql_type='char')
    obecneZadani = Optional(str, column='oZadani', nullable=True)
    bodu = Optional(int)
    otazkyTestu = Set('DbOtazkaTestu')
    odpovedi = Set('DbOdpovedi')


class DbOdpoved(db.Entity):
    """Vazební tabulka mezi výsledkem testu a otázkami testu. 

Obsahuje znovu (redundantně) zadání a odpověď. Je to proto, že otázku může učitel editovat a není možné hodnotit odpověď na změněnou otázku. Dále se řeší problém, kdy je v otázce náhodné číslo: je nutno uchovat konkretní zadání i očekávaný výsledek """
    _table_ = 'Odpoved'
    id = PrimaryKey(int, column='idOdpoved', auto=True)
    konkretniZadani = Required(str, column='kZadani')
    ocekavanaOdpoved = Required(str, 512, column='ocOdpoved')
    konkretniOdpoved = Required(str, 512, column='kOdpoved')
    vysledekTestu = Required(DbVysledekTestu, column='vTestu')
    otazkaTestu = Required('DbOtazkaTestu', column='otTestu')


class DbOtazkaTestu(db.Entity):
    """Vazební tabulka: každý test, lze vytvořit kombinací libovolných otázek.
"""
    _table_ = 'OtazkaTestu'
    id = PrimaryKey(int, column='idOtTestu', auto=True)
    poradi = Required(int)
    test = Required(DbTest)
    otazka = Required(DbOtazka)
    odpovedi = Set(DbOdpoved)


class DbUcitel(db.Entity):
    """Každý jeden učitel, který tvoří testy."""
    _table_ = 'Ucitel'
    id = PrimaryKey(int, column='idUcitel', auto=True)
    login = Required(str, 20)
    jmeno = Required(str, 40)
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


class DbZnamky(db.Entity):
    _table_ = 'Znamky'
    id = PrimaryKey(int, column='idZnamky', auto=True)
    nazev = Required(str, 128)
    hodnoceni = Required(str, 128)


class DbOdpovedi(db.Entity):
    _table_ = 'Odpovedi'
    id = PrimaryKey(int, column='idOdpoved', auto=True)
    odpoved = Required(str)
    typ = Optional(str)
    otazka = Required(DbOtazka)


sql_debug(True)
db.generate_mapping(create_tables=True)
