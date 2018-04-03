from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt

from .db import *

import psycopg2
import time
import os
import functools
import random
import sys
import re
import json as _json
import sympy

from decimal import Decimal
from sympy import init_printing, Symbol
from sympy.solvers import solve

init_printing()

"""
def pswd_check(pswd, encript):
    i = encript.rfind('$')
    salt = encript[:i]
    return encript == crypt(pswd, salt)
"""
############################################################################

formatCasu = "%d.%m.%Y %H:%M"

def prihlasit(klic):
    #Dekoruje funkce, které vyžadují přihlášení
    #@prihlasit(klic)
    #klic: je klic ve slovniku session, který se kontroluje.
    
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
                return "neprihlasen"
        return wrapper
    return decorator

def prihlasitJSON2(klic):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if klic in session:
                return function(*args, **kwargs)
            else:
                return wsJSON({"chyba":"neprihlasen"})
        return wrapper
    return decorator

def pswd_check(pswd, encript):
    return True   

def vysledky1():
    if request.method == 'GET':
        seznam_testu = select((u.jmeno, u.id) for u in DbTest)
        return render_template('vysledky.html', seznam_testu=seznam_testu)

def nahodne(a,b):
    return str(random.randint(a,b))

def ted():
    return dt.now().strftime("%d.%m.%Y %H:%M:%S")

def vypocitej(text,promenne):
    #najde a vypocita vyraz v [ ]
    def nahraditVyrazy(m):
        vyraz = m.group(1)
        priklad = True

        #nahradi promenne ze zadani a dosadi jeji hodnotou
        for promenna, hodnota in sorted(promenne.items()):
            # pokud promenna obsah seznam           
            if type(hodnota) is list:
                priklad = False
                if len(hodnota) >= 1:
                    hodnota = hodnota[0]
                    # odebere pridane slovo ze seznamu
                    promenne[promenna].pop(0)
                else:
                    hodnota = "[Chyba: málo slov v DB]"

            vyraz = vyraz.replace("$" + promenna, hodnota)  

        if not priklad:
            return vyraz

        try:
            #vykona funkci prumer pokud je zadana
            vyraz = re.compile("Prumer\((.*?)\)").sub(prumer,vyraz)
            #zjednodusi vyraz
            vyraz = str(sympy.simplify(vyraz))
            #nahradi mocninu v pythonu, aby se zobrazila spravne v MathJax
            vyraz = vyraz.replace("**", "^")
        except NameError:
            return vyraz
        except Exception as e:
            return "[Sympy - chybný výraz]"
        return vyraz   
    
    def prumer(m):
        cisla = m.group(1).split(","); 
        soucet=0
        for c in cisla:
            soucet += float(c)

        return str(float(soucet/len(cisla)))

    #regularni vyraz - funkce nahore
    text = re.compile("\[(.*?)\]").sub(nahraditVyrazy,text)
    return str(text)

def json(js):
    return Response(response=_json.dumps(js),status=200,mimetype="application/json")

def jsonStahnout(js,jmeno):
    js = _json.dumps(js,sort_keys = True, indent = 1, ensure_ascii=False)
    js = js.replace('\n', '\r\n')
    r = Response(response=js,status=200,mimetype="application/json")
    r.headers["Content-Disposition"] = 'attachment; filename="' + jmeno + '"'
    return r

def wsJSON(js):
    return _json.dumps(js)


def seznam(s):
    vysledek = []
    for polozky in s:
        vysledek.append(polozky)

    return vysledek

def chyba(ch):
    return json({'chyba': ch})

def naDesetinne(text,mista):
    text = text.replace(",",".")
    cislo = 0
    
    try:
        cislo = float(text)
    except:
        cislo = 0
        
    cislo = Decimal(cislo)
    
    return round(cislo,mista)

class Ucitel:
    def zobrazTest(id):
        """zobrazi obsah vyplneneho testu studenta"""
        if request.method == 'GET':
            otazky = select((u.konkretni_zadani, u.ocekavana_odpoved,
                            u.konkretniOdpoved,
                            u.otazkaTestu.otazka.typOtazky) for u in Odpoved if
                
                            u.vysledek_testu.id is id)[:]
            print(otazky)
            return render_template('student_vysledky_zobraz.html', otazky=otazky)


    def vyplneno(id):
        """seznam uzivatelu, kteri vyplnili test"""
        if request.method == 'GET':
            nazev_testu = get(u.jmeno for u in DbTest if u.id is id)
            seznam_zaku = select((u.student.jmeno, u.id, u.casUkonceni) for u in
                                DbVysledekTestu if u.test.id is id)
            return render_template('vypracovane_testy.html', seznamZaku=seznam_zaku, nazevTestu=nazev_testu)

    def vysledky():
        if request.method == 'GET':
            seznam_testu = select((u.jmeno, u.id) for u in DbTest)
            return render_template('vysledky.html', seznamTestu=seznam_testu)

class Zaznamy:
    def pridat(typ,student):
        DbAkce(
            cas = ted(),
            typAkce = typ,
            student = get(s.id for s in DbStudent if s.login == student)
        )