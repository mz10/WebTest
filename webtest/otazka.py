from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from webtest.db import *
import re
import random
import sympy

from .funkce import (nahodne, json, jsonStahnout, vypocitej, seznam)

class Odpovedi:
    # najde odpovedi ktere patri do otazky (podle id)
    def __init__(self,oId, promenne = {}):
        self.odpovedi = select((o.odpoved, o.typ) for o in DbOdpovedi if o.otazka.id == oId) 
        self.promenne = promenne
        self.oId = oId

    def tridit(self,typ):
        return [i[0] for i in self.odpovedi if i[1] == typ]

    def vypocitat(self,typ):
        return [vypocitej(i[0],self.promenne) for i in self.odpovedi if i[1] == typ]

    def pridat(self,odpovedi,typOdpovedi):
        for od in odpovedi:
            if od == "": continue

            DbOdpovedi(
                odpoved = od,
                typ = typOdpovedi,
                otazka = self.oId
            ) 


class Otazka:

    def vytvorZadani(m):
        promenne = {}

        def nahraditPromenne(m):
            rozdeleno = m.groups(0)[0].split(",")
            promenna = rozdeleno[0]

            #overi jestli promenna uz existuje
            #pokud jo, tak ji nahradi stejnou hodnotou   
            if promenna in promenne:
                return str(promenne[promenna])

            try:
                vysledek = "[spatne zadano]"
                
                if len(rozdeleno) == 1:
                    vysledek = random.randint(0,1000)
                elif len(rozdeleno) == 2:
                    od = int(rozdeleno[1])
                    
                    if od < 0:
                        vysledek = random.randint(od,0)
                    else:
                        vysledek = random.randint(0,od)
                elif len(rozdeleno) == 3:
                    od = int(rozdeleno[1])
                    do = int(rozdeleno[2]) 
                    
                    if od>do:
                        vysledek = random.randint(do,od)
                    else:
                        vysledek = random.randint(od,do)
                elif len(rozdeleno) == 4:
                    od = float(rozdeleno[1])
                    do =  float(rozdeleno[2])  
                    zaokrouhlit = int(rozdeleno[3])
                    
                    if od>do:
                        vysledek = random.uniform(do,od)     
                    else:
                        vysledek = random.uniform(od,do)
                    
                    vysledek = round(vysledek,zaokrouhlit)
                
            except Exception as e:
                promenne[promenna] = 0
                return "[chyba ve vyrazu 1]"
                #return str(e)

            promenne[promenna] = str(vysledek)
            return str(vysledek)

        def nahraditPromenne2(m):
            promenna = m.group(1)
            vyraz = m.group(2)
            
            #dosadit promenne do vyrazu
            for p, hodnota in sorted(promenne.items()):
                vyraz = vyraz.replace("$" + p,hodnota)    
            
            #vypocitat vyraz 
            try:
                vysledek = str(sympy.simplify(vyraz))
            except:
                promenne[promenna] = "0"
                return "[chyba ve vyrazu 2]"
            
            #pridat vysledek do seznamu promennych
            promenne[promenna] = vysledek
            return vysledek

        def nahraditSlova(m):
            vyraz = m.group(0).split(".")
            slovo = vyraz[0]
            kategorie = vyraz[1]
            slova = select((s.slovo1, s.slovo2) for s in DbSlovnik if s.typ is kategorie)

            seznamSlov = seznam(slova)
            slovo12 = random.choice(seznamSlov)

            promenne["slovo1.spravne"] = slovo12[0]
            promenne["slovo2.spravne"] = slovo12[1]

            if slovo == "$slovo1":
                return slovo12[0]
            elif slovo == "$slovo2":
                return slovo12[1]

            return str(slovo)

        #nahradi textove promenne v [] nahodnymi cisly
        m = re.compile('\[\$*([a-z][,\-*\d+[.d+]*]*)\]').sub(nahraditPromenne,m)
        #nahradi textove promenne vypocitanym vyrazem
        m = re.compile('\[\$*([a-z])\=(.*?)\]').sub(nahraditPromenne2,m)
        #vybere slovo ze slovniku
        m = re.compile("\$slovo[1-9]\.([a-z])+").sub(nahraditSlova,m)

        #prevede markdown do HTML
        m = typogrify(markdown(m))
        #nahradi \n novym radkem <br>
        m = m.replace("\n","<br>")

        hotovo = {}
        hotovo["promenne"] = promenne
        hotovo["html"] = Markup(m)

        return hotovo


    def zobraz(id):
        #try:
        otazka = DbOtazka[id]
        zadani = Otazka.vytvorZadani(otazka.obecneZadani)
        odpovedi = Odpovedi(otazka.id, zadani["promenne"])

        jsOtazka = {
            'id':             otazka.id,
            'jmeno':          otazka.jmeno,
            'bodu':           otazka.bodu,
            'zadani':         otazka.obecneZadani,
            'zadaniHTML':     zadani["html"],
            'spravneZadano':  odpovedi.tridit("D"),
            'spatneZadano':   odpovedi.tridit("S"),
            'otevrenaZadano': odpovedi.tridit("O"),
            'spravne':        odpovedi.vypocitat("D"),
            'spatne':         odpovedi.vypocitat("S"),
            'otevrena':       odpovedi.vypocitat("O"),
        }

        return json({'otazka': jsOtazka})

        #except:
        #    return json({'chyba': 'Otázka s id: ' + id + ' neexistuje!'})


    def zobrazOtazky():
        seznamOtazek = []
        otazky = select(o for o in DbOtazka).order_by(1)

        for ot in otazky:
            zadani = Otazka.vytvorZadani(ot.obecneZadani)

            seznamOtazek.append({
                'id':           ot.id,
                'jmeno':        ot.jmeno,
                'bodu':         ot.bodu,
                'zadani':       ot.obecneZadani,
                'zadaniHTML':   zadani["html"],
                'autor':        ot.ucitel.jmeno,
            })

        return json({"otazky": seznamOtazek})

    def export():
        seznamOtazek = []
        otazky = select(o for o in DbOtazka).order_by(1)

        for otazka in otazky:
            odpovedi = Odpovedi(otazka.id)

            seznamOtazek.append({
                'id':       otazka.id,
                'jmeno':    otazka.jmeno,
                'zadani':   otazka.obecneZadani,
                'spravne':  odpovedi.tridit("D"),  
                'spatne':   odpovedi.tridit("S"), 
                'otevrena': odpovedi.tridit("O"),  
            })

        #return jsonStahnout(seznamOtazek,"otazky.txt")
        return json(seznamOtazek)

    def pridat(J):
        with db_session:
            nahodneJmeno = "_" + str(nahodne(1000,10000))

            # vytvorit prazdnou otazku, id je nezname!
            # pro prirazeni odpovedi je potreba znat id
            DbOtazka(
                ucitel = get(u for u in DbUcitel if u.login == session['ucitel']),
                jmeno = nahodneJmeno
            )           
            
            # zjistit id teto otazky
            idOtazky = get(u.id for u in DbOtazka if u.jmeno == nahodneJmeno)
            
            # vyplnit
            Otazka.upravit(J,idOtazky)

            return "Uzavřená otázka byla přidána. " + str(idOtazky)

    def upravit(J,id=0):        
            idOtazky = id or int(J['id'])
            otazka = DbOtazka[idOtazky]                 
            otazka.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
            
            otazka.jmeno = J['jmeno']
            otazka.bodu = J['bodu']
            otazka.obecneZadani = J['zadani']

            #smazat puvodni odpovedi
            select(o for o in DbOdpovedi if o.otazka.id is idOtazky).delete()

            odpovedi = Odpovedi(otazka.id)           
            odpovedi.pridat(J["spravne"],"D")
            odpovedi.pridat(J["spatne"],"S")
            odpovedi.pridat(J["otevrena"],"O")

            return "Uzavřená otázka byla upravena. " + str(idOtazky)


    #############################################

    def ucitel(login):
        # Zobrazí všechny otázky jednoho zadávajícího učitele
        otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno,
                        o.obecneZadani) for o in DbOtazka
                        if o.ucitel.login == login)
        return render_template('otazky.html', otazky=otazky)