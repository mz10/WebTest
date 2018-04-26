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

from .funkce import (nahodne, json, jsonStahnout, seznam, uzivatel, uzJmeno)
from .zadani import Zadani

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
        return [cgi.escape(Zadani.vytvorOdpovedi(i[0],self.promenne))
            for i in self.odpovedi if i[1] == typ]
    
    def vypocitatVsechny(self):
        vysledek = []
        for o in self.odpovedi:
            odpoved = cgi.escape(Zadani.vytvorOdpovedi(o[0],self.promenne))
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
    def smazat(J):
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

    def zobraz(id):
        #try:
        oId = get(o.id for o in DbOtazka if o.id is id)

        if not oId:
            return "Tato otázka neexistuje!"

        otazka = DbOtazka[id]
        Zadani.promenne = {}
        zadani = Zadani.vytvorZadani(otazka.obecneZadani)
        odpovedi = Odpovedi(otazka.id, zadani["promenne"])
        
        jsOtazka = {
            'id':             otazka.id,
            'jmeno':          otazka.jmeno,
            'bodu':           otazka.bodu,
            'zadani':         otazka.obecneZadani,
            'hodnotit':       otazka.hodnotit,
            'zadaniHTML':     zadani["html"],
            'tolerance':      otazka.tolerance,
            'zaokrouhlit':    otazka.zaokrouhlit,
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
            zadani = Zadani.vytvorZadani(otazka.obecneZadani)

            seznamOtazek.append({
                'id':           otazka.id,
                'jmeno':        otazka.jmeno,
                'bodu':         otazka.bodu,
                'hodnotit':     otazka.hodnotit,
                'zadani':       otazka.obecneZadani,               
                'zadaniHTML':   zadani["html"],
                'tolerance':    otazka.tolerance,
                'zaokrouhlit':  otazka.zaokrouhlit,
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
                'id':           otazka.id,
                'jmeno':        otazka.jmeno,
                'bodu':         otazka.bodu,
                'hodnotit':     otazka.hodnotit,
                'zadani':       otazka.obecneZadani,
                'tolerance':    otazka.tolerance,
                'zaokrouhlit':  otazka.zaokrouhlit,
                'spravne':      odpovedi.tridit("D"),  
                'spatne':       odpovedi.tridit("S"), 
                'otevrena':     odpovedi.tridit("O"),  
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
        otazka.tolerance = J['tolerance']
        otazka.zaokrouhlit = J['zaokrouhlit']

        #smazat puvodni odpovedi
        select(o for o in DbOdpoved if o.otazka.id is idOtazky).delete()

        odpovedi = Odpovedi(otazka.id)           
        odpovedi.pridat(J["spravne"],"D")
        odpovedi.pridat(J["spatne"],"S")
        odpovedi.pridat(J["otevrena"],"O")

        return "Uzavřená otázka byla upravena. " + str(idOtazky)

    # vytvoří náhled zadani v editoru
    def nahled(zadani):
        Zadani.promenne = {}
        zadani = Zadani.vytvorZadani(zadani)
        return zadani["html"]