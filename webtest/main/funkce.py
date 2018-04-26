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

formatCasu = "%d.%m.%Y %H:%M:%S"

def prihlasit(klic1, klic2="", klic3=""):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if "typ" in session and (session["typ"] == klic1 or \
                    session["typ"] == klic2 or session["typ"] == klic3):
                return function(*args, **kwargs)
            else:
                return "neprihlasen"
        return wrapper
    return decorator

def prihlasitWS(klic1, klic2="", klic3=""):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):           
            if "typ" in session and (session["typ"] == klic1 or \
                    session["typ"] == klic2 or session["typ"] == klic3):
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

# vytvori nahodne cislo s promenlivou delkou
def nahodne(a,b):
    cislo = random.randint(a,b)
    delkaOd = abs(a).__str__().__len__()
    delkaDo = abs(cislo).__str__().__len__()
    delka = abs(delkaOd - delkaDo)
    nahodnaDelka = random.randint(0,delka)
    return str(int(cislo/(10**nahodnaDelka)))

# vytvori nahodne desetinne cislo s promenlivou delkou
def nahodneDes(a,b):
    cislo = random.uniform(a,b)
    delkaOd = abs(int(a)).__str__().__len__()
    delkaDo = abs(int(cislo)).__str__().__len__()
    delka = abs(delkaOd - delkaDo)
    nahodnaDelka = random.randint(0,delka)
    cislo = cislo/(10**nahodnaDelka)
    return str(cislo)

def zaokrouhlit(cislo,mista):
    cislo = float(cislo)
    try: mista = int(mista)
    except: mista = 0
    return ('%.10f' % round(cislo,mista)).rstrip('0').rstrip('.')

# zaokrouhli cislo na pocet platnych mist
def platneMista(cislo, mista=0):   
    cislo = float(cislo)
    try: mista = int(mista)
    except: mista = 0       
    if mista <= 0: return cislo
    
    return round(cislo, mista-int(math.floor(math.log10(abs(cislo))))-1)

def ted():
    return dt.now().strftime("%d.%m.%Y %H:%M:%S")

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

def dtRozdil(od,do):
    r = abs(do - od)
    dnu = str(r.days) + "d, "
    hodin = r.seconds//3600
    minut = (r.seconds - hodin*3600)//60
    sekund = r.seconds - (hodin*3600 + minut*60)

    hodin = str(hodin) + "h, "
    minut = str(minut) + "m, "
    sekund = str(sekund) + "s"

    zprava = "Test bude možné spustit za: "

    return zprava + dnu + hodin + minut + sekund

# zkontroluje zadanou odchylku v % 2 cisel
def tolerance(c1,c2,procent):
    odchylka = 0
    
    if c1 == c2:
        odchylka = 100    
    elif c1 < c2 and c2 != 0:
        odchylka = (c1/c2)*100
    elif c2 < c1 and c1 != 0:
        odchylka = (c2/c1)*100
        
    if 100-odchylka <= procent:
        return True
        
    return False

def spVypocitat(vyraz):
    #return str(sympy.latex(sympy.N(vyraz)))
    return str(sympy.N(vyraz))

def prumer(cisla):
    if cisla[0] == "": return 0
    soucet = 0
    for c in cisla:
        soucet += float(c)
    return str(float(soucet/len(cisla)))




def rovnice(zadani):
    strana2 = "0"
    if len(zadani) == 2:
       strana2 = zadani[1] 

    rovnice = "Eq(%s,%s)" % (zadani[0], strana2)
    vysledek = sympy.N(sympy.solveset(rovnice)) 
    vysledek = list(vysledek)
    
    if len(vysledek) > 1:
        return vysledek[1]
    else:
        return vysledek[0]

# velikosti jednotek
velikosti = {
                "y": -24,                
                "z": -21,
                "a": -18,    
                "f": -15,
                "p": -12,
                "n":  -9,
                "µ":  -6,
                "m":  -3,
                "":   0,
                "k":   3,
                "M":   6,
                "G":   9,
                "T":  12,
                "P":  15,
                "E":  18,
                "Z":  21,
                "Y":  24,
}

# prevede cislo na nejakou jednotku - napr mV, MB, A, ...
def jednotka(cislo,typ, mista = -1):  
    cislo = float(cislo)
    try: mista = int(mista)
    except: mista = 0
    typ = typ.replace("u","µ")

    mocnina = 0
    velikost = "" 
    
    # najde velikost jednotky - k, M, G ...
    # a priradi mocninu
    # typ muze obsahovat napr. "mV", "A", "kB", ...
    if len(typ) == 2:
        velikost = typ[0]
        typ = typ[1]
        if velikost in velikosti:
            mocnina = velikosti[velikost] 
    
    # desetinne cislo
    if cislo > -1 and cislo < 1:
        while cislo > -1 and cislo < 1:
            cislo = cislo*1000    
            mocnina -= 3        
    
    # velke cislo nad 1000
    if cislo <= -1000 or cislo >= 1000:
        while cislo <= -1000 or cislo >= 1000:
            cislo = cislo/1000    
            mocnina += 3
      
    # priradi velikost pred hlavni jednotku
    for klic, vel in velikosti.items():
        if velikosti[klic] == mocnina:
            velikost = klic
            break

    if mista >= 0:
        cislo = platneMista(cislo,mista) 

    return str(cislo) + " " + velikost + typ

# opak k funkci jednotka - prevede zpet na cislo
def jednotka2(text, mista = -1):
    try: mista = int(mista)
    except: mista = 0

    parametry = text.split(" ")
    cislo = float(parametry[0])
    typ = ""
    velikost = ""
    mocnina = 0 
    
    if len(parametry) >= 2: typ = parametry[1]   
    if len(typ) >=1: velikost = typ[0]
    
    if velikost in velikosti:
        mocnina = velikosti[velikost] 
         
        cislo = cislo*(10**mocnina)
        
    if mista >= 0:
        cislo = platneMista(cislo,mista)        
        
    return str(cislo)

class Zaznamy:
    def pridat(typ,student):
        DbAkce(
            cas = ted(),
            typAkce = typ,
            student = get(s.id for s in DbStudent if s.login == student)
        )