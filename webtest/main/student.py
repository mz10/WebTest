from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from .db import *
import time
import os
import functools
import cgi
import re

from .testy import Testy
from .funkce import (Zaznamy, naDesetinne, delka, 
    datum, ted, uzivatel, uzJmeno, tolerance, dtRozdil)
from .otazka import *

from collections import defaultdict

formatCasu = "%d.%m.%Y %H:%M:%S"

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
            "id":       student.id,
            "login":    student.login,
            "jmeno":    student.jmeno,
            "prijmeni": student.prijmeni,
            "trida": {
                "id":     idTridy,
                "nazev":  trida,
            },
        }
            
        return studentInfo

    def vyplnitTest(id): 
        # vytvori se 3 tabulky:
        # vysledekTestu, vyslednaOtazka a vyslednaOdpoved
        # az student vyplni test, do sloupce 'odpoved' se odeslou jeho odpovedi

        test = get(u for u in DbTest if u.id is id)

        if dt.now() < test.zobrazenoOd:
            return json({"info": dtRozdil(dt.now(),test.zobrazenoOd)})

        if dt.now() > test.zobrazenoDo:          
            return json({"info": "Tento test už není možné vyplnit."})

        # ziska pocet pokusu u 1 testu
        pokusu = select(v for v in DbVysledekTestu 
            if v.test.id is id and v.student.login == uzJmeno()).count()

        if test.pokusu <= pokusu:
            return json({"info": "Smůla, už nemáš další pokus!"})

        if uzivatel("student"):
            Zaznamy.pridat("vyplneni",uzJmeno())

        vTestu = DbVysledekTestu(
            student = get(s.id for s in DbStudent if s.login == uzJmeno()),
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
            zadani = Zadani.vytvorZadani(otazka.obecneZadani)
            odpovedi = Odpovedi(idOtazky, zadani["promenne"])

            # odstrani komentar z otazky
            pZadani = re.compile(r"\/\*\*(.*?)\*\*\/?",re.DOTALL).sub("",otazka.obecneZadani)

            vOtazka = DbVyslednaOtazka(
                jmeno = otazka.jmeno,
                puvodniZadani = pZadani,
                konkretniZadani = zadani["html"],
                vysledekTestu = vTestu.id,
                puvodniOtazka = idOtazky,
                zaokrouhlit = otazka.zaokrouhlit,
                tolerance = otazka.tolerance,
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
                'id':           vOtazka.id,
                'jmeno':        otazka.jmeno,
                'zadani':       zadani["html"],
                'zaokrouhlit':  otazka.zaokrouhlit,
                'tolerance':    otazka.tolerance,
                'spravnych':    len(odpovedi.tridit("D")),
                'odpovedi':     seznamOdpovedi
            })

        if test.nahodny:
            random.shuffle(seznamOtazek)

        # oreze seznam otazek na maximalni pocet
        if test.maxOtazek > 0:
            seznamOtazek = seznamOtazek[:test.maxOtazek]

        test = {
            'id':       vTestu.id,
            'do':       "limit",
            'limit':    seznam(test.limit)[0],
            'otazky':   seznamOtazek
        }

        return json({"test": test})

    def odeslatTest(J): 
        idTestu = int(J["idTestu"])
        vId = get(v.id for v in DbVysledekTestu if v.id is idTestu)

        if not vId:
            return "Tento výsledek testu neexistuje!"

        Zaznamy.pridat("vyplneno",uzJmeno())      
        
        vTestu = DbVysledekTestu[idTestu]
        vTestu.casUkonceni = ted()

        for odpoved in J["odpovedi"]:
            text = odpoved[1]
            idOtazky = int(odpoved[0])
            idVOdpovedi = get(o.id for o in DbVyslednaOdpoved 
                if o.vyslednaOtazka.id is idOtazky and text == o.ocekavanaOdpoved)

            # priradi odpoved od studenta k ocekavane odpovedi
            # nebo pokud bude otevrena, vyhleda typ
            if idVOdpovedi:
                vOdpoved = DbVyslednaOdpoved[idVOdpovedi]                
                vOdpoved.odpoved = cgi.escape(text)
            else:
                idOtOdpovedi = get(o.id for o in DbVyslednaOdpoved 
                    if o.vyslednaOtazka.id is idOtazky and o.typ == "O")
                
                if idOtOdpovedi:
                    vOdpoved = DbVyslednaOdpoved[idOtOdpovedi]                
                    vOdpoved.odpoved = cgi.escape(text)
        
        return "Test byl odeslán"                  

    def vysledekTestu(id):
        vId = get(v.id for v in DbVysledekTestu if v.id is id)

        if not vId:
            return json({"odpoved": "Tento výsledek testu neexistuje!"})       

        vTestu = DbVysledekTestu[id]

        # zjisti, jestli ma student si tento vysledek pravo zobrazit
        if uzivatel("student"):
            sId = get(s.id for s in DbStudent if s.login == uzJmeno())   
 
            if sId != vTestu.student.id:
                return json({"odpoved": "Nemáš právo zobrazit tento výsledek!"})

        vsechnyOdpovedi = select(o for o in DbVyslednaOdpoved if o.vysledekTestu.id is id).sort_by("o.typ")

        typDobre = "zadaniDobre"
        typSpatne = "zadaniSpatne"
        typOtevrena = "zadaniOtevrena" 

        oznaceneDobre = "oznaceneDobre"
        oznaceneSpatne = "oznaceneSpatne"
        oznaceneOtevrena = "oznaceneOtevrena"

        # datovy typ ktery podporuje vlozeni seznamu
        vysledek = defaultdict(dict)

        # projdou se vsechny odpovedi
        for o in vsechnyOdpovedi:
            oId = o.vyslednaOtazka.id
            typ = o.typ

            if typ == "D": typ = typDobre
            elif typ == "S": typ = typSpatne
            elif typ == "O": typ = typOtevrena 

            ocOdpoved = o.ocekavanaOdpoved
            odpoved = o.odpoved
            
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
                "jmeno":        otazka.jmeno,
                "zadani":       otazka.konkretniZadani,
                "bodu":         otazka.bodu,
                "hodnotit":     otazka.hodnotit,
                "zaokrouhlit":  otazka.zaokrouhlit,
                "tolerance":    otazka.tolerance,
                "hodnoceni":    0 
            })

            # priradi, ktere odpovedi jsou spravne a spatne
            if odpoved and ocOdpoved == odpoved and typ != typOtevrena:                       
                oznacene = oznaceneSpatne
                
                if typ == typDobre: 
                    oznacene = oznaceneDobre         

                vysledek[oId][oznacene].append(odpoved)

            if typ == typOtevrena:
                #cislena odpoved - desetinne cislo?:
                # zaokrouhli na pocet DM v DB, nahradi carku za tecku a porovna
                vysledek[oId]["ciselna"] = False
                dMista = otazka.zaokrouhlit

                # hleda cislo v odpovedi:
                if not re.match("^\d+?[\.\,]\d+?$", ocOdpoved) is None:
                    ocCislo = naDesetinne(ocOdpoved,dMista)
                    stCislo = naDesetinne(odpoved,dMista)
                    vysledek[oId]["ciselna"] = True                   

                    # pokusi se pouzit zadanou toleranci
                    if tolerance(ocCislo,stCislo,otazka.tolerance): 
                        vysledek[oId][oznaceneDobre] = odpoved
                        vysledek[oId]["hodnoceni"] = otazka.bodu
                    else: # pokud ne tak oznaci odpoved za spatnou
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
        
        if not vTestu.boduVysledek:
            vTestu.boduVysledek = boduTest
        if not vTestu.boduMax:
            vTestu.boduMax = boduMax

        procent = 100
        if boduMax != 0: procent = 100*boduTest/boduMax

        jsTest = {
            "id":       vTestu.id,
            "student":  vTestu.student.login,
            "od":       datum(vTestu.casZahajeni),
            "do":       datum(vTestu.casUkonceni),
            "boduMax":  boduMax,
            "boduTest": boduTest,
            "procent":  procent,          
            "otazky":   vysledek,
        }

        return json({"test": jsTest})

    def zobrazVysledekTestu(id):
        vId = get(v.id for v in DbVysledekTestu if v.id is id)

        if not vId:
            return "Tento výsledek testu neexistuje!"

        test = DbVysledekTestu[id]
        otazky = select(o for o in DbVyslednaOtazka if o.vysledekTestu.id is test.id)
        seznamOtazek = []

        for otazka in otazky:
            odpovedi = select(o.odpoved for o in DbVyslednaOdpoved if o.vysledekTestu.id is test.id)

            seznamOtazek.append({
                'id':           otazka.id,
                'jmeno':        otazka.jmeno,
                'zadani':       otazka.konkretniZadani,
                'bodu':         otazka.bodu,
                'odpovedi':     seznam(odpovedi)
            })

        jsTest = {
            'id':           test.id,
            'od':           test.casZahajeni.strftime(formatCasu),
            'do':           test.casUkonceni.strftime(formatCasu),
            'boduVysledek': str(test.boduVysledek),
            'boduMax':      str(test.boduMax),
            'student':      test.student.login,
            'otazky':       seznamOtazek,
        }

        return json({"test": jsTest})

    def nahrat(J):
        text = J["data"].split("\n")
        
        # ziska seznam vsech loginu:
        studenti = select(s.login for s in DbStudent)
        ucitele = select(s.login for s in DbUcitel)
        loginy = seznam(studenti) + seznam(ucitele)

        for radek in text:
            bunka = radek.split(";")                   
            if len(bunka) < 5: continue           
            prerusit = False

            # kontrola jestli login uz existuje:
            for login in loginy:
                if login == bunka[0]: 
                    prerusit = True
                    break

            if prerusit: continue

            trida = None

            if bunka[3].isdigit():
                trida = get(t.id for t in DbTridy if t.poradi == bunka[3] and t.nazev == bunka[4])

            DbStudent(
                login = bunka[0],
                jmeno = bunka[1],
                prijmeni = bunka[2],         
                trida = trida
            ) 

        return "CSV soubor se seznamem studentů byl úspěšně nahrán"

    def stahnout():
        studenti = select(s for s in DbStudent)
        #utf-8 hlavnicka, aby csv sel spravne zobrazit v Excelu
        csv = '\ufeff'

        for s in studenti:
            trida = "-;-"
            if s.trida:
                trida = str(s.trida.poradi) + ";" + s.trida.nazev
            csv += s.login + ";" + s.jmeno + ";" + s.prijmeni + ";" + trida + "\r\n"

        r = Response(response=csv,status=200,mimetype="text/plain")
        r.headers["Content-Disposition"] = 'attachment; filename="studenti.csv"'
        return r

    def zmenObsah(J):
        if J["tabulka"] != "Student" or not uzivatel("admin"):
            return "Nemáš oprávnění měnit obsah této tabulky!!!"
        
        trida = J["bunky"][3]   
        if trida == "null": trida = None
        else: trida = int(trida)

        # zkontroluje, jestli uz v tabulkach neni stejny login
        login = J["bunky"][0]
        ucitel = get(s.id for s in DbUcitel if s.login == login)
        student = get(s.id for s in DbStudent if s.login == login)

        if J["id"] == "":
            if (student or ucitel):
                return "Tento login už existuje!"
                
            DbStudent(
                login = J["bunky"][0],
                jmeno =  J["bunky"][1],
                prijmeni = J["bunky"][2],
                trida = trida
            )

            return "Byl vložen nový student."

        id = int(J["id"])

        dbId = get(o.id for o in DbStudent if o.id is id)

        if not dbId:
            return "Toto id neexistuje!"

        dbStudent = DbStudent[id]

        if (student or ucitel):
            login = dbStudent.login 

        if J["akce"] == "smazat":
            dbStudent.delete()
            return "Student byl smazán"

        elif J["akce"] == "zmenit":
            dbStudent.login = login
            dbStudent.jmeno = J["bunky"][1]
            dbStudent.prijmeni = J["bunky"][2]
            if J["bunky"][3] != "null":
                dbStudent.trida = trida

            return "Student byl změněn."

        def vlozitStudenta(login, jmeno, prijmeni):
            student = get(s.id for s in DbStudent if s.login == login)
            if student: return

            J = {}
            J["bunky"][0] = login,
            J["bunky"][1] = jmeno,
            J["bunky"][2] = prijmeni,
            J["bunky"][3] = ""  

            return Student.zmenObsah(J)
                        