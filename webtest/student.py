from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from webtest.db import *
import time
import os
import functools

from .testy import Testy
from .funkce import Zaznamy
from .otazka import *

from collections import defaultdict

formatCasu = "%d.%m.%Y %H:%M"

class Student:
    def vyplnitTest(id): 
        Zaznamy.pridat("vyplneni",session['student'])
        zacatek = dt.now().strftime("%d.%m.%Y %H:%M:%S")

        limit = select(t.limit for t in DbTest if t.id == id)


        # vytvori se 3 tabulky:
        # vysledekTestu, vyslednaOtazka a vyslednaOdpoved
        # v tabulce vyslednaOdpoved budou jen spravne a otevrene odpovedi
        # az student vyplni test, do teto tabulky se odeslou jeho odpovedi (typ vyplneno - "V")
        # podle id se porovna kolik odeslanych odpovedi je spravne

        vTestu = DbVysledekTestu(
            student = get(s.id for s in DbStudent if s.login == session['student']),
            test = get(u.id for u in DbTest if u.id is id),
            casZahajeni = zacatek,
        )

        cislaOtazek = select(o.otazka for o in DbOtazkaTestu if o.test.id is id)

        seznamOtazek = [] 
        
        for cislo in cislaOtazek: 
            seznamOdpovedi = []
            idOtazky = cislo.id   
            otazka = DbOtazka[idOtazky]
            zadani = Otazka.vytvorZadani(otazka.obecneZadani)
            odpovedi = Odpovedi(idOtazky, zadani["promenne"])

            vOtazka = DbVyslednaOtazka(
                jmeno = otazka.jmeno,
                puvodniZadani = otazka.obecneZadani,
                konkretniZadani = zadani["html"],
                vysledekTestu = vTestu.id,
                puvodniOtazka = idOtazky,
                bodu = otazka.bodu
            )

            for (odpoved, typ) in odpovedi.vypocitatVsechny():
                if typ == "O":
                    seznamOdpovedi.append("_OTEVRENA_")
                else:
                    seznamOdpovedi.append(odpoved)

                #if typ == "S": continue;
                
                DbVyslednaOdpoved(
                    ocekavanaOdpoved = odpoved,
                    typ = typ,
                    vysledekTestu = vTestu.id,
                    vyslednaOtazka = vOtazka.id
                )
        
            random.shuffle(seznamOdpovedi)            
             
            seznamOtazek.append({
                'id': vOtazka.id,
                'jmeno': otazka.jmeno,
                'zadani': zadani["html"],
                'spravnych': len(odpovedi.tridit("D")),
                'odpovedi': seznamOdpovedi
            })

        random.shuffle(seznamOtazek)

        test = {
            'id': vTestu.id,
            'do': "limit",
            'limit': seznam(limit)[0],
            'otazky': seznamOtazek
        }

        return json({"test": test})

    def vyhodnotitTest(J): 
        Zaznamy.pridat("vyplneno",session['student'])      
        
        idTestu = int(J["idTestu"])
        vTestu = DbVysledekTestu[idTestu]
        vTestu.casUkonceni = dt.now().strftime(formatCasu)

        for odpoved in J["odpovedi"]:
            text = odpoved[1]
            idOtazky = int(odpoved[0])
            idVOdpovedi = get(o.id for o in DbVyslednaOdpoved 
                if o.vyslednaOtazka.id is idOtazky and text == o.ocekavanaOdpoved)

            # priradi odpoved od studenta k ocekavane odpovedi
            # nebo pokud bude otevrena, vyhleda typ
            if idVOdpovedi:
                vOdpoved = DbVyslednaOdpoved[idVOdpovedi]                
                vOdpoved.odpoved = text
            else:
                idOtOdpovedi = get(o.id for o in DbVyslednaOdpoved 
                    if o.vyslednaOtazka.id is idOtazky and o.typ == "O")
                
                vOdpoved = DbVyslednaOdpoved[idOtOdpovedi]                
                vOdpoved.odpoved = text   
        
        return "Test byl odeslán" 
                                 

    def hodnotit1(id):
        vysledek = ""

        zadaneOdpovedi = select((o.odpoved, o.typ, o.vyslednaOtazka.id) 
            for o in DbVyslednaOdpoved if o.vysledekTestu.id is id and o.typ != "V").order_by(3)

        vyplneneOdpovedi = select((o.odpoved, o.typ, o.vyslednaOtazka.id) 
            for o in DbVyslednaOdpoved if o.vysledekTestu.id is id and o.typ == "V").order_by(3)

        for o in zadaneOdpovedi:
            vysledek += str(o) + "\n"

        vysledek += "\n\n"

        for o in vyplneneOdpovedi:
            vysledek += str(o) + "\n"

        vysledky = []

        # vyhleda cisla spravnych odpovedi
        for zo in zadaneOdpovedi:
            odpoved = zo[0]
            idOdpovedi = zo[2]

            for vo in vyplneneOdpovedi:
                if odpoved == vo[0]:
                   vysledky.append(idOdpovedi)
                   break
                
                if idOdpovedi < vo[2]: 
                    #vysledky.append(["spatne", idOdpovedi]) 
                    break
                    
        pocetOtazek = select(u for u in DbVyslednaOtazka).count()
        pocetSpravnych = len(vysledky)

        procent = pocetSpravnych/pocetOtazek*100

        vTestu = DbVysledekTestu[id]
        vTestu.procent = procent

        return vysledek + "\n\n\n"  + "\n\n\n" + str(pocetOtazek) + "\n\n\n" + str(procent)


    def hodnotit(id):
        # datovy typ ktery podporuje vlozeni seznamu
        vysledek = defaultdict(dict)

        vsechnyOdpovedi = select((o.ocekavanaOdpoved, o.odpoved, o.typ, o.vyslednaOtazka.id) 
            for o in DbVyslednaOdpoved if o.vysledekTestu.id is id).order_by(3)

        # projdou se vsechny odpovedi
        for o in vsechnyOdpovedi:
            oId = o[3]
            typ = o[2]

            if typ == "D": typ = "dobre"
            elif typ == "S": typ = "spatne"
            elif typ == "O": typ = "otevrena"
                 

            ocOdpoved = o[0]
            odpoved = o[1]
            
            if not oId in vysledek:
              vysledek[oId] = {}  

            if not typ in vysledek[oId]:
                vysledek[oId][typ] = []
            
            vysledek[oId][typ].append(ocOdpoved)
            
            # zobrazi info o otazce
            otazka = get(o for o in DbVyslednaOtazka if o.id == oId)
            vysledek[oId]["jmeno"] = otazka.jmeno
            vysledek[oId]["zadani"] = otazka.konkretniZadani
            vysledek[oId]["bodu"] = otazka.bodu          


            # priradi, ktere odpovedi jsou spravne a spatne
            if odpoved and ocOdpoved == odpoved and typ != "otevrena":
                if not "hodnoceni" in vysledek[oId]:
                    vysledek[oId]["hodnoceni"] = 0               
                                
                oznacene = "oznaceneSpatne"
                
                # pokud je otazka dobre, hodnoceni je 1
                # pokud je vic spatnych nez dobrych, hodnoceni je zaporne
                if typ == "dobre": 
                    oznacene = "oznaceneDobre"
                    vysledek[oId]["hodnoceni"] += 1                 
                else:
                    vysledek[oId]["hodnoceni"] -= 1 

                if not oznacene in vysledek[oId]:
                    vysledek[oId][oznacene] = []

                vysledek[oId][oznacene].append(odpoved)

            # otevrena odpoved - spatne/spravne
            if odpoved and ocOdpoved != odpoved and typ == "otevrena":
                vysledek[oId]["oznaceneSpatne"] = odpoved
                vysledek[oId]["hodnoceni"] = 0  
            elif odpoved and ocOdpoved == odpoved and typ == "otevrena":
                vysledek[oId]["oznaceneDobre"] = odpoved
                vysledek[oId]["hodnoceni"] = 1 

        return json({"test": vysledek})

    def zobrazVysledekTestu(id):
        test = DbVysledekTestu[id]
        otazky = select(o for o in DbVyslednaOtazka if o.vysledekTestu.id is test.id)
        seznamOtazek = []

        for otazka in otazky:
            odpovedi = select(o.odpoved for o in DbVyslednaOdpoved if o.vysledekTestu.id is test.id)

            seznamOtazek.append({
                'id': otazka.id,
                'jmeno': otazka.jmeno,
                'zadani': otazka.konkretniZadani,
                'bodu': otazka.bodu,
                'odpovedi': seznam(odpovedi)
            })

        jsTest = {
            'id': test.id,
            'od': test.casZahajeni.strftime(formatCasu),
            'do': test.casUkonceni.strftime(formatCasu),
            'procent': str(test.procent),
            'bodu': str(test.bodu),
            'student': test.student.login,
            'otazky': seznamOtazek,
        }

        return json({"test": jsTest})  



    def testy():
        if request.method == 'GET':
            pritomnost = dt.strptime(
                time.strftime("%d.%m.%Y %H:%M"), "%d.%m.%Y %H:%M")
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