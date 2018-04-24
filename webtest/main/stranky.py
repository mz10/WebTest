from flask import *
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime
from sympy import *
from jinja2 import TemplateNotFound

from .. import socketio as ws
from . import main

from .funkce import *
from .ostatni import *
from .student import *
from .testy import *
from .otazka import *
from .tridy import *
from .uzivatel import Uzivatel
from .slovnik import Slovnik
from .vysledky import Vysledky
from .ucitel import Ucitel

import time
import os
import functools         
import random
import sys
import json as _json
import traceback

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

# socket IO
nm = "/ws"

@main.route('/')
@db_session
def index(): return Uzivatel.index()

@main.errorhandler(404)
def nenalezeno(ch): return render_template('404.html', e=ch), 404

@main.route('/tabulky/')
@prihlasit('admin')
def databaze(): return Ostatni.databaze()

@main.route('/tabulky/', methods=('get','post'), endpoint='new')
@prihlasit('admin')
def SmazTabulku(): return Ostatni.smazTabulku()

@main.route('/tabulky/uklid/')
@prihlasit('admin')
def uklidDb(): return Ostatni.uklidDb()

@main.route('/db/')
@prihlasit('admin')
def db(): return render_template('db.html') 

@main.route('/vytvor/')
def NovaTabulka1(): return Ostatni.novaTabulka()
    
@main.route('/prihlasit/', methods=["GET", "POST"])
@db_session
def login2(): return Uzivatel.prihlasit()
    
@main.route('/odhlasit/', methods=['GET', 'POST'])
def logout(): return Uzivatel.odhlasit()

@main.route('/otazky/ucitel/<login>', methods=['GET'])
@prihlasit('ucitel','admin')
@db_session
def otazky_ucitel(login): return Otazka.ucitel(login)

@main.route('/otazky/editovat/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def otazka_editovat(id): return Otazka.upravit(id)

@main.route('/otazky/smazat/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def otazka_smazat(id): return Otazka.smazat(id)

@main.route('/pridat/otazku/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
def pridat_otazku(): return Otazka.pridat()

@main.route('/pridat/test/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def pridat_test(): return Testy.pridat()

@main.route('/testy/<id_test>', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def uprav_test(id_test): return Testy.uprav(id_test)

@main.route('/student/testy/', methods=['GET', 'POST'])
@prihlasit('student')
@db_session
def student_testy(): return Student.testy()

@main.route('/student/testy/<id>', methods=['GET', 'POST'])
@prihlasit('student')
@db_session
def student_zobrazit(id): return Student.zobrazit(id)

@main.route('/student/vysledky/')
@prihlasit('student')
@db_session
def student_vysledek(): return Student.vysledky()

@main.route('/csv/slovnik/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def sl(): return Slovnik.stahnout()

@main.route('/csv/studenti/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def sts(): return Student.stahnout()

@main.route('/vzory/testy/')
def testy1(): return render_template('test.html') 

@main.route('/vzory/otazky/')
def otazky1(): return render_template('otazka.html') 

@main.route('/vzory/upload/')
def upload1(): return render_template('upload.html') 



################JSON#################
@main.route('/json/slovnik/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def sl2(): return Slovnik.zobraz()

@main.route('/json/testy/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def testy(): return Testy.zobraz()

@main.route('/json/student/testy/', methods=['GET', 'POST'])
@db_session
def testyS(): return Testy.zobrazStudent()

@main.route('/json/student/testy/<id>', methods=['GET', 'POST'])
@db_session
def testy3(id): return Student.vyplnitTest(id)

@main.route('/json/testy/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def testy2(id): return Testy.zobrazTest(id)

@main.route('/json/otazky/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def otazky(): return Otazka.zobrazOtazky()

@main.route('/json/otazky/export/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def otazkyE(): return Otazka.export()

@main.route('/json/testy/export/', methods=['GET', 'POST'])
#@prihlasit('ucitel','admin')
@db_session
def testyE(): return Testy.export()

@main.route('/json/registrace/', methods=['GET', 'POST'])
@db_session
def reg(): return Ostatni.registrace(request.json)

@main.route('/json/tridy/<id>', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def trId(id): return Trida.zobrazCelouTridu(id)

@main.route('/json/tridy/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def tr(): return Trida.zobrazTridy()

@main.route('/json/studenti/', methods=['GET', 'POST'])
@prihlasit('ucitel','admin')
@db_session
def st(): return Student.seznamStudentu()

@main.route('/json/ucitele/', methods=['GET', 'POST'])
#@prihlasit('ucitel','admin')
@db_session
def uc(): return Ucitel.seznamUcitelu()

@main.route('/json/otazky/<id>', methods=['GET'])
@prihlasit('ucitel','admin')
@db_session
def otazka_zobrazit(id): return Otazka.zobraz(id)

@main.route('/json/vysledky/', methods=['GET'])
@db_session
def vz(): return Vysledky.vsechnyVysledky()

@main.route('/json/vysledky/seznam/', methods=['GET'])
@db_session
def vs(): return Vysledky.seznamVysledku()

@main.route('/json/vysledky/<id>/', methods=['GET'])
@db_session
def vt(id): return Vysledky.test(id)

@main.route('/json/post/student/', methods=['POST'])
@prihlasit('student')
@db_session
def postS():
    J = request.json
    akce = J["akce"]
    co = J["co"]
    odpoved = "zadna akce"

    if(co == "test"):
        if akce == "vyhodnotit":
            Student.odeslatTest(J)
            return Student.vysledekTestu(J["idTestu"])

    js = {
        "odpoved":odpoved,
        "stav":"ok",
    }           

    return json(js)


@main.route('/student/vyhodnotit/<id>', methods=['GET'])
@db_session
def ttt(id):
    return Student.vysledekTestu(id)

@main.route('/json/post/', methods=['POST'])
@prihlasit('ucitel','admin')
@db_session
def postU(): 
    odpoved = "zadna akce" 
    
    #try:
    J = request.json
    akce = J["akce"]
    co = J["co"]

    if(co == "otazka"):
        if akce == "smazat":
            odpoved = Otazka.smazat(J)
        if akce == "smazatVsechny":
            odpoved = Otazka.smazatVsechny()
        elif akce == "pridat":
            odpoved = Otazka.pridat(J)
        elif akce == "upravit":
            odpoved = Otazka.upravit(J)
        elif akce == "nahrat":
            odpoved = Otazka.pridatVsechny(J)                       
    if(co == "test"):
        if akce == "smazat":
            idTestu = J["id"]
            DbTest[idTestu].delete()
            odpoved = "Test s id " + idTestu + " byl smazán"
        elif akce == "pridat":
            odpoved = Testy.pridat(J)
        elif akce == "upravit":
            odpoved = Testy.uprav(J)
        elif akce == "nahrat":
            odpoved = Testy.pridatVsechny(J)
    elif(co == "tabulka"):
        if akce == "smazat":
            Ostatni.smazTabulku(J["nazev"],"smazat")
            odpoved = "Tabulka " + J["nazev"] + " byla smazána."
        elif akce == "vysypat":
            Ostatni.smazTabulku(J["nazev"],"vysypat")
            odpoved = "Tabulka " + J["nazev"] + " byla vysypána."
    elif(co == "slovnik"):
        if akce == "pridat":
            Slovnik.pridat(J)
            odpoved = "Slovo bylo přidáno."
    elif(co == "trida"):
        if akce == "pridat":
            odpoved = Trida.pridat(J)
    elif(co == "csv"):
        if akce == "nahrat" and J["studenti"] == False:
            odpoved = Slovnik.nahrat(J)
        elif akce == "nahrat" and J["studenti"] == True:
            odpoved = Student.nahrat(J)
    elif(co == "radek"):
        tabulka = J["tabulka"]
        if tabulka == "Student":
            odpoved = Student.zmenObsah(J)
        elif tabulka == "Tridy":
            odpoved = Trida.zmenObsah(J)
        elif tabulka == "Slovnik":
            odpoved = Slovnik.zmenObsah(J)
        elif tabulka == "Ucitel":
            odpoved = Ucitel.zmenObsah(J)


    #except Exception as e:
    #    odpoved = "Chyba v JSON!: " + str(e)

    return json({"odpoved":odpoved})

#@prihlasitWS('ucitel')
@db_session
def zpracovatJSON(J): 
    J = _json.loads(J)
    akce = J["akce"]
    co = J["co"]
    odpoved = "zadna akce"

    if(co == "otazka"):
        if akce == "smazat":
            idOtazky = J["id"]
            DbOtazka[idOtazky].delete()
            odpoved = "Otázka s id " + idOtazky + " byla smazána"
        elif akce == "pridat":
            odpoved = Otazka.pridat(J)
        elif akce == "upravit":
            odpoved = Otazka.upravit(J)
        elif akce == "nahrat":
            odpoved = Otazka.pridatVsechny(J)                     
    if(co == "test"):
        if akce == "smazat":
            idTestu = J["id"]
            DbTest[idTestu].delete()
            odpoved = "Test s id " + idTestu + " byl smazán"
        elif akce == "pridat":
            odpoved = Testy.pridat(J)
        elif akce == "upravit":
            odpoved = Testy.uprav(J)
    elif(co == "tabulka"):
        if akce == "smazat":
            Ostatni.smazTabulku(J["nazev"],"smazat")
            odpoved = "Tabulka " + J["nazev"] + " byla smazána."
        elif akce == "vysypat":
            Ostatni.smazTabulku(J["nazev"],"vysypat")
            odpoved = "Tabulka " + J["nazev"] + " byla vysypána."
    elif(co == "slovnik"):
        if akce == "pridat":
            Slovnik.pridat(J)
            odpoved = "Slovo bylo přidáno."
    elif(co == "trida"):
        if akce == "pridat":
            odpoved = Trida.pridat(J)
    elif(co == "osoba"):
        if akce == "pridat":
            odpoved = Ostatni.registrace(J)
    elif(co == "csvSlovnik"):
        if akce == "nahrat":
            odpoved = Slovnik.nahrat(J)
    elif(co == "csvSlovnik"):
        if akce == "nahrat":
            odpoved = Slovnik.nahrat(J)



    js = {
        "odpoved":odpoved,
        "stav":"ok",
    }           

    return wsJSON(js)


##########################################

@ws.on('odeslatJSON', namespace=nm)
def odjson(J):
    try:
        return zpracovatJSON(J)
    except Exception as e:
        return wsJSON({"traceback": traceback.format_exc().split("\n")})


@ws.on('prihlasit', namespace=nm)
@db_session
def wsp(z): 
    Uzivatel.zaznamenat(z)

@ws.on('odhlasit', namespace=nm)
@db_session
def wsp(z): 
    Uzivatel.smazatSpojeni(z)

@ws.on('info', namespace=nm)
def info(z): 
    Uzivatel.poslatZaznam(z)

@ws.on('odpojUzivatele', namespace=nm)
def odU(sid): 
    Uzivatel.odpojUzivatele(sid)