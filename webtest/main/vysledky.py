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

from collections import defaultdict
from .funkce import (json, wsJSON, ted, Zaznamy, datum, uzivatel, uzJmeno)

class Vysledky:
    def zobrazVysledek(id,vysledek):
        if not vysledek:
            vysledek = get(v for v in DbVysledekTestu if v.id is id)

        procent = 0
        if vysledek.boduMax != 0:
            procent = 100*vysledek.boduVysledek/vysledek.boduMax

        trida = "-"
        if vysledek.student and vysledek.student.trida:
            trida = str(vysledek.student.trida.poradi) + vysledek.student.trida.nazev

        cas = "-"

        if vysledek.casUkonceni:
            cas = vysledek.casUkonceni - vysledek.casZahajeni

            hodiny =  cas.seconds//3600
            minuty = (cas.seconds -  hodiny*3600)//60
            sekundy = cas.seconds - (hodiny*3600 + minuty*60)

            if minuty  < 10: minuty  = "0" + str(minuty)
            if sekundy < 10: sekundy = "0" + str(sekundy)

            if hodiny > 0: cas = str(hodiny) + ":" + minuty + ":" + sekundy
            else:          cas = str(minuty) + ":" + str(sekundy)  

        info = {
            'id':               vysledek.id,
            'jmeno':            vysledek.jmeno,
            'casZahajeni':      datum(vysledek.casZahajeni),
            'casUkonceni':      datum(vysledek.casUkonceni),
            'limit':            vysledek.limit,
            'cas':              cas,
            'pokus':            vysledek.pokus,
            'boduVysledek':     vysledek.boduVysledek,
            'boduMax':          vysledek.boduMax,
            'procent':          procent,          
            'znamka':           vysledek.znamka,        
            'student': {
                'id':               vysledek.student.id,
                'login':            vysledek.student.login,
                'prijmeni':         vysledek.student.prijmeni,
                'trida':            trida
            }
        }

        return info
  
    def test(id):       
        vysledky = select(v for v in DbVysledekTestu if v.test.id is id)
        seznam = []

        for vysledek in vysledky:
            tId = vysledek.test.id

            seznam.append(
                Vysledky.zobrazVysledek(None,vysledek)
            )

        return json({'vysledky': seznam})


    def vsechnyVysledky(): 
        vysledky = None
        student = False
        seznam = defaultdict(dict)

        if uzivatel("student"):
            vysledky = select(t for t in DbVysledekTestu if t.student.login == uzJmeno())
        elif uzivatel("ucitel"):
            vysledky = select(t for t in DbVysledekTestu)
        else:
            return "neprihasen"

        for vysledek in vysledky:
            tId = vysledek.test.id

            if not tId in seznam:
                seznam[tId] = []

            seznam[tId].append(
                Vysledky.zobrazVysledek(None,vysledek)
            )

        return json({'vysledky': seznam})

    def seznamVysledku(): 
        vysledky = select(t for t in DbVysledekTestu)
        seznam = defaultdict(dict)

        if not vysledky:
            return json({'vysledky': []})

        for vysledek in vysledky:
            if vysledek.test:
                tId = vysledek.test.id
            else: continue
            
            if not tId in seznam:
                seznam[tId] = {
                   "jmeno": vysledek.jmeno,
                   "vysledku": 0,
                }
            
            seznam[tId]["vysledku"] += 1


        return json({'vysledky': seznam})
