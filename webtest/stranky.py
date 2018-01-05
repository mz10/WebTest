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
import time
import os
import functools
from .funkce import *                
import random
import sys
import json

from jinja2 import TemplateNotFound

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

def prihlasit0(klic):
    #Dekoruje funkce, které vyžadují přihlášení
    #@prihlasit(klic)
    #klic: je klic ve slovniku session, který se kontroluje.

    if not klic in session:
        return redirect(url_for('login', url=request.path))
    return False
    
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
def databaze(): 
    return Ostatni.databaze()

@app.route('/tabulky/', methods=('get','post'), endpoint='new')
def SmazTabulku(): 
    return Ostatni.smazTabulku()

@app.route('/tabulky/uklid/')
def uklidDb(): 
    return Ostatni.uklidDb()

@app.route('/db/')
def db(): 
    return render_template('db.html') 

@app.route('/vytvor/')
def NovaTabulka1(): 
    return Ostatni.novaTabulka()

@app.route('/login/', methods=["GET", "POST"])
def login():
    return Prihlaseni.prihlasit()
    
@app.route('/logout/', methods=['GET'])
def logout():
    return Prihlaseni.odhlasit()

@app.route('/vysledky/', methods=['GET'])
@prihlasit('ucitel')
@db_session
def vysledky():
    return Ucitel.vysledky()

@app.route('/vysledky/<id>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def vypracovan_testi(id):
    return Ucitel.vyplneno(id)

@app.route('/vysledky/zobraz/<id>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def zobraz_test_studenta(id):
    return Ucitel.zobrazTest(id)

@app.route('/otazky/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def otazky():
    return Otazky.zobraz()

@app.route('/otazky/ucitel/<login>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def otazky_ucitel(login):
    return Otazky.ucitel(login)

@app.route('/otazky/zobrazit/<id>', methods=['GET'])
@prihlasit('ucitel')
@db_session
def otazka_zobrazit(id):
    return Otazka.zobraz(id)

@app.route('/otazky/editovat/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def otazka_editovat(id):
    return Otazka.editovat(id)

@app.route('/otazky/smazat/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def otazka_smazat(id):
    return Otazka.smazat(id)

@app.route('/pridat/otazku/', methods=['GET', 'POST'])
@prihlasit('ucitel')
def pridat_otazku():  
    return Otazka.pridat()

@app.route('/testy/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def testy():
    return Testy.zobraz()

@app.route('/pridat/test/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def pridat_test():
    return Testy.pridat()

@app.route('/testy/<id_test>', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def uprav_test(id_test):
    return Testy.uprav(id_test)

@app.route('/student/testy/', methods=['GET', 'POST'])
@prihlasit('student')
@db_session
def student_testy():
    return Student.testy()

@app.route('/student/testy/<id>', methods=['GET', 'POST'])
@prihlasit('student')
@db_session
def student_zobrazit(id):
    return Student.zobrazit(id)

@app.route('/student/vysledky/')
@prihlasit('student')
@db_session
def student_vysledek(): 
    return Student.vysledky()

@app.route('/upload/', methods=['GET', 'POST'])
@prihlasit('ucitel')
@db_session
def upload():  
    return upload1()


@app.errorhandler(404)
def nenalezeno(ch):
    return render_template('404.html', e=ch), 404


# json test
@app.route('/test/')
def ttt():  
    js= ['gggg', {'hhhh': ('bbb', None, 1.5, 2)}]

    jsf = {
        'seznam': [1, 2, 3, 'test'],
        12: "abc",
    }

    return Response(response=json.dumps(js),status=200,mimetype="application/json")

@app.route('/test2/')
def tt():
     return render_template('ajax.html')



