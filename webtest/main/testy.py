from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from .db import *
import json as _json
import random

from .funkce import (nahodne, json, jsonStahnout, vypocitej, uzivatel, uzJmeno)
from .otazka import Otazka, Odpovedi

formatCasu = "%d.%m.%Y %H:%M"

class Testy:
    def zobraz():
        seznam = []
        testy = None

        if uzivatel("admin"):
            testy = select(o for o in DbTest)
        elif uzivatel("ucitel"):
            testy = select(o for o in DbTest if o.ucitel.login == uzJmeno())
        else:
            return "!!!"

        for test in testy:
            seznamOtazek = []

            for o in select(o for o in DbOtazkaTestu if o.test.id is test.id):
                seznamOtazek.append(o.otazka.id)

            seznam.append(
                Testy.testInfo(test,seznamOtazek)
            )

        return json({"testy": seznam})

    def zobrazStudent():
        seznam = []
        testy = None

        # info o studentovi
        student = get(s for s in DbStudent if s.login == uzJmeno())
        testy = select(o for o in DbTest)

        for test in testy:
            if test.skryty: continue

            # overi jestli je test prirazen k studentove tride
            tridy = select(t.trida for t in DbTridyTestu if t.test.id is test.id)
            pokracovat = 0
            for trida in tridy:
                if student.trida and trida and trida.id != student.trida.id:
                    pokracovat +=1
            
            if pokracovat > 0:
                continue

            seznamOtazek = []

            for o in select(o for o in DbOtazkaTestu if o.test.id is test.id):
                seznamOtazek.append(o.otazka.id)

            seznam.append(
                Testy.testInfo(test,seznamOtazek)
            )

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

        jsTest = Testy.testInfo(test,seznamOtazek)
        return json({"test": jsTest})        

    def testInfo(test,otazky):
        return {
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
            'otazky':   otazky,
            'tridy':    Testy.seznamTrid(test.id)
        }

    def pridat(J,hromadne=False):
        nahodneJmeno = "_" + str(nahodne(1000,10000))

        # vytvorit prazdny test, id je nezname!
        # pro prirazeni odpovedi je potreba znat id
        DbTest(
            ucitel = get(u for u in DbUcitel if u.login == uzJmeno()),
            jmeno = nahodneJmeno
        )           
        
        # zjistit id tohoto testu
        idTestu = get(u.id for u in DbTest if u.jmeno == nahodneJmeno)
        
        # vyplnit
        if idTestu:
            Testy.uprav(J,idTestu,hromadne)
            return 'Vytvořen test: ' + J['jmeno']
        else:
            return 'Test nebyl vytvořen!'

    def uprav(J,tid=0,hromadne=False):
        idTestu = tid or J['id']
        test = DbTest[idTestu]

        test.jmeno = J['jmeno']
        test.ucitel = get(u for u in DbUcitel if u.login == uzJmeno())
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

        # pokud se testy nahraji hromadne,
        # nejdriv se musi zjistit id otazek
        if hromadne:
            for otazka in J['otazky']:
                DbOtazkaTestu(
                    poradi = 0, 
                    test = test.id,
                    otazka = get(o.id for o in DbOtazka if o.jmeno == otazka["jmeno"])
                )

   
        else:
            for idOtazky in J['otazky']:
                DbOtazkaTestu(
                    poradi = 0, 
                    test = test.id,
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

    def export():
        """
        if uzivatel("admin"):
            testy = select(o for o in DbTest)
        elif uzivatel("ucitel"):
            testy = select(o for o in DbTest if o.ucitel.login == uzJmeno())
        else:
            return "!!!"

        """

        testy = select(o for o in DbTest)

        seznamTestu = []

        for test in testy:
            seznamOtazek = []

            #ziskat seznam otazek v testu
            for o in select(o for o in DbOtazkaTestu if o.test.id is test.id):
                otazka = DbOtazka[o.otazka.id]
                odpovedi = Odpovedi(otazka.id)

                seznamOtazek.append({
                    'id':       otazka.id,
                    'jmeno':    otazka.jmeno,
                    'bodu':     otazka.bodu,
                    'hodnotit': otazka.hodnotit,
                    'zadani':   otazka.obecneZadani,
                    'spravne':  odpovedi.tridit("D"),  
                    'spatne':   odpovedi.tridit("S"), 
                    'otevrena': odpovedi.tridit("O"),  
                })

            seznamTestu.append(
                Testy.testInfo(test,seznamOtazek)
            )

        seznam = {
            'akce': 'nahrat', 
            'co': 'test',
            'testy': seznamTestu,
        }

        return jsonStahnout(seznam,"testy.txt")
        #return json(seznam)


    def pridatVsechny(J):
        for test in J["testy"]:
            # přidá otázky
            for otazka in test["otazky"]:
                Otazka.pridat(otazka)            
            
            # přidá test a přiřadí k nim otázky
            Testy.pridat(test,True)
        return "Testy byly přidány."