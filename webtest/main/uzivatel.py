from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from flask_socketio import disconnect

from .db import *
from .. import socketio as ws

import psycopg2
import time
import os
import functools
import random
import sys
import re

from .funkce import (pswd_check, json, wsJSON, ted, Zaznamy)

studenti = []
ucitele = []
# socket IO
nm = "/ws"

class Uzivatel:
    def prihlasit():
        J = request.json
        login = J["login"]
        heslo = J["heslo"]
        
        prihlasen = "nikdo"
        html = None
        info = None

        student = get(s for s in DbStudent if s.login == login)
        ucitel = get(u for u in DbUcitel if u.login == login)

        if student and student.hash and pswd_check(heslo, student.hash):
            Uzivatel.odpojLogin(student.login, student.prijmeni)
            prihlasen = "student"
            session['student'] = login
            Zaznamy.pridat("prihlaseni", login)
            html = render_template('studentMenu.html')
        elif ucitel and ucitel.hash and pswd_check(heslo, ucitel.hash):
            Uzivatel.odpojLogin(ucitel.login, ucitel.prijmeni)
            prihlasen = "učitel"
            session['ucitel'] = login
            html = render_template('ucitelMenu.html')
        else:  # špatně
            info = "Špatné jméno nebo heslo"
            Uzivatel.poslatZaznam("ŠH: " + login)

        vysledek = {
            "prihlasen": prihlasen, 
            "uzivatel": login,
            "html": html,
            "info": info,
            "spojeni": "a",
        }

        return json(vysledek)

    def zobraz():
        if 'student' in session:
            student = get(s for s in DbStudent if s.login == session['student'])
            return render_template('login.html', jmeno=student.jmeno)
        elif 'ucitel' in session:
            ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
            return render_template('login.html', jmeno=ucitel.jmeno)
        else:
            return render_template('login.html')

    def odhlasit():
        if 'student' in session:
            session.pop('student', None)
        elif 'ucitel' in session:
            session.pop('ucitel', None)
        return json({"odpoved": "odhlaseno"})

    def zaznamenat(z):
        jmeno = ""
        trida = ""
        login = ""
        typ = "neznamy"
        sid = request.sid

        if 'student' in session:
            student = get(s for s in DbStudent if s.login == session['student'])
            jmeno = student.prijmeni
            login = student.login
            typ = "student"
            Zaznamy.pridat("prihlaseni",session['student'])

            if student.trida:
                tridy = get(t for t in DbTridy if t.id is student.trida.id)         
                trida = str(tridy.poradi) + tridy.nazev
        
        elif 'ucitel' in session:
            ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
            jmeno = ucitel.prijmeni
            login = ucitel.login
            typ = "ucitel"

        prihlaseniInfo = {
            "sid": sid,
            "login": login,
            "jmeno": jmeno,
            "typ": typ,
            "trida": trida,
            "casPrihlaseni": ted()
        }

        if 'ucitel' in session:
            ucitele.append(prihlaseniInfo)
        else:
            studenti.append(prihlaseniInfo)
            Uzivatel.poslatZaznam("prihlasen")

        Uzivatel.zobrazPrihlasene()
        Uzivatel.pocetPrihlasenych()

    # ukonci spojeni WS a smaze ze seznamu prihlasenych
    def smazatSpojeni(z):
        sid = request.sid

        for p in ucitele:
            if sid in p["sid"]:
                ucitele.remove(p)

        for p in studenti:
            if sid in p["sid"]:
                Uzivatel.poslatZaznam("odhlasen") 
                studenti.remove(p)
        
        Uzivatel.zobrazPrihlasene()
        Uzivatel.pocetPrihlasenych()

        disconnect()
        
    def poslatZaznam(z):
        if 'ucitel' in session: return
        
        student = {}

        for s in studenti:
            if s["sid"] == request.sid:
                student = s

        if z == "s": z = "skryto"
        elif z == "z": z = "zobrazeno"
        elif z == "f": z = "aktivni"
        elif z == "b": z = "neaktivni"

        student.update({
            "akce":z,
            "casAkce": ted()
        })

        for u in ucitele:
            ws.emit("log",wsJSON(student),namespace=nm,room=u["sid"])

    def zobrazPrihlasene():
        prihlaseni = ucitele + studenti
        
        for u in ucitele:
            ws.emit("uzivatele",wsJSON(prihlaseni),namespace=nm,room=u["sid"])

    def odpojUzivatele(sid,osoba="neznamy"):
        odstraneno = False    
        sidUcitele = None
        
        if hasattr(request, 'sid'):
            sidUcitele = request.sid

        # najde jmeno ucitele ktery to odpojil
        for p in ucitele:
            if sidUcitele and sidUcitele in p["sid"]:
                osoba = p["jmeno"]
                break
        
        for p in ucitele:          
            if sid in p["sid"]: 
                ucitele.remove(p)
                odstraneno = True

        for p in studenti:
            if sid in p["sid"]:
                studenti.remove(p)
                odstraneno = True

        if not odstraneno: return

        #odpojit uzivatele
        ws.emit("uzivatelOdpojen",osoba,namespace=nm,room=sid)       
        
        #poslat tabulku prihlasenych
        Uzivatel.zobrazPrihlasene()

        Uzivatel.pocetPrihlasenych()

        # funkce by mela prijimat 2 parametry
        # s "nm" vypise chybu, ale vysledek je spravny,
        # bez "nm" by odpojila aktualniho uzivatele
        try: disconnect(sid,nm)
        except: False

    #posle vsem zpravu o poctu prihlasenych uzivatelu
    def pocetPrihlasenych():
        pocet = len(ucitele) + len(studenti)
        ws.emit('pocet', str(pocet), namespace=nm, broadcast=True)

    # odpoji uzivatele se stejnym loginem
    def odpojLogin(login,osoba):
        for p in studenti:
            if login in p["login"]:
                Uzivatel.odpojUzivatele(p["sid"],osoba)
        
        for p in ucitele:
            if login in p["login"]:
                Uzivatel.odpojUzivatele(p["sid"],osoba)