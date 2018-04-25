from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from pony.orm import (sql_debug, get, select, db_session)
from werkzeug.routing import BaseConverter
from flask_socketio import disconnect
from datetime import datetime as dt
from markdown import markdown

from .. import socketio as ws
from .db import *

import functools
import psycopg2
import operator
import random
import time
import sys
import os
import re

from .funkce import (pswd_check, json, wsJSON, ted, Zaznamy, uzivatel, uzJmeno)

studenti = []
ucitele = []
# socket IO
nm = "/ws"

class Uzivatel:
    def index():
        if uzivatel("ucitel") or uzivatel("admin") or uzivatel("student"):
            Uzivatel.prihlasit(True)

        return render_template('base.html')

    def prihlasit(prihlasen = False):
        J = request.json
        login = ""
        heslo = ""

        if prihlasen:
            login = uzJmeno()

        else:
            login = J["login"]
            heslo = J["heslo"]
        
        uzivatel = "nikdo"
        html = None
        info = None

        if login == "admin": Uzivatel.admin()

        student = get(s for s in DbStudent if s.login == login)
        ucitel = get(u for u in DbUcitel if u.login == login)

        if student and student.hash and pswd_check(heslo, student.hash):
            uzivatel = "student"
            if not prihlasen:
                session['jmeno'] = login
                session['typ'] = "student"
            Zaznamy.pridat("prihlaseni", login)
        elif ucitel and ucitel.hash and pswd_check(heslo, ucitel.hash):
            uzivatel = "učitel"
            if ucitel.admin:
                uzivatel = "admin"
                if not prihlasen:    
                    session['jmeno'] = login
                    session['typ'] = "admin"   
            else:
                uzivatel = "učitel"
                if not prihlasen: 
                    session['jmeno'] = login
                    session['typ'] = "ucitel"   
        else:  # špatně
            info = "Špatné jméno nebo heslo"
            Uzivatel.poslatZaznam("ŠH: " + login)

        vysledek = {
            "prihlasen": uzivatel, 
            "uzivatel": login,
            "html": "",
            "info": info,
            "spojeni": "a",
        }

        return json(vysledek)

    def odhlasit():
        if "jmeno" in session:
            session.pop('jmeno', None)
        if "typ" in session:
            session.pop('typ', None)          
        return json({"odpoved": "odhlaseno"})

    def zaznamenat(z):
        jmeno = ""
        trida = ""
        login = ""
        typ = "neznamy"
        sid = request.sid

        if uzivatel("student"):
            student = get(s for s in DbStudent if s.login == uzJmeno())
            jmeno = student.prijmeni
            login = student.login
            typ = "student"
            Zaznamy.pridat("prihlaseni",uzJmeno())

            if student.trida:
                tridy = get(t for t in DbTridy if t.id is student.trida.id)         
                trida = str(tridy.poradi) + tridy.nazev
        
        if uzivatel("ucitel"):
            ucitel = get(u for u in DbUcitel if u.login == uzJmeno())  
            typ = "ucitel"   
            jmeno = ucitel.prijmeni
            login = ucitel.login
        elif uzivatel("admin"):
            ucitel = get(u for u in DbUcitel if u.login == uzJmeno())
            typ = "admin"
            jmeno = ucitel.prijmeni
            login = ucitel.login

        # odpoji neznameho uzivatele
        if typ == "neznamy":
            ws.emit("uzivatelOdpojen","neznamy",namespace=nm,room=sid)
            try: disconnect(sid,nm)
            except: True
            return           

        prihlaseniInfo = {
            "sid": sid,
            "login": login,
            "jmeno": jmeno,
            "typ": typ,
            "trida": trida,
            "casPrihlaseni": ted()
        }

        if uzivatel("ucitel") or uzivatel("admin"):
            ucitele.append(prihlaseniInfo) 
            #ws.emit("odpoved","ucitelPrihlasen: " + str(ucitele),namespace=nm)
            ucitel = get(u for u in DbUcitel if u.login == uzJmeno())  
            Uzivatel.odpojLogin(ucitel.login)
        elif uzivatel("student"):
            studenti.append(prihlaseniInfo)
            Uzivatel.poslatZaznam("prihlasen")
            student = get(s for s in DbStudent if s.login == uzJmeno())
            Uzivatel.odpojLogin(student.login)

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
        if uzivatel('ucitel') or uzivatel('admin'):
            return
        
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

    # odpoji uzivatele se stejnym loginem, krome posledniho prihlaseneho (podle datumu)
    def odpojLogin(login):
        # odfiltruji se ostatni loginy

        #ws.emit("odpoved","Bude odpojen: " + login,namespace=nm,broadcast=True)   


        filtr = [u for u in studenti if u["login"] == login]
        
        # seradi se podle casu prihlaseni
        for student in sorted(filtr, key=operator.itemgetter("casPrihlaseni")):
            # odpojit dokud nezustane jen 1 prihlaseny login
            if len(filtr) > 1:
                filtr.remove(student)                   
                Uzivatel.odpojUzivatele(student["sid"])

        # odfiltruji se ostatni loginy
        filtr = [u for u in ucitele if u["login"] == login]

        # seradi se podle casu prihlaseni
        for ucitel in sorted(filtr, key=operator.itemgetter("casPrihlaseni")):
            # odpojit dokud nezustane jen 1 prihlaseny login
            if len(filtr) > 1:
                filtr.remove(ucitel)                  
                Uzivatel.odpojUzivatele(ucitel["sid"]) 

    # prida admina pokud jeste neexistuje
    def admin():
        jmeno = "admin"
        admin = get(u for u in DbUcitel if u.login == jmeno)
        
        if admin: 
            admin.admin = True
            return

        DbUcitel(
            login = jmeno,
            jmeno = jmeno,
            prijmeni = jmeno,
            hash = "1111",
            admin = True
        )

    def ucet():
        student = get(s for s in DbStudent if s.login == uzJmeno())
        ucitel = get(u for u in DbUcitel if u.login == uzJmeno())
        
        info = {}
        trida = "-"

        if student:
            if student.trida:
                tridy = get(t for t in DbTridy if t.id is student.trida.id)         
                trida = str(tridy.poradi) + tridy.nazev

            info = {
                "login": student.login, 
                "jmeno": student.jmeno,
                "prijmeni": student.prijmeni,
                "trida": trida,
                "student": True
            }
        
        elif ucitel:
           info = {
                "login": ucitel.login, 
                "jmeno": ucitel.jmeno,
                "prijmeni": ucitel.prijmeni,
                "trida": "-",
                "student": False
            }

        return json({"prihlasen": info})