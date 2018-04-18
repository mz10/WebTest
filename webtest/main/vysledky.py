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
from .funkce import (pswd_check, json, wsJSON, ted, Zaznamy, datum, uzivatel, uzJmeno)

class Vysledky:
    def zobrazVysledek(id,vysledek):
        if not vysledek:
            vysledek = get(v for v in DbVysledekTestu if v.id is id)

        procent = 0
        if vysledek.boduMax != 0:
            procent = 100*vysledek.boduVysledek/vysledek.boduMax

        trida = "-"
        if vysledek.student.trida:
            trida = str(vysledek.student.trida.poradi) + vysledek.student.trida.nazev

        info = {
            'id': vysledek.id,
            'jmeno': vysledek.jmeno,
            'casZahajeni': datum(vysledek.casZahajeni),
            'casUkonceni': datum(vysledek.casUkonceni),
            'limit': vysledek.limit,
            'pokus': vysledek.pokus,
            'boduVysledek': vysledek.boduVysledek,
            'boduMax': vysledek.boduMax,
            'procent': procent,
            'hodnoceni': vysledek.hodnoceni,
            'student': {
                'id': vysledek.student.id,
                'login': vysledek.student.login,
                'prijmeni': vysledek.student.prijmeni,
                'trida': trida
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

        for vysledek in vysledky:
            tId = vysledek.test.id
            
            if not tId in seznam:
                seznam[tId] = {
                   "jmeno": vysledek.jmeno,
                   "vysledku": 0,
                }
            
            seznam[tId]["vysledku"] += 1


        return json({'vysledky': seznam})
