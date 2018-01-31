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

from .funkce import (nahodne, json, jsonStahnout, vypocitej)

class Objekt(object):
    pass

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
        try:
            otazka = DbOtazka[id]
            zadani = Otazka.vytvorZadani(otazka.obecneZadani)
            prom = zadani["promenne"]

            jsOtazka = {
                'id':       otazka.id,
                'jmeno':    otazka.jmeno,
                'typ':      otazka.typOtazky,
                'zadani':   otazka.obecneZadani,
                'zadaniHTML': zadani["html"],
                'spravneZadano': [
                    otazka.SprO
                ],
                'spatneZadano': [
                    otazka.SPO1,
                    otazka.SPO2,
                    otazka.SPO3,
                    otazka.SPO4,
                    otazka.SPO5,
                    otazka.SPO6,                                                                                                                                          
                ],
                'spravne': [
                    vypocitej(otazka.SprO,prom),
                ],
                'spatne': [
                    vypocitej(otazka.SPO1,prom),
                    vypocitej(otazka.SPO2,prom),
                    vypocitej(otazka.SPO3,prom),
                    vypocitej(otazka.SPO4,prom),
                    vypocitej(otazka.SPO5,prom),
                    vypocitej(otazka.SPO6,prom),
                ],
            }

            return json({'otazka': jsOtazka})

        except:
            return json({'chyba': 'Otázka s id: ' + id + ' neexistuje!'})


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

    def export():
        seznamOtazek = []
        otazky = select(o for o in DbOtazka).order_by(1)

        for ot in otazky:
            seznamOtazek.append({
                'id': ot.id,
                'jmeno': ot.jmeno,
                'typ': ot.typOtazky,
                'zadani': ot.obecneZadani,
                'spravne': [
                    ot.SprO
                ],
                'spatne': [
                    ot.SPO1,
                    ot.SPO2,
                    ot.SPO3,
                    ot.SPO4,
                    ot.SPO5,
                    ot.SPO6,                                                                                                                                          
                ],                
            })

        return jsonStahnout(seznamOtazek,"otazky.txt")


    def ucitel(login):
        #: Zobrazí všechny otázky jednoho zadávajícího učitele
        otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno,
                        o.obecneZadani) for o in DbOtazka
                        if o.ucitel.login == login)
        return render_template('otazky.html', otazky=otazky)

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
            otazka = {}          
            otazka["ucitel"] = get(u for u in DbUcitel if u.login == session['ucitel'])
            otazka["jmeno"] = J['jmeno']
            otazka["obecneZadani"] = J['zadani']
            otazka["SprO"] = J["spravne"][0]

            if J["typ"] == 'O':
                otazka["typOtazky"] = 'O'
                otazka["SprO"] = 'Otevrena otazka'
                DbOtazka(**otazka)
                return "Otevřená otázka byla přidána."
            
            elif J["typ"] == 'C':
                otazka["typOtazky"] = 'C'
                DbOtazka(**otazka)
                return "Číselná otázka byla přidána."
            
            elif J["typ"] == 'U':           
                spatne = {}
                i=1
                for spatna in J["spatne"]:
                    spatne['SPO' + str(i)] = spatna
                    i=i+1
                
                otazka["typOtazky"] = 'U'
                DbOtazka(**otazka, **spatne)              
                return "Uzavřená otázka byla přidána. " + J['zadani']

            else:
                return "Špatně zadaný typ otázky!"


    def upravit(J):
            idOtazky = int(J['id'])
            otazka = DbOtazka[idOtazky]       
            
            otazka.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
            otazka.jmeno = J['jmeno']
            otazka.obecneZadani = J['zadani']
            otazka.SprO = J["spravne"][0]

            if J["typ"] == 'O':
                otazka.typOtazky = 'O'
                otazka.SprO = 'Otevrena otazka'
                return "Otevřená otázka byla upravena."
            
            elif J["typ"] == 'C':
                otazka.typOtazky = 'C'
                return "Číselná otázka byla upravena."
            
            elif J["typ"] == 'U':                
                otazka.typOtazky = 'U'
                otazka.SPO1 = J["spatne"][0]
                otazka.SPO2 = J["spatne"][1]
                otazka.SPO3 = J["spatne"][2]
                otazka.SPO4 = J["spatne"][3]
                otazka.SPO5 = J["spatne"][4]
                otazka.SPO6 = J["spatne"][5]
            
                #otazka(**spatne)
                return "Uzavřená otázka byla upravena. " + J['zadani']

            else:
                return "Špatně zadaný typ otázky!"