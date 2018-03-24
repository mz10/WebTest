from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt

from webtest.db import *

import psycopg2
import time
import os
import functools
import random
import sys
import re
import json as _json
import sympy
from sympy import init_printing
init_printing()

"""
def pswd_check(pswd, encript):
    i = encript.rfind('$')
    salt = encript[:i]
    return encript == crypt(pswd, salt)
"""

############################################################################

def pswd_check(pswd, encript):
    return True   

def vysledky1():
    if request.method == 'GET':
        seznam_testu = select((u.jmeno, u.id) for u in DbTest)
        return render_template('vysledky.html', seznam_testu=seznam_testu)

def nahodne(a,b):
    return str(random.randint(a,b))

def vypocitej(text,promenne):
    #najde a vypocita vyraz v [ ]
    def nahraditVyrazy(m):
        vyraz = m.group(1)

        #nahradi promenne ze zadani a dosadi jeji hodnotou
        for promenna, hodnota in sorted(promenne.items()):
            vyraz = vyraz.replace("$" + promenna, hodnota)    
        try:
            vyraz = re.compile("Prumer\((.*?)\)").sub(prumer,vyraz)
            vyraz = str(sympy.simplify(vyraz))
        except:
            return "[Sympy - chybny vyraz]"    
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

def seznam(s):
    vysledek = []
    for polozky in s:
        vysledek.append(polozky)

    return vysledek

class Prihlaseni:
    def prihlasit():
        if request.method == 'GET':
            with db_session:
                if 'student' in session:
                    student = get(s for s in DbStudent if s.login == session['student'])
                    Zaznamy.pridat("prihlaseni",session['student'])
                    return render_template('login.html', jmeno=student.jmeno)
                elif 'ucitel' in session:
                    ucitel = get(u for u in DbUcitel
                                if u.login == session['ucitel'])
                    return render_template('login.html', jmeno=ucitel.jmeno)
            if 'url' in request.args:
                return render_template('login.html', url=request.args['url'])
            else:
                return render_template('login.html')
        elif request.method == 'POST':
            login = request.form['login']
            heslo = request.form['passwd']
            with db_session:
                student_hash = get(s.hash for s in DbStudent if s.login == login)
                ucitel_hash = get(u.hash for u in DbUcitel if u.login == login)
            if student_hash and pswd_check(heslo, student_hash):
                session['student'] = login
                with db_session:
                    Zaznamy.pridat("prihlaseni",session['student'])
                if 'url' in request.form:
                    return redirect(request.form['url'])
                else:
                    return redirect(url_for('index'))
            elif ucitel_hash and pswd_check(heslo, ucitel_hash):
                session['ucitel'] = login
                if 'url' in request.form:
                    return redirect(request.form['url'])
                else:
                    return redirect(url_for('index'))
            else:  # špatně
                if 'url' in request.form:
                    return render_template('login.html', spatne=True,
                                        url=request.form['url'])
                else:
                    return render_template('login.html', spatne=True)

    def odhlasit():
        if 'student' in session:
            session.pop('student', None)
        elif 'ucitel' in session:
            session.pop('ucitel', None)
        return redirect(url_for('login'))

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

class Slovnik:
    def pridat(J):
        DbSlovnik(
            slovo1 = J["slovo1"],
            slovo2 = J["slovo2"],
            kategorie = J["kategorie"],           
            jazyk = J["jazyk"]
        )
        
        return

    def nahrat(J):
        text = J["data"].split("\n")
        for radek in text:
            bunka = radek.split(";")       
            if len(bunka) < 4: continue
            
            DbSlovnik(
                slovo1 = bunka[0],
                slovo2 = bunka[1],
                kategorie = bunka[2],         
                jazyk = bunka[3]
            )            
        return "CSV soubor byl úspěšně nahrán"


    def stahnout():
        slovnik = select((s.slovo1, s.slovo2, s.kategorie, s.jazyk) for s in DbSlovnik).order_by(3)
        csv = '\ufeff'

        for sloupec in slovnik:
            csv += sloupec[0] + ";" + sloupec[1] + ";" + sloupec[2] + ";" + sloupec[3] + "\r\n"

        r = Response(response=csv,status=200,mimetype="text/plain")
        r.headers["Content-Disposition"] = 'attachment; filename="slovnik.csv"'
        return r

class Trida:
    def pridat(J):
        DbTridy(
            poradi = int(J["poradi"]),
            nazev = J["nazev"],
            rokUkonceni = J["rok"]
        )

        return "Třída byla přidána"

    def zobraz():
        seznamTrid = []
        tridy = select(t for t in DbTridy).order_by(1)

        for trida in tridy:
            seznamTrid.append({
                'id':           trida.id,
                'poradi':       trida.poradi,
                'nazev':        trida.nazev,
                'rokUkonceni':  trida.rokUkonceni
            })

        return json({"tridy": seznamTrid})

class Zaznamy:
    def pridat(typ,student):
        DbAkce(
            cas = dt.now().strftime("%d.%m.%Y %H:%M:%S"),
            typAkce = typ,
            student = get(s.id for s in DbStudent if s.login == student)
        )