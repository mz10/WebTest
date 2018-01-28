#!/usr/bin/env python
# -*- coding: utf8 -*-
# Soubor:  webtest.py
# Datum:   22.02.2015 16:35
# Autor:   Marek Nožka, marek <@t> tlapicka <d.t> net
# Licence: GNU/GPL
# Úloha:   Hlavní soubor aplikace WebTest
# from __future__ import division, print_function, unicode_literals
############################################################################

from flask import *
from . import app
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime
from sympy import *
from jinja2 import TemplateNotFound

from .funkce import *
from .ostatni import *
from .student import *
from .testy import *
from .otazka import *

import time
import os
import functools         
import random
import sys
import json as _json

#from crypt import crypt
#reload(sys)  # to enable `setdefaultencoding` again
#sys.setdefaultencoding("UTF-8")

############################################################################

class RegexConverter(BaseConverter):
    "Díky této funci je možné do routovat pomocí regulárních výrazů"
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

def prihlasit(klic):
    """Dekoruje funkce, které vyžadují přihlášení

    @prihlasit(klic)
    klic: je klic ve slovniku session, který se kontroluje.
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if klic in session:
                return function(*args, **kwargs)
            else:
                return redirect(url_for('login', url=request.path))
        return wrapper
    return decorator

def prihlasitJSON(klic):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if klic in session:
                return function(*args, **kwargs)
            else:
                return json({"chyba":"Nejsi přihlášen!"})
        return wrapper
    return decorator

def json(js):
    return Response(response=_json.dumps(js),status=200,mimetype="application/json")

@app.route('/')
def index():
    if 'student' in session:
        return redirect(url_for('student_testy'))
    elif 'ucitel' in session:
        return render_template('ucitel.html')
    else:
        return redirect(url_for('login'))

@app.route('/registrace/', methods=['GET', 'POST'])
@db_session
def registrace():   
    return Ostatni.registrace()

@app.route('/tabulky/')
def databaze(): return Ostatni.databaze()

@app.route('/tabulky/', methods=('get','post'), endpoint='new')
def SmazTabulku(): return Ostatni.smazTabulku()

@app.route('/tabulky/uklid/')
def uklidDb(): return Ostatni.uklidDb()

@app.route('/db/')
def db(): return render_template('db.html') 

@app.route('/vytvor/')
def NovaTabulka1(): return Ostatni.novaTabulka()

@app.route('/login/', methods=["GET", "POST"])
def login(): return Prihlaseni.prihlasit()
    
@app.route('/logout/', methods=['GET'])
def logout(): return Prihlaseni.odhlasit()

@app.route('/vysledky/', methods=['GET'])
@prihlasit('ucitel')
@db_session
def vysledky(): return Ucitel.vysledky()

@app.route('/vysledky/<id>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def vypracovan_testi(id): return Ucitel.vyplneno(id)

@app.route('/vysledky/zobraz/<id>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def zobraz_test_studenta(id): return Ucitel.zobrazTest(id)

@app.route('/json/otazky/', methods=['GET', 'POST'])
@prihlasitJSON('ucitel')
@db_session
def otazky(): return Otazka.zobrazOtazky()

@app.route('/otazky/ucitel/<login>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def otazky_ucitel(login): return Otazka.ucitel(login)

@app.route('/json/otazky/<id>', methods=['GET'])
@prihlasitJSON('ucitel')
@db_session
def otazka_zobrazit(id): return Otazka.zobraz(id)

@app.route('/otazky/editovat/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def otazka_editovat(id): return Otazka.upravit(id)

@app.route('/otazky/smazat/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def otazka_smazat(id): return Otazka.smazat(id)

@app.route('/pridat/otazku/', methods=['GET', 'POST'])
@prihlasit('ucitel')
def pridat_otazku(): return Otazka.pridat()

@app.route('/json/testy/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def testy(): return Testy.zobraz()

@app.route('/pridat/test/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def pridat_test(): return Testy.pridat()

@app.route('/testy/<id_test>', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def uprav_test(id_test): return Testy.uprav(id_test)

@app.route('/student/testy/', methods=['GET', 'POST'])
@prihlasit('student')
@db_session
def student_testy(): return Student.testy()

@app.route('/student/testy/<id>', methods=['GET', 'POST'])
@prihlasit('student')
@db_session
def student_zobrazit(id): return Student.zobrazit(id)

@app.route('/student/vysledky/')
@prihlasit('student')
@db_session
def student_vysledek(): return Student.vysledky()

@app.route('/upload/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def upload():return upload1()


@app.errorhandler(404)
def nenalezeno(ch): return render_template('404.html', e=ch), 404

@app.route('/vzory/testy/')
def testy1(): return render_template('upravit_test1.html') 

@app.route('/vzory/otazky/')
def otazky1(): return render_template('upravit_otazku1.html') 

@app.route('/json/akce/<typAkce>/<vec>/', methods=['GET'])
@prihlasitJSON('ucitel')
@db_session
def akce(typAkce,vec):
    js = {
        "akce":typAkce,
        "vec":vec,
    }

    return json(js)


@app.route('/json/post/', methods=['POST'])
@prihlasitJSON('ucitel')
@db_session
def akceP(): 
    J = request.json
    akce = J["akce"]
    co = J["co"]
    odpoved = "zadna akce"

    if(co == "otazka"):
        if akce == "smazat":
            idOtazky = J["id"]
            DbOtazka[idOtazky].delete()
            odpoved = "Otázka s id " + idOtazky + " byla smazána"
        elif akce == "pridat":
            odpoved = Otazka.pridat(J)
        elif akce == "upravit":
            odpoved = Otazka.upravit(J)
    if(co == "test"):
        if akce == "smazat":
            idTestu = J["id"]
            DbTest[idTestu].delete()
            odpoved = "Test s id " + idTestu + " byl smazán"
        elif akce == "pridat":
            odpoved = Testy.pridat(J)
        elif akce == "upravit":
            odpoved = "b"
    elif(co == "tabulka"):
        if akce == "smazat":
            Ostatni.smazTabulku(J["nazev"],"smazat")
            odpoved = "Tabulka " + J["nazev"] + " byla smazána."
        elif akce == "vysypat":
            Ostatni.smazTabulku(J["nazev"],"vysypat")
            odpoved = "Tabulka " + J["nazev"] + " byla vysypána."

    js = {
        "odpoved":odpoved,
        "stav":"ok",
    }           

    return json(js)
