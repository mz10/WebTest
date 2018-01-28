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

from .funkce import (nahodne, json, vypocitej)

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
                vyraz = vyraz.replace("§" + p,hodnota)    
            
            #vypocitat vyraz 
            try:
                vysledek = str(sympy.simplify(vyraz))
            except:
                promenne[promenna] = "0"
                return "[chyba ve vyrazu 2]"
            
            #pridat vysledek do seznamu promennych
            promenne[promenna] = vysledek
            return vysledek

        #nahradi textove promenne v [] nahodnymi cisly
        m = re.compile('\[§*([a-z][,\-*\d+[.d+]*]*)\]').sub(nahraditPromenne,m)
        #nahradi textove promenne vypocitanym vyrazem
        m = re.compile('\[§*([a-z])\=(.*?)\]').sub(nahraditPromenne2,m)
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
        otazka.SPO1 = otazka.SprO.replace("nahodne",nahodne(2,50))
        zadani = Otazka.vytvorZadani(otazka.obecneZadani)
        
        jsOtazka = {
            'id':       otazka.id,
            'jmeno':    otazka.jmeno,
            'typ':      otazka.typOtazky,
            'zadani':   otazka.obecneZadani,
            'zadaniHTML': zadani["html"],
            'spravne': [
                vypocitej(otazka.SprO,zadani["promenne"]),
            ],
            'spatne': [
                vypocitej(otazka.SPO1,zadani["promenne"]),
                vypocitej(otazka.SPO2,zadani["promenne"]),
                vypocitej(otazka.SPO3,zadani["promenne"]),
                vypocitej(otazka.SPO4,zadani["promenne"]),
                vypocitej(otazka.SPO5,zadani["promenne"]),
                vypocitej(otazka.SPO6,zadani["promenne"]),
            ]
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
                'id': ot.id,
                'jmeno': ot.jmeno,
                'typ': ot.typOtazky,
                'zadani': ot.obecneZadani,
                'zadaniHTML': zadani["html"],
                'autor': ot.ucitel.jmeno,
            })

        return json({"otazky": seznamOtazek})


    def ucitel(login):
        #: Zobrazí všechny otázky jednoho zadávajícího učitele
        otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno,
                        o.obecneZadani) for o in DbOtazka
                        if o.ucitel.login == login)
        return render_template('otazky.html', otazky=otazky)

    def upravit(J):
        idOtazky = int(J['id'])

        if J['jmeno'] and J['typ'] and J['zadani']:
            otazka = DbOtazka[idOtazky]
            otazka.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
            otazka.jmeno = J['jmeno']
            otazka.typTtazky = J['typ']
            otazka.obecneZadani = J['zadani']            
                       
            if J['typ'] == 'O':
                return "Otevřená otázka byla upravena."
            elif J['typ'] == 'C' and J['spravne'][0]:
                otazka.SprO = J['spravne'][0]
                return "Číselná otázka byla upravena."
            elif J['typ'] == 'U':
                otazka.SprO = J['spravne'][0]
                return "Uzavřená otázka byla upravena."                       
        else:
            return "Nebyly zadány všechny požadované údaje."

    def smazat(id):
        #: Zobrazí všechny otázky a nabídne příslušné akce
        if request.method == 'GET':
            return render_template('otazka_smazat.html', otazka=DbOtazka[id], rendruj=rendruj)
        elif request.method == 'POST':
            if 'ano' in request.form and request.form['ano'] == 'Ano':
                DbOtazka[id].delete()
            return redirect(url_for('otazky'))

    def pridat(J):
        with db_session:
            if J["typ"] == 'O':
                DbOtazka(
                    ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                    jmeno=J['jmeno'],
                    typOtazky='O',
                    obecneZadani=J['zadani'],
                    SprO='Otevrena otazka'
                )
                return "Otevřená otázka byla přidána."
            elif J["typ"] == 'C':
                DbOtazka(
                    ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                    jmeno=J['jmeno'],
                    typOtazky='C',
                    obecneZadani=J['zadani'],
                    SprO=J["spravne"][0]
                )
                return "Číselná otázka byla přidána."
            elif J["typ"] == 'U':
                spatne = {}
                i=1
                for spatna in J["spatne"]:
                    spatne['SPO' + str(i)] = spatna
                    i=i+1

                spravnaOdpoved = J["spravne"][0]
                if J["spravne"][0] == '':
                    spravnaOdpoved = 'Nespecifikovano'
                DbOtazka(
                    ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                    jmeno=J['jmeno'],
                    typOtazky='U',
                    obecneZadani=J['zadani'],
                    SprO=spravnaOdpoved, 
                    **spatne
                )
                return "Uzavřená otázka byla přidána. " + J['zadani']
            else:
                return "Špatně zadaný typ otázky!"