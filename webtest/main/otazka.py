from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from .db import *
import re
import random
import sympy
import cgi

from .funkce import (nahodne, json, jsonStahnout, vypocitej, seznam, uzivatel, uzJmeno)

class Odpovedi:
    # najde odpovedi ktere patri do otazky (podle id)
    def __init__(self,oId, promenne = {}):
        # v dotazu jsou i opakujici se odpovedi - without_distinct
        self.odpovedi = select((o.odpoved, o.typ) for o in DbOdpoved if o.otazka.id == oId).without_distinct()
        self.promenne = promenne
        self.oId = oId

    def tridit(self,typ):
        return [cgi.escape(i[0]) for i in self.odpovedi if i[1] == typ]

    def vypocitat(self,typ):
        return [cgi.escape(vypocitej(i[0],self.promenne))
            for i in self.odpovedi if i[1] == typ]
    
    def vypocitatVsechny(self):
        vysledek = []
        for o in self.odpovedi:
            odpoved = cgi.escape(vypocitej(o[0],self.promenne))
            typ = o[1]
            vysledek.append([odpoved, typ])

        return vysledek
        
    def pridat(self,odpovedi,typOdpovedi):
        for od in odpovedi:
            if od == "": continue

            DbOdpoved(
                odpoved = od,
                typ = typOdpovedi,
                otazka = self.oId
            )

class Otazka:
    def smazat():
        idOtazky = J["id"]
        DbOtazka[idOtazky].delete()
        return "Otázka s id " + idOtazky + " byla smazána"

    def smazatVsechny():
        if uzivatel("ucitel"):
            otazky = select(o for o in DbOtazka if o.ucitel.login == uzJmeno())
        elif uzivatel("admin"):
            otazky = select(o for o in DbOtazka)
        else:
            return "!!!"

        for otazka in otazky:
            otazka.delete()
        
        return "Všechny vaše otázky byly smazány."

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
            jazyk = vyraz[1]
            kategorie = vyraz[2]
            vsechno = True if kategorie == "vsechno" else False

            slova = select((s.slovo1, s.slovo2) 
                for s in DbSlovnik if (s.kategorie is kategorie or vsechno) and s.jazyk is jazyk)
            seznamSlov = seznam(slova)

            random.shuffle(seznamSlov)

            if len(seznamSlov) == 0:
                return "[spatne zadani]"

            spravne1 = seznamSlov[0][0]
            spravne2 = seznamSlov[0][1]

            promenne["slovo1.spravne"] = spravne1
            promenne["slovo2.spravne"] = spravne2

            #odebere spravne slova ze seznamu a zustanou jen spatne
            seznamSlov.pop(0)
            
            promenne["slovo1.spatne"] = []
            promenne["slovo2.spatne"] = []      

            for sl in seznamSlov:
                promenne["slovo1.spatne"].append(sl[0])
                promenne["slovo2.spatne"].append(sl[1])

            if slovo == "$slovo1":
                return spravne1
            elif slovo == "$slovo2":
                return spravne2

            return str(slovo)

        #nahradi textove promenne v [] nahodnymi cisly
        m = re.compile('\[\$*([a-z][,\-*\d+[.d+]*]*)\]').sub(nahraditPromenne,m)
        #nahradi textove promenne vypocitanym vyrazem
        m = re.compile('\[\$*([a-z])\=(.*?)\]').sub(nahraditPromenne2,m)
        #vybere slovo ze slovniku
        m = re.compile("\$slovo[1-9]\.\w+.\w+?$", re.UNICODE).sub(nahraditSlova,m)
        #vyhleda a odstrani komentare /** komentar **/
        m = re.compile(r"\/\*\*(.*?)\*\*\/?",re.DOTALL).sub("",m)
        #prevede markdown do HTML
        m = markdown(m)
        #nahradi \n novym radkem <br>
        m = m.replace("\n","<br>")

        hotovo = {}
        hotovo["promenne"] = promenne
        hotovo["html"] = Markup(m)

        return hotovo


    def zobraz(id):
        #try:
        oId = get(o.id for o in DbOtazka if o.id is id)

        if not oId:
            return "Tato otázka neexistuje!"

        otazka = DbOtazka[id]
        zadani = Otazka.vytvorZadani(otazka.obecneZadani)
        odpovedi = Odpovedi(otazka.id, zadani["promenne"])
        
        jsOtazka = {
            'id':             otazka.id,
            'jmeno':          otazka.jmeno,
            'bodu':           otazka.bodu,
            'zadani':         otazka.obecneZadani,
            'hodnotit':       otazka.hodnotit,
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
        otazky = None

        if uzivatel("ucitel"):
            otazky = select(o for o in DbOtazka if o.ucitel.login == uzJmeno()).order_by(1)
        elif uzivatel("admin"):
            otazky = select(o for o in DbOtazka).order_by(1)
        else:
            return "!!!"

        for otazka in otazky:
            zadani = Otazka.vytvorZadani(otazka.obecneZadani)

            seznamOtazek.append({
                'id':           otazka.id,
                'jmeno':        otazka.jmeno,
                'bodu':         otazka.bodu,
                'hodnotit':     otazka.hodnotit,
                'zadani':       otazka.obecneZadani,               
                'zadaniHTML':   zadani["html"],
                'autor':        otazka.ucitel.jmeno,
            })

        return json({"otazky": seznamOtazek})

    def export():
        seznamOtazek = []
        otazky = None

        if uzivatel("ucitel"):
            otazky = select(o for o in DbOtazka if o.ucitel.login == uzJmeno()).order_by(1)
        elif uzivatel("admin"):
            otazky = select(o for o in DbOtazka).order_by(1)
        else: 
            return "!!!"

        for otazka in otazky:
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

            jsOtazka = {
                'akce': 'nahrat', 
                'co': 'otazka',
                'otazky': seznamOtazek,
            }

        return jsonStahnout(jsOtazka,"otazky.txt")
        #return json(jsOtazka)

    def pridatVsechny(J):
        for otazka in J["otazky"]:
            Otazka.pridat(otazka)

        return "Otázky byly přidány"

    def pridat(J):
        if get(o.id for o in DbOtazka if o.jmeno == J["jmeno"]):
            return "Tato otázka s tímto jménem už existuje."
        
        nahodneJmeno = "_" + str(nahodne(1000,10000))

        # vytvorit prazdnou otazku, id je nezname!
        # pro prirazeni odpovedi je potreba znat id
        DbOtazka(
            ucitel = get(u for u in DbUcitel if u.login == uzJmeno()),
            jmeno = nahodneJmeno
        )           
        
        # zjistit id teto otazky
        idOtazky = get(u.id for u in DbOtazka if u.jmeno == nahodneJmeno)
        
        # vyplnit
        Otazka.upravit(J,idOtazky)

        return "Uzavřená otázka byla přidána. " + str(idOtazky)

    def upravit(J,id=0):
        idOtazky = id or int(J['id'])
        oId = get(o.id for o in DbOtazka if o.id is idOtazky)

        if not oId:
            return "Tato otázka neexistuje!"

        # odstrani JS kod ze zadani
        zadani = J['zadani'] \
            .replace("<script>","&lt;script&gt;") \
            .replace("</script>","&lt;/script&gt;")

        otazka = DbOtazka[idOtazky] 

        otazka.ucitel = get(u for u in DbUcitel if u.login == uzJmeno())
        
        jmeno = J['jmeno']
        
        # pokud se otazka prejmenuje na jmeno, ktere uz existuje,
        # zabrani prejmenovani teto otazky
        if get(o.id for o in DbOtazka if o.jmeno == J["jmeno"]):
            jmeno = otazka.jmeno

        otazka.jmeno = jmeno
        otazka.bodu = J['bodu']
        otazka.obecneZadani = zadani
        otazka.hodnotit = J['hodnotit']

        #smazat puvodni odpovedi
        select(o for o in DbOdpoved if o.otazka.id is idOtazky).delete()

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