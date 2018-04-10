from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from .db import *
import time
import os
import functools

from .testy import Testy
from .funkce import (Zaznamy, naDesetinne, delka, datum, ted)
from .otazka import *

from collections import defaultdict

formatCasu = "%d.%m.%Y %H:%M"

class Student:
    def seznamStudentu():
        studenti = select(s for s in DbStudent)
        seznam = []

        for student in studenti:
            seznam.append(Student.zobrazStudenta(student))
            
        return json({"studenti": seznam})

    def zobrazStudenta(student):
        trida = None
        idTridy = None

        if student.trida:
            tridy = get(t for t in DbTridy if t.id is student.trida.id)         
            trida = str(tridy.poradi) + tridy.nazev
            idTridy = tridy.id

        studentInfo = {
            "id": student.id,
            "login": student.login,
            "jmeno": student.jmeno,
            "prijmeni": student.prijmeni,
            "trida": {
                "id": idTridy,
                "nazev": trida,
            },
        }
            
        return studentInfo

    def vyplnitTest(id): 
        Zaznamy.pridat("vyplneni",session['student'])
        
        # vytvori se 3 tabulky:
        # vysledekTestu, vyslednaOtazka a vyslednaOdpoved
        # az student vyplni test, do sloupce 'odpoved' se odeslou jeho odpovedi

        test = get(u for u in DbTest if u.id is id)

        vTestu = DbVysledekTestu(
            student = get(s.id for s in DbStudent if s.login == session['student']),
            test = test.id,
            jmeno = test.jmeno,
            limit = test.limit,
            casZahajeni = ted(),
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
                bodu = otazka.bodu,
                hodnotit = otazka.hodnotit
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
            'limit': seznam(test.limit)[0],
            'otazky': seznamOtazek
        }

        return json({"test": test})

    def odeslatTest(J): 
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

    def vysledekTestu(id):
        # datovy typ ktery podporuje vlozeni seznamu
        vysledek = defaultdict(dict)

        vsechnyOdpovedi = select((o.ocekavanaOdpoved, o.odpoved, o.typ, o.vyslednaOtazka.id) 
            for o in DbVyslednaOdpoved if o.vysledekTestu.id is id).order_by(3)

        typDobre = "zadaniDobre"
        typSpatne = "zadaniSpatne"
        typOtevrena = "zadaniOtevrena" 

        oznaceneDobre = "oznaceneDobre"
        oznaceneSpatne = "oznaceneSpatne"
        oznaceneOtevrena = "oznaceneOtevrena"

        # projdou se vsechny odpovedi
        for o in vsechnyOdpovedi:
            oId = o[3]
            typ = o[2]

            if typ == "D": typ = typDobre
            elif typ == "S": typ = typSpatne
            elif typ == "O": typ = typOtevrena 

            ocOdpoved = o[0]
            odpoved = o[1]
            
            if not oId in vysledek:
              vysledek[oId] = {}  

            def pridatTyp(tp):
                if not tp in vysledek[oId]:
                    vysledek[oId][tp] = []
            
            pridatTyp(typDobre)
            pridatTyp(typSpatne)
            pridatTyp(typOtevrena)
            
            pridatTyp(oznaceneDobre)
            pridatTyp(oznaceneSpatne)
            pridatTyp(oznaceneOtevrena)
            
            vysledek[oId][typ].append(ocOdpoved)
            
            #a=5/0

            # prida info o otazce
            otazka = get(o for o in DbVyslednaOtazka if o.id == oId)
            vysledek[oId].update({
                "jmeno": otazka.jmeno,
                "zadani": otazka.konkretniZadani,
                "bodu": otazka.bodu,
                "hodnotit": otazka.hodnotit,
                "hodnoceni": 0 
            })

            # priradi, ktere odpovedi jsou spravne a spatne
            if odpoved and ocOdpoved == odpoved and typ != typOtevrena:                       
                oznacene = oznaceneSpatne
                
                if typ == typDobre: 
                    oznacene = oznaceneDobre         

                vysledek[oId][oznacene].append(odpoved)

            if typ == typOtevrena:
                #cislena odpoved - desetinne cislo?:
                # zaokrouhli na 2 DM, nahradi carku za tecku a porovna
                vysledek[oId]["ciselna"] = False

                if not re.match("^\d+?[\.\,]\d+?$", ocOdpoved) is None:
                    ocCislo = naDesetinne(ocOdpoved,2)
                    stCislo = naDesetinne(odpoved,2)
                    vysledek[oId]["ciselna"] = True                   

                    if ocCislo == stCislo:
                        vysledek[oId][oznaceneDobre] = odpoved
                        vysledek[oId]["hodnoceni"] = otazka.bodu
                    else:
                        vysledek[oId][oznaceneSpatne] = odpoved
                
                # obycejna odpoved - spatne/spravne
                elif odpoved and ocOdpoved != odpoved:
                    vysledek[oId][oznaceneSpatne] = odpoved
                elif odpoved and ocOdpoved == odpoved:
                    vysledek[oId][oznaceneDobre] = odpoved
                    vysledek[oId]["hodnoceni"] = otazka.bodu

        #prideli pocet bodu k otazkam
        for i, o in vysledek.items():
            if len(o[typOtevrena]) > 0:
                continue     
            if len(o[typDobre]) == 0 and len(o[oznaceneDobre]) == 0:
                continue
            if len(o[typDobre]) == 0: 
                continue
            # pokud je v zadani 1 spravna odpoved:
            elif len(o[typDobre]) == 1:
                if len(o[oznaceneDobre]) == 0:
                    continue       
                o["hodnoceni"] = o["bodu"]
                continue

            # pokud je v zadani nekolik spravnych odpovedi:
            spravnych = len(o[typDobre])
            oznacenych = len(o[oznaceneDobre])
            hodnotit = o["hodnotit"]

            # pokud neni oznacena spravna odpoved:
            if oznacenych == 0: continue

            # pokud otazka obsahuje spatnou odpoved = 0 bodu:
            if len(o[oznaceneSpatne]) > 0: continue

            # podminky pridelovani bodu:
            # pokud jsou jen nektere oznaceny:   
            if hodnotit == 1:
                o["hodnoceni"] = o["bodu"] 
            # pokud jsou vsechny oznaceny:
            elif hodnotit == 2 and spravnych == oznacenych:
                o["hodnoceni"] = o["bodu"]
                a=5/0
            # castecne spravne - body se deli  
            elif hodnotit == 3:
                if spravnych != 0:
                    o["hodnoceni"] = o["bodu"]*oznacenych/spravnych

        # zpocita pocet bodu, prida odpovedi a prida vysledek na konec JSON
        boduMax = 0
        boduTest = 0

        for i, o in vysledek.items():
            boduMax += o["bodu"]
            boduTest += o ["hodnoceni"]
        
        # zapise udeje do DB (pokud jeste nejsou v DB)
        vTestu = DbVysledekTestu[id]
        
        if not vTestu.boduVysledek:
            vTestu.boduVysledek = boduTest
        if not vTestu.boduMax:
            vTestu.boduMax = boduMax


        jsTest = {
            "id": vTestu.id,
            "student": vTestu.student.login,
            "od": datum(vTestu.casZahajeni),
            "do": datum(vTestu.casUkonceni),
            "boduMax": boduMax,
            "boduTest": boduTest,
            "procent": 100*boduTest/boduMax,          
            "otazky": vysledek,
        }

        return json({"test": jsTest})

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
            'boduVysledek': str(test.boduVysledek),
            'boduMax': str(test.boduMax),
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

    def zmenObsah(J):
        if J["tabulka"] != "Student":
            return "Nemáš oprávnění měnit obsah této tabulky!!!"
        
        if J["id"] == "":
            DbStudent(
                login = J["bunky"][0],
                jmeno =  J["bunky"][1],
                prijmeni = J["bunky"][2],
                trida = int(J["bunky"][3])
            )

            return "Byl vložen nový student."

        id = int(J["id"])

        dbId = get(o.id for o in DbStudent if o.id is id)

        if not dbId:
            return "Toto id neexistuje!"

        student = DbStudent[id]

        if J["akce"] == "smazat":
            student.delete()
            return "Student byl smazán"

        elif J["akce"] == "zmenit":
            student.login = J["bunky"][0]
            student.jmeno = J["bunky"][1]
            student.prijmeni = J["bunky"][2]
            if J["bunky"][3] != "null":
                student.trida = int(J["bunky"][3])

            return "Student byl změněn."