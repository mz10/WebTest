from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from .db import *
import json as _json
import random

from .funkce import (nahodne, json, jsonStahnout, vypocitej)
from .otazka import Otazka, Odpovedi

formatCasu = "%d.%m.%Y %H:%M"

class Testy:
    def zobraz():
        seznam = []
        testy = select(o for o in DbTest)

        for t in testy:
            seznamOtazek = []

            for o in select(o for o in DbOtazkaTestu if o.test.id is t.id):
                seznamOtazek.append(o.otazka.id)

            seznam.append({
                'id':       t.id,
                'jmeno':    t.jmeno,
                'od':       t.zobrazenoOd.strftime(formatCasu),
                'do':       t.zobrazenoDo.strftime(formatCasu),
                'autor':    t.ucitel.login,
                'limit':    t.limit,
                'pokusu':   t.pokusu,
                'skryty':   t.skryty,
                'nahodny':  t.nahodny,
                'omezit':   t.maxOtazek,
                'otazky':   seznamOtazek,
                'tridy':    Testy.seznamTrid(t.id)
            })

        return json({"testy": seznam})

    def zobrazTest(id):
        test = DbTest[id]
        seznamOtazek = []

        #ziskat seznam otazek v testu
        for o in select(o for o in DbOtazkaTestu if o.test.id is test.id):
            otazka = DbOtazka[o.otazka.id]
            zadani = Otazka.vytvorZadani(otazka.obecneZadani)
 
            odpovedi = Odpovedi(otazka.id, zadani["promenne"])
            dobre = odpovedi.vypocitat("D")
            spatne = odpovedi.vypocitat("S")
            otevrena = ["_OTEVRENA_" for i in odpovedi.tridit("O")]
            
            seznamOdpovedi = dobre + spatne + otevrena        
            random.shuffle(seznamOdpovedi)

            seznamOtazek.append({
                'id':           otazka.id,
                'jmeno':        otazka.jmeno,
                'zadani':       zadani["html"],
                'spravnych':    len(odpovedi.tridit("D")),
                'odpovedi':     seznamOdpovedi
            })

            random.shuffle(seznamOtazek)

        jsTest = {
            'id':       test.id,
            'jmeno':    test.jmeno,
            'od':       test.zobrazenoOd.strftime(formatCasu),
            'do':       test.zobrazenoDo.strftime(formatCasu),
            'limit':    test.limit,
            'pokusu':   test.pokusu,
            'skryty':   test.skryty,
            'nahodny':  test.nahodny,
            'omezit':   test.maxOtazek,
            'autor':    test.ucitel.login,
            'otazky':   seznamOtazek,
            'tridy':    Testy.seznamTrid(test.id)
        }

        return json({"test": jsTest})        

    def pridat(J):
        nahodneJmeno = "_" + str(nahodne(1000,10000))

        # vytvorit prazdny test, id je nezname!
        # pro prirazeni odpovedi je potreba znat id
        DbTest(
            ucitel = get(u for u in DbUcitel if u.login == session['ucitel']),
            jmeno = nahodneJmeno
        )           
        
        # zjistit id tohoto testu
        idTestu = get(u.id for u in DbTest if u.jmeno == nahodneJmeno)
        
        # vyplnit
        if idTestu:
            Testy.uprav(J,idTestu)
            return 'Vytvořen test: ' + J['jmeno']
        else:
            return 'Test nebyl vytvořen!'

    def uprav(J,tid=0):
        idTestu = tid or J['id']
        test = DbTest[idTestu]

        test.jmeno = J['jmeno']
        test.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
        test.zobrazenoOd = dt.strptime(J['od'], formatCasu)
        test.zobrazenoDo = dt.strptime(J['do'], formatCasu)
        test.limit = J["limit"]
        test.pokusu = int(J["pokusu"])
        test.skryty = J["skryty"] 
        test.nahodny = J["nahodny"]
        test.maxOtazek = int(J["omezit"])

        #smaz puvodni otazky a tridy z testu
        select(o for o in DbOtazkaTestu if o.test.id is idTestu).delete()
        select(o for o in DbTridyTestu if o.test.id is idTestu).delete()

        for idOtazky in J['otazky']:
            DbOtazkaTestu(
                poradi = 0, 
                test = get(u.id for u in DbTest if u.jmeno == J['jmeno']),
                otazka = get(o for o in DbOtazka if o.id == idOtazky)
            )

        for idTridy in J['tridy']:
            DbTridyTestu(
                test = idTestu,
                trida = get(t for t in DbTridy if t.id == idTridy)
            )   

        return 'Upraven test: ' + J['jmeno']

    def seznamTrid(idTestu):
        seznam = []

        for tt in select(tt for tt in DbTridyTestu if tt.test.id is idTestu):
            if not tt.trida: continue

            trida = get(t for t in DbTridy if t.id == tt.trida.id)
            jmenoTridy = str(trida.poradi) + trida.nazev
            seznam.append({
                "id": trida.id, 
                "jmeno": jmenoTridy,
            })

        return seznam