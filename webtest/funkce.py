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
    if text[:1] != "=": return text
    text=text[1:]

    #nahradi promenne ze zadani jeji hodnotou
    for promenna, hodnota in sorted(promenne.items()):
        text = text.replace("§" + promenna, hodnota)
    
    #vypocita zadany vyraz s dosazenyma hodnotama
    vysledek = sympy.simplify(text)
    return str(vysledek)

def json(js):
    return Response(response=_json.dumps(js),status=200,mimetype="application/json")

def jsonStahnout(js,jmeno):
    js = _json.dumps(js,sort_keys = True, indent = 1, ensure_ascii=False)
    js = js.replace('\n', '\r\n')
    r = Response(response=js,status=200,mimetype="application/json")
    r.headers["Content-Disposition"] = 'attachment; filename="' + jmeno + '"'
    return r

def upload1():
    """upload souboru se zadáním
    """
    def add(typ, nazev_otazky, cislo, otazka, spravna, spatna):
        """zapis do databaze
        """
        ucitel = get(u for u in Ucitel if u.login == session['ucitel'])
        while len(spatna) < 7:  # doplni hodnoty NULL do nevyuzitych mist
            spatna.append('Null')

        # prevede polozky seznamu na UNICODE
        spatna = [unicode(i) for i in spatna]
        DbOtazka(ucitel=ucitel, 
               jmeno=nazev_otazky, 
               typOtazky=typ,
               obecneZadani='10', 
               SprO=spravna,
               SPO1=spatna[0],
               SPO2=spatna[1],
               SPO3=spatna[2],
               SPO4=spatna[3],
               SPO5=spatna[4],
               SPO6=spatna[5])
        # Obecne_zadani nastaveno perma na 10

    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        if 'datafile' in request.files:
            fil = request.files['datafile']
            typ = cislo = nazev_otazky = otazka = spravna = ""
            spatna = []  # seznam spatnych odpovedi
            for line in fil:
                radek = line.strip().decode('UTF-8')
                if line != '\n':  # ignoruj prazdne radky
                    if radek.split()[0] == '::date':
                        #  datum = " ".join(radek.split()[1:])
                        pass
                    elif radek.split()[0] == '::number':
                        typ = 'C'
                        spravna = " ".join(radek.split()[1:])
                    elif radek.split()[0] == ':+':
                        spravna = " ".join(radek.split()[1:])
                    elif radek.split()[0] == ':-':
                        spatna.append(radek.split()[1:])
                    elif radek.split()[0] == '::task':
                        nazev_otazky = " ".join(radek.split()[1:])
                    elif radek.split()[0] == '::open':
                        typ = 'O'
                    elif radek.split()[0] == '::close':
                        typ = 'U'
                    else:
                        otazka = otazka + line
                else:  # kdyz je mezera(oddeleni otazek), udelej zapis do DB
                    # ignoruj 1.mezeru či  nekor. otazky
                    if nazev_otazky and otazka:
                        add(typ, nazev_otazky, cislo, otazka, spravna, spatna)
                    # vynuluj
                    typ = nazev_otazky = cislo = otazka = spravna = ""
                    spatna = []
        return redirect(url_for('upload'))

class Prihlaseni:
    def prihlasit():
        if request.method == 'GET':
            with db_session:
                if 'student' in session:
                    student = get(s for s in DbStudent
                                if s.login == session['student'])
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
