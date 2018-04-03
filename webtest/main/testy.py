from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
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
                'id': t.id,
                'jmeno': t.jmeno,
                'od': t.zobrazenoOd.strftime(formatCasu),
                'do': t.zobrazenoDo.strftime(formatCasu),
                'autor': t.ucitel.login,
                'limit': t.limit,
                'pokusu': t.pokusu,
                'skryty': t.skryty,
                'otazky': seznamOtazek
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
                'id': otazka.id,
                'jmeno': otazka.jmeno,
                'zadani': zadani["html"],
                'spravnych': len(odpovedi.tridit("D")),
                'odpovedi': seznamOdpovedi
            })

            random.shuffle(seznamOtazek)

        jsTest = {
            'id': test.id,
            'jmeno': test.jmeno,
            'od': test.zobrazenoOd.strftime(formatCasu),
            'do': test.zobrazenoDo.strftime(formatCasu),
            'limit': test.limit,
            'pokusu': test.pokusu,
            'skryty': test.skryty,
            'autor': test.ucitel.login,
            'otazky': seznamOtazek
        }

        return json({"test": jsTest})        

    def uprav(J):
        test = DbTest
        idTestu = J['id']
        test = DbTest[idTestu]

        test.jmeno = J['jmeno']
        test.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
        test.zobrazenoOd = dt.strptime(J['od'], formatCasu)
        test.zobrazenoDo = dt.strptime(J['do'], formatCasu)
        test.limit = J["limit"]
        test.pokusu = int(J["pokusu"])
        test.skryty = J["skryty"] 

        #smaz puvodni otazky z testu
        select(o for o in DbOtazkaTestu if o.test.id is idTestu).delete()
        
        for idOtazky in J['otazky']:
            DbOtazkaTestu(
                poradi = 0, 
                test = get(u for u in DbTest if u.jmeno == J['jmeno']),
                otazka = get(o for o in DbOtazka if o.id == idOtazky)
            )

        return 'Upraven test: ' + J['jmeno']


    def pridat(J):
        DbTest(
            jmeno = J['jmeno'],
            ucitel = get(u for u in DbUcitel if u.login == session['ucitel']),
            zobrazenoOd = dt.strptime(J['od'], formatCasu),
            zobrazenoDo = dt.strptime(J['do'], formatCasu),
            limit = J["limit"],
            pokusu = int(J["pokusu"]),
            skryty = J["skryty"]
        )

        for idOtazky in J['otazky']:
            DbOtazkaTestu(
                poradi = 0, 
                test = get(u for u in DbTest if u.jmeno == J['jmeno']),
                otazka = get(o for o in DbOtazka if o.id == idOtazky)
            )

        return 'Vytvořen test: ' + J['jmeno']
            


    ###################################################################

    def testy():
        if request.method == 'GET':
            pritomnost = dt.strptime(
                time.strftime(formatCasu), formatCasu)
            testy = select((u.id, u.jmeno, u.zobrazenoOd, u.zobrazenoDo)
                        for u in DbTest if (pritomnost >= u.zobrazenoOd and
                                            pritomnost <= u.zobrazenoDo))
            return render_template('student.html', testy=testy)

    def vysledky():
        if request.method == 'GET':
            testy_uzivatele = select((u.test.jmeno, u.casUkonceni, u.id) for u in DbVysledekTestu
                                    if u.student.login is session['student'])
            for test in testy_uzivatele:
                print (test)
        return render_template('student_vysledky.html', testyUzivatele=testy_uzivatele)   