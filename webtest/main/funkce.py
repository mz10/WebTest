from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
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
import math
import cgi

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

def prihlasit(klic1, klic2=""):
    #Dekoruje funkce, které vyžadují přihlášení
    #@prihlasit(klic)
    #klic: je klic ve slovniku session, který se kontroluje.
    
    def decorator(function): 
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if "typ" in session and (session["typ"] == klic1 or session["typ"] == klic2):
                return function(*args, **kwargs)
            else:
                return redirect(url_for('.login'))
        return wrapper
    return decorator

def prihlasitJSON(klic1, klic2=""):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if "typ" in session and (session["typ"] == klic1 or session["typ"] == klic2):
                return function(*args, **kwargs)
            else:
                return "neprihlasen"
        return wrapper
    return decorator

def prihlasitJSON2(klic1, klic2=""):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):           
            if "typ" in session and (session["typ"] == klic1 or session["typ"] == klic2):
                return function(*args, **kwargs)
            else:
                return wsJSON({"chyba":"neprihlasen"})
        return wrapper
    return decorator

def uzivatel(typ):
    if not "typ" in session: 
        return False
    if session["typ"] == typ:
        return True
    
    return False

def uzJmeno():
    if not "jmeno" in session: return "" 
    return session["jmeno"]   

def pswd_check(pswd, encript):
    return True   

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

            #pokusi se zaokrouhlit vyraz na max 4 mista
            try:    
                vyraz = float(vyraz)
                vyraz = ('%.14f' % round(vyraz,4)).rstrip('0').rstrip('.')
            except: True
            
            return vyraz

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

def datum(d):
    if d:
        return d.strftime(formatCasu)
    return None

def delka(p):
    if p: return len(p)
    return 0

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

    def seznamUcitelu():
        ucitele = select(s for s in DbUcitel).sort_by("s.id")
        seznam = []

        for ucitel in ucitele:
            seznam.append({
                "id":       ucitel.id,
                "login":    ucitel.login,
                "jmeno":    ucitel.jmeno,
                "prijmeni": ucitel.prijmeni,
                "admin":    ucitel.admin
            })
            
        return json({"ucitele": seznam})

    def zmenObsah(J):
        if J["tabulka"] != "Ucitel":
            return "Nemáš oprávnění měnit obsah této tabulky!!!"
        
        admin = False
        if J["bunky"][3] == "true": admin = True

        # zkontroluje, jestli uz v tabulkach neni stejny login
        login = J["bunky"][0]
        ucitel = get(s.id for s in DbUcitel if s.login == login)
        student = get(s.id for s in DbStudent if s.login == login)

        if J["id"] == "":
            if (student or ucitel):
                return "Tento login už existuje!"

            DbUcitel(
                login = login,
                jmeno =  J["bunky"][1],
                prijmeni = J["bunky"][2],
                admin = admin
            )

            return "Byl přidán nový učitel."

        id = int(J["id"])

        dbId = get(o.id for o in DbUcitel if o.id is id)

        if not dbId:
            return "Toto id neexistuje!"

        ucitel = DbUcitel[id]

        if J["akce"] == "smazat":
            ucitel.delete()
            return "Učitel byl smazán"

        elif J["akce"] == "zmenit":
            ucitel.login = login
            ucitel.jmeno = J["bunky"][1]
            ucitel.prijmeni = J["bunky"][2]
            ucitel.admin = admin

            return "Učitel byl změněn."

        return "Chyba - záznam nebyl přidán."

class Zaznamy:
    def pridat(typ,student):
        DbAkce(
            cas = ted(),
            typAkce = typ,
            student = get(s.id for s in DbStudent if s.login == student)
        )