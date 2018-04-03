from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
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

        studentHash = get(s.hash for s in DbStudent if s.login == login)
        ucitelHash = get(u.hash for u in DbUcitel if u.login == login)

        if studentHash and pswd_check(heslo, studentHash):
            prihlasen = "student"
            session['student'] = login
            Zaznamy.pridat("prihlaseni", login)
            html = render_template('studentMenu.html')
        elif ucitelHash and pswd_check(heslo, ucitelHash):
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

        pocet = len(ucitele) + len(studenti)
        #posle vsem zpravu o poctu prihlasenych uzivatelu
        ws.emit('pocet', str(pocet), namespace=nm, broadcast=True)

    # ukonci spojeni WS a smaze ze seznamu prihlasenych
    def smazatSpojeni(z):
        sid = request.sid

        for p in ucitele:
            if sid in p.values(): 
                ucitele.remove(p)

        for p in studenti:
            if sid in p.values():
                Uzivatel.poslatZaznam("odhlasen") 
                studenti.remove(p)
        
        pocet = len(ucitele) + len(studenti)
        
        Uzivatel.zobrazPrihlasene()
        ws.emit('pocet', str(pocet), namespace=nm, broadcast=True)

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