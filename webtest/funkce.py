from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)

import psycopg2
from datetime import datetime as dt
import time
import os
import functools
import random
import sys
from webtest.db import *
import json as _json

udaje = "host='localhost' user='postgres' password='a' dbname='webtest'"

"""
def pswd_check(pswd, encript):
    i = encript.rfind('$')
    salt = encript[:i]
    return encript == crypt(pswd, salt)
"""

def rendruj(m):
    return Markup(typogrify(markdown(m)))
############################################################################

def pswd_check(pswd, encript):
    return True   

def vysledky1():
    if request.method == 'GET':
        seznam_testu = select((u.jmeno, u.id) for u in DbTest)
        return render_template('vysledky.html', seznam_testu=seznam_testu)

def nahodne(a,b):
    return str(random.randint(a,b))

def json(js):
    return Response(response=_json.dumps(js),status=200,mimetype="application/json")

def upload1():
    """upload souboru se zadáním
    """
    def add(typ, nazev_otazky, cislo, otazka, spravna, spatna):
        """zapis do databaze
        """
        ucitel = get(u for u in Ucitel if u.login == session['ucitel'])
        while len(spatna) < 7:  # doplni hodnoty NULL do nevyuzitych mist
            spatna.append('Null')

        # prevede polozky seznamu na UNICODE
        spatna = [unicode(i) for i in spatna]
        DbOtazka(ucitel=ucitel, 
               jmeno=nazev_otazky, 
               typOtazky=typ,
               obecneZadani='10', 
               SprO=spravna,
               SPO1=spatna[0],
               SPO2=spatna[1],
               SPO3=spatna[2],
               SPO4=spatna[3],
               SPO5=spatna[4],
               SPO6=spatna[5])
        # Obecne_zadani nastaveno perma na 10

    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        if 'datafile' in request.files:
            fil = request.files['datafile']
            typ = cislo = nazev_otazky = otazka = spravna = ""
            spatna = []  # seznam spatnych odpovedi
            for line in fil:
                radek = line.strip().decode('UTF-8')
                if line != '\n':  # ignoruj prazdne radky
                    if radek.split()[0] == '::date':
                        #  datum = " ".join(radek.split()[1:])
                        pass
                    elif radek.split()[0] == '::number':
                        typ = 'C'
                        spravna = " ".join(radek.split()[1:])
                    elif radek.split()[0] == ':+':
                        spravna = " ".join(radek.split()[1:])
                    elif radek.split()[0] == ':-':
                        spatna.append(radek.split()[1:])
                    elif radek.split()[0] == '::task':
                        nazev_otazky = " ".join(radek.split()[1:])
                    elif radek.split()[0] == '::open':
                        typ = 'O'
                    elif radek.split()[0] == '::close':
                        typ = 'U'
                    else:
                        otazka = otazka + line
                else:  # kdyz je mezera(oddeleni otazek), udelej zapis do DB
                    # ignoruj 1.mezeru či  nekor. otazky
                    if nazev_otazky and otazka:
                        add(typ, nazev_otazky, cislo, otazka, spravna, spatna)
                    # vynuluj
                    typ = nazev_otazky = cislo = otazka = spravna = ""
                    spatna = []
        return redirect(url_for('upload'))

class Prihlaseni:
    def prihlasit():
        if request.method == 'GET':
            with db_session:
                if 'student' in session:
                    student = get(s for s in Student
                                if s.login == session['student'])
                    return render_template('login.html', jmeno=student.jmeno)
                elif 'ucitel' in session:
                    ucitel = get(u for u in Ucitel
                                if u.login == session['ucitel'])
                    return render_template('login.html', jmeno=ucitel.jmeno)
            if 'url' in request.args:
                return render_template('login.html', url=request.args['url'])
            else:
                return render_template('login.html')
        elif request.method == 'POST':
            login = request.form['login']
            heslo = request.form['passwd']
            with db_session:
                student_hash = get(s.hash for s in Student if s.login == login)
                ucitel_hash = get(u.hash for u in Ucitel if u.login == login)
            if student_hash and pswd_check(heslo, student_hash):
                session['student'] = login
                if 'url' in request.form:
                    return redirect(request.form['url'])
                else:
                    return redirect(url_for('index'))
            elif ucitel_hash and pswd_check(heslo, ucitel_hash):
                session['ucitel'] = login
                if 'url' in request.form:
                    return redirect(request.form['url'])
                else:
                    return redirect(url_for('index'))
            else:  # špatně
                if 'url' in request.form:
                    return render_template('login.html', spatne=True,
                                        url=request.form['url'])
                else:
                    return render_template('login.html', spatne=True)

    def odhlasit():
        if 'student' in session:
            session.pop('student', None)
        elif 'ucitel' in session:
            session.pop('ucitel', None)
        return redirect(url_for('login'))

class Ucitel:
    def zobrazTest(id):
        """zobrazi obsah vyplneneho testu studenta"""
        if request.method == 'GET':
            otazky = select((u.konkretni_zadani, u.ocekavana_odpoved,
                            u.konkretniOdpoved,
                            u.otazkaTestu.otazka.typOtazky) for u in Odpoved if
                            u.vysledek_testu.id is id)[:]
            print(otazky)
            return render_template('student_vysledky_zobraz.html', otazky=otazky)


    def vyplneno(id):
        """seznam uzivatelu, kteri vyplnili test"""
        if request.method == 'GET':
            nazev_testu = get(u.jmeno for u in DbTest if u.id is id)
            seznam_zaku = select((u.student.jmeno, u.id, u.casUkonceni) for u in
                                DbVysledekTestu if u.test.id is id)
            return render_template('vypracovane_testy.html', seznamZaku=seznam_zaku, nazevTestu=nazev_testu)

    def vysledky():
        if request.method == 'GET':
            seznam_testu = select((u.jmeno, u.id) for u in DbTest)
            return render_template('vysledky.html', seznamTestu=seznam_testu)

class Otazky:
    def zobraz0():
        #: Zobrazí všechny otázky a nabídne příslušné akce
        if request.method == 'GET':
            otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno, o.obecneZadani) for o in DbOtazka)
            return render_template('otazky.html', otazky=otazky.order_by(1))
        elif request.method == 'POST':
            return redirect(url_for('/'))

    def zobraz():
        seznamOtazek = []
        otazky = select(o for o in DbOtazka).order_by(1)

        for ot in otazky:
            seznamOtazek.append({
                'id': ot.id,
                'jmeno': ot.jmeno,
                'typ': ot.typOtazky,
                'zadani': ot.obecneZadani,
                'autor': ot.ucitel.jmeno,
            })

        return json({"otazky": seznamOtazek})


    def ucitel(login):
        #: Zobrazí všechny otázky jednoho zadávajícího učitele
        otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno,
                        o.obecneZadani) for o in DbOtazka
                        if o.ucitel.login == login)
        return render_template('otazky.html', otazky=otazky)

class Otazka:
    def editovat(J):
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

    def zobraz(id):
        try:
            otazka = DbOtazka[id]
            otazka.SPO1 = otazka.SprO.replace("nahodne",nahodne(2,50))

            jsOtazka = {
                'id':       otazka.id,
                'jmeno':    otazka.jmeno,
                'typ':      otazka.typOtazky,
                'zadani':   otazka.obecneZadani,
                'spravne': [
                    otazka.SprO,
                ],
                'spatne': [
                    otazka.SPO1,
                    otazka.SPO2,
                    otazka.SPO3,
                    otazka.SPO4,
                    otazka.SPO5,
                    otazka.SPO6,
                ]
            }

            return json({'otazka': jsOtazka})

        except:
            return json({'chyba': 'Otázka s id: ' + id + ' neexistuje!'})

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


class Testy:
    def zobraz0():
        #seznam testu
        if request.method == 'GET':
            testy = select((u.id, u.jmeno) for u in DbTest)
            return render_template('testy.html', testy=testy)
        elif request.method == 'POST':
            return redirect(url_for('/'))

    def zobraz():
        seznam = []
        testy = select(o for o in DbTest)

        for p in testy:
            seznam.append({
                'id': p.id,
                'jmeno': p.jmeno,
                'od': str(p.zobrazenoOd),
                'do': str(p.zobrazenoDo),
                'autor': p.ucitel.jmeno,
            })

        return json({"testy": seznam})




    def uprav(id_test):
        #uprava vytvoreneho testu
        if request.method == 'POST':
            if 'upravit' in request.form:
                nazev_testu = request.form['nazev_testu']
                platne_od = request.form['datum1'] + " " + request.form['cas_od']
                platne_do = request.form['datum2'] + " " + request.form['cas_do']
                datum_od = dt.strptime(platne_od,"%d.%m.%Y %H:%M")
                datum_do = dt.strptime(platne_do,"%d.%m.%Y %H:%M")
                checked = request.form.getlist('check')
                # smaz puvodni zaznam test-otazky
                get(u for u in DbTest if u.id is id_test).delete()
                # vytvor nove zaznamy
                DbTest(jmeno=nazev_testu,
                    ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                    zobrazenoOd=datum_od, zobrazenoDo=datum_do)
                for otazka in checked:
                    DbOtazkaTestu(poradi=0, test=get(u for u in DbTest
                                                    if u.jmeno == nazev_testu),
                                otazka=get(o for o in DbOtazka
                                            if o.jmeno == otazka))
                zprava = 'Test "' + nazev_testu + '" byl úspěšně upraven'
                testy = select((u.id, u.jmeno) for u in DbTest)
                return render_template('testy.html', zprava=zprava, testy=testy)
            if 'smazat' in request.form:
                get(u for u in DbTest if u.id is id_test).delete()
                zprava = 'smazan test "' + request.form['nazev_testu'] + '"'
                testy = select((u.id, u.jmeno) for u in DbTest)
                return render_template('testy.html', zprava=zprava, testy=testy)
        elif request.method == 'GET':
            test = select((u.id, u.jmeno) for u in DbTest
                        if u.id is id_test)
            datum = select((u.zobrazenoOd, u.zobrazenoDo)
                        for u in DbTest if u.id is id_test).get()
            datum_od, cas_od = (datum[0]).strftime("%d.%m.%Y %H:%M").split()
            datum_do, cas_do = (datum[1]).strftime("%d.%m.%Y %H:%M").split()
            
            # vyber ucitelem zvolene testy
            testy = select((u.otazka.id, u.otazka.ucitel.login,
                            u.otazka.ucitel.jmeno, u.otazka.jmeno,
                            u.otazka.obecneZadani)for u in DbOtazkaTestu if
                        u.test.id is id_test)
           
            # vyber vsechny testy
            otazky_all = select((u.id, u.ucitel.login, u.ucitel.jmeno, u.jmeno,u.obecneZadani) 
                                    for u in DbOtazka if u.id not in select(ot.otazka.id 
                                        for ot in DbOtazkaTestu if ot.test.id is id_test)
                                )
            return render_template('upravit_test.html', test=test,
                                otazky=testy, casOd=cas_od, casDo=cas_do,
                                datumOd=datum_od, datumDo=datum_do,
                                otazku=otazky_all)


    def pridat():
        """pridat test z již vložených otázek a určit dobu platnosti testu"""
        if request.method == 'GET':
            otazky = select((o.id, o.ucitel, o.ucitel.jmeno, o.jmeno, o.obecneZadani) for o in DbOtazka)
            return render_template('pridat_test.html', otazky=otazky.order_by(1))
        elif request.method == 'POST':
            nazev_testu = request.form['nazev_testu']
            platne_od = request.form['datum1'] + " " + request.form['cas_od']
            platne_do = request.form['datum2'] + " " + request.form['cas_do']
            datum_od = dt.strptime(platne_od, "%d.%m.%Y %H:%M")
            datum_do = dt.strptime(platne_do, "%d.%m.%Y %H:%M")
            checked = request.form.getlist('check')
            DbTest( jmeno=nazev_testu, 
                    ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                    zobrazenoOd=datum_od, 
                    zobrazenoDo=datum_do
                  )
            for otazkaF in checked:
                DbOtazkaTestu(poradi=0, 
                              test=get(u for u in DbTest if u.jmeno == nazev_testu),
                              otazka=get(o for o in DbOtazka if o.jmeno == otazkaF)
                              #test=1,
                              #otazka=1
                             )
            zprava = 'Vytvořen test "' + nazev_testu + '"'
            otazky = select((o.id, o.ucitel, o.ucitel.jmeno, o.jmeno, o.obecneZadani) for o in DbOtazka)
            return render_template('pridat_test.html', zprava=zprava, otazky=otazky.order_by(1))

class Student:
    def testy():
        if request.method == 'GET':
            pritomnost = dt.strptime(
                time.strftime("%d.%m.%Y %H:%M"), "%d.%m.%Y %H:%M")
            testy = select((u.id, u.jmeno, u.zobrazenoOd, u.zobrazenoDo)
                        for u in DbTest if (pritomnost >= u.zobrazenoOd and
                                            pritomnost <= u.zobrazenoDo))
            return render_template('student.html', testy=testy)

    def zobrazit(id):
        if request.method == 'GET':
            global zacatek_testu
            zacatek_testu = (dt.now()).strftime("%d.%m.%Y %H:%M:%S")
            shluk_otazek = []
            otazky_testu = select((u.otazka.id,
                                u.otazka.typOtazky,
                                u.otazka.obecneZadani,
                                u.otazka.SprO,
                                u.otazka.SPO1,
                                u.otazka.SPO2,
                                u.otazka.SPO3,
                                u.otazka.SPO4,
                                u.otazka.SPO5,
                                u.otazka.SPO6) for u in DbOtazkaTestu if u.test.id is id)
            for ramec in otazky_testu:
                vysledek = []
                for clen in ramec[4:]:
                    vysledek.append(clen)
                
                random.shuffle(vysledek)
                vysledek.insert(0, ramec[0])
                vysledek.insert(1, ramec[1])
                vysledek.insert(2, ramec[2])
                vysledek.insert(3, ramec[3])
                shluk_otazek.append(vysledek)
            
            random.shuffle(shluk_otazek)

            DbVysledekTestu(student=get(s.id for s in DbStudent if s.login == session['student']),
                            test=get(u.id for u in DbTest if u.id is id),
                            casZahajeni=zacatek_testu
                           )
            return render_template('student_testy.html', otazkaTestu=shluk_otazek)
        elif request.method == 'POST':
            checked = request.form
            konec_testu = dt.now().strftime("%d.%m.%Y %H:%M:%S")
            DbVysledekTestu(student=get(s.id for s in DbStudent if s.login == session['student']),
                            test=get(u.id for u in DbTest if u.id is id),
                            casZahajeni=zacatek_testu,
                            casUkonceni=konec_testu)
            for ch in checked:
                zadani = select((u.obecneZadani, u.SprO)
                                for u in DbOtazka if u.id is ch).get()
                konk_odpoved = request.form.get("%s" % ch)
                if not konk_odpoved:
                    konk_odpoved = "Nevyplneno"
                
                idcko = get(u.id for u in DbOtazkaTestu if u.otazka.id is ch and u.test.id is id)
                if not idcko:
                    idcko = "Nevyplneno"
                id_vysledek = select(max(u.id) for u in DbVysledekTestu
                                    if u.student.login == session['student'] and u.test.id is id)[:]
                # vlozeni
                if len(zadani) == 1:
                    zadani.append("Nespecifikovano")
                else:
                    zadani1 = zadani[1]

                DbOdpoved(  konkretniZadani=zadani[0],
                            ocekavanaOdpoved=zadani1,
                            konkretniOdpoved=konk_odpoved,
                            vysledekTestu=id_vysledek[0],
                            otazkaTestu=idcko
                         )
            return redirect(url_for('student_testy'))

    def vysledky():
        if request.method == 'GET':
            testy_uzivatele = select((u.test.jmeno, u.casUkonceni, u.id) for u in DbVysledekTestu
                                    if u.student.login is session['student'])
            for test in testy_uzivatele:
                print (test)
        return render_template('student_vysledky.html', testyUzivatele=testy_uzivatele)

class Prihlaseni:
    def prihlasit():
        if request.method == 'GET':
            with db_session:
                if 'student' in session:
                    student = get(s for s in DbStudent
                                if s.login == session['student'])
                    return render_template('login.html', jmeno=student.jmeno)
                elif 'ucitel' in session:
                    ucitel = get(u for u in DbUcitel
                                if u.login == session['ucitel'])
                    return render_template('login.html', jmeno=ucitel.jmeno)
            if 'url' in request.args:
                return render_template('login.html', url=request.args['url'])
            else:
                return render_template('login.html')
        elif request.method == 'POST':
            login = request.form['login']
            heslo = request.form['passwd']
            with db_session:
                student_hash = get(s.hash for s in DbStudent if s.login == login)
                ucitel_hash = get(u.hash for u in DbUcitel if u.login == login)
            if student_hash and pswd_check(heslo, student_hash):
                session['student'] = login
                if 'url' in request.form:
                    return redirect(request.form['url'])
                else:
                    return redirect(url_for('index'))
            elif ucitel_hash and pswd_check(heslo, ucitel_hash):
                session['ucitel'] = login
                if 'url' in request.form:
                    return redirect(request.form['url'])
                else:
                    return redirect(url_for('index'))
            else:  # špatně
                if 'url' in request.form:
                    return render_template('login.html', spatne=True, url=request.form['url'])
                else:
                    return render_template('login.html', spatne=True)

    def odhlasit():
        if 'student' in session:
            session.pop('student', None)
        elif 'ucitel' in session:
            session.pop('ucitel', None)
        return redirect(url_for('login'))


class Ostatni:
    def novaTabulka():
        db = psycopg2.connect(udaje)
        sql = db.cursor()
        db.autocommit = True

        sql.execute("CREATE TABLE IF NOT EXISTS \
            tabTest (neco VARCHAR(50), cisla INTEGER);")

        vlozit = "INSERT INTO tabTest VALUES ('test', 20);"
        sql.execute(vlozit)

        return "vytvoreno"

    def uklidDb():
        db = psycopg2.connect(udaje)
        sql = db.cursor()
        db.autocommit = True

        html="Vsechny tyto tabulky byly smazany:<br>"

        #smazat tabulku:
        sql.execute("select * from pg_tables where schemaname = 'public';");   
        for radek in sql.fetchall():
            html += radek[1] + "<br>"
            sql.execute('DROP TABLE "' + radek[1] + '" CASCADE;')

        sql.close()
        db.close()
        return Markup(html)

    def databaze():
        db = psycopg2.connect(udaje)
        sql = db.cursor()
        db.autocommit = True

        html = ""
        
        #tabulky
        sql.execute("select * from pg_tables where schemaname = 'public';")
        for radek in sql.fetchall():
            tabulka = radek[1]  
            html += '<span class="tbNazev">' + tabulka + '</span>'
            html += '<button class="tbSmazat" value="' + tabulka + '">Smazat</button>'
            html += '<button class="tbVysypat" value="' + tabulka + '">Vysypat</button>'

            #sloupce
            sql.execute("select * from information_schema.columns where table_name=%s;", (tabulka,))
            html += '<table border="1" class="tabulka"><tr>' 
            
            for radek in sql.fetchall():
                html += "<th>" + radek[3] + "</th>"

            html += '</tr>'

            #obsah tabulky
            sql.execute('SELECT * FROM "' + tabulka + '";')       
            for radek in sql.fetchall():
                html += '<tr>'
                
                for bunka in radek:      
                    html += "<td>" + str(bunka) + "</td>"

                html += '</tr>'

            html+="</table>"

        sql.close()
        db.close()
        
        return Markup(html)
        #return render_template('tabulky.html', html=Markup(html)) 

    def smazTabulku(tabulka,akce):
        db = psycopg2.connect(udaje)
        sql = db.cursor()
        db.autocommit = True

        if akce == "smazat":
            sql.execute('DROP TABLE "' + tabulka + '" CASCADE;')
        elif akce == "vysypat":
            sql.execute('TRUNCATE TABLE "' + tabulka + '" CASCADE;')

    def registrace():   
        R = request
        F = R.form
        
        if R.method == 'POST':
            with db_session:
                if F['ok'] == 'Ucitel':
                    DbUcitel(
                        login=  F['login'],
                        jmeno=  F['jmeno'],
                        hash=   F['heslo']
                    )
                elif F['ok'] == 'Student':
                    DbStudent(
                        login=  F['login'],
                        jmeno=  F['jmeno'],
                        hash=   F['heslo']
                    )
        
        return render_template('registrace.html')
