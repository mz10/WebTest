from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for)
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
        Otazka(ucitel=ucitel, 
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
    def zobraz():
        #: Zobrazí všechny otázky a nabídne příslušné akce
        if request.method == 'GET':
            otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno, o.obecneZadani) for o in DbOtazka)
            return render_template('otazky.html', otazky=otazky.order_by(1))
        elif request.method == 'POST':
            return redirect(url_for('/'))

    def ucitel(login):
        #: Zobrazí všechny otázky jednoho zadávajícího učitele
        otazky = select((o.id, o.ucitel.login, o.ucitel.jmeno, o.jmeno,
                        o.obecneZadani) for o in DbOtazka
                        if o.ucitel.login == login)
        return render_template('otazky.html', otazky=otazky)

class Otazka:
    def editovat(id):
        if request.method == 'GET':
            otazka = DbOtazka[id]
            return render_template('otazka_editovat.html', otazka=otazka, rendruj=rendruj)
        if request.method == 'POST':
            r = request
            F = r.form
            if F['jmeno'] and F['typ_otazky'] and F['obecne_zadani']:
                if F['typ_otazky'] == 'O':
                    otazka = DbOtazka[id]
                    otazka.ucitel = get(u for u in DbUcitel
                                        if u.login == session['ucitel'])
                    otazka.jmeno = F['jmeno']
                    otazka.typ_otazky = 'O'
                    otazka.obecneZadani = F['obecne_zadani']
                    return redirect(url_for('otazky'))
                elif F['typ_otazky'] == 'C' and F['spravna_odpoved']:
                    otazka = DbOtazka[id]
                    otazka.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
                    otazka.jmeno = F['jmeno']
                    otazka.typOtazky = 'C'
                    otazka.obecneZadani = F['obecne_zadani']
                    otazka.spravnaOdpoved = F['spravna_odpoved']
                    return redirect(url_for('otazky'))
                # TODO!
            else:
                zprava = "Nebyla zadána všechna požadovaná data."
                otazka = DbOtazka[id]
                return render_template('otazka_editovat.html', chyba=zprava, otazka=otazka)

    def smazat(id):
        #: Zobrazí všechny otázky a nabídne příslušné akce
        if request.method == 'GET':
            return render_template('otazka_smazat.html', otazka=DbOtazka[id], rendruj=rendruj)
        elif request.method == 'POST':
            if 'ano' in request.form and request.form['ano'] == 'Ano':
                DbOtazka[id].delete()
            return redirect(url_for('otazky'))

    def zobraz(id):
        otazka = DbOtazka[id]
        return render_template('otazka.html', otazka=otazka, rendruj=rendruj)

    def pridat():
        # otazka je evidovana do databaze
        # POZN.:  Spravna_odpoved musi byt VZDY uvedena, protoze je v
        #         dalsi tabulce tento parametr vyzadovan!!!
        r = request
        F = r.form
        if r.method == 'GET':
            if 'ok' in r.args:
                zprava = 'Proběhlo vložení otázky "' + r.args['ok'] + '".'
                return render_template('pridat_otazku.html', vlozeno=zprava)
            else:
                return render_template('pridat_otazku.html')
        elif r.method == 'POST':
            if F['jmeno'] and F['typ_otazky'] and F['obecne_zadani']:
                if F['typ_otazky'] == 'O':
                    with db_session:
                        DbOtazka(ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                            jmeno=F['jmeno'],
                            typOtazky='O',
                            obecneZadani=F['obecne_zadani'],
                            SprO='Otevrena otazka')
                    return redirect(url_for('pridat_otazku', ok=F['jmeno']))
                elif F['typ_otazky'] == 'C' and F['spravna_odpoved']:
                    with db_session:
                        DbOtazka(ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                            jmeno=F['jmeno'],
                            typOtazky='C',
                            obecneZadani=F['obecne_zadani'],
                            SprO=F['spravna_odpoved'])
                    return redirect(url_for('pridat_otazku', ok=F['jmeno']))
                elif F['typ_otazky'] == 'U' and F['spravna_odpoved']:
                    # Musím dát všechny špatné odpovědi těsně za sebe
                    KLICE = ('spatna_odpoved1', 'spatna_odpoved2',
                            'spatna_odpoved3', 'spatna_odpoved4',
                            'spatna_odpoved5', 'spatna_odpoved6')
                    odpovedi = []
                    for klic in KLICE:
                        if F[klic]:
                            odpovedi.append(F[klic])
                    parametry = {}
                    i = 1
                    html= ""
                    for odpoved in odpovedi:
                        parametry['SPO' + str(i)] = odpoved
                        i=i+1

                    # Chce to alespoň jednu špatnou odpověď
                    if len(parametry) < 1:
                        zprava = "... alespoň jednu špatnou odpověď!"
                        return render_template('pridat_otazku.html', chyba=zprava)
                    with db_session:
                        spravnaOdpoved = F['spravna_odpoved']
                        if F['spravna_odpoved'] == '':
                            spravnaOdpoved = 'Nespecifikovano'
                        DbOtazka(ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
                            jmeno=F['jmeno'],
                            typOtazky='U',
                            obecneZadani=F['obecne_zadani'],
                            SprO=spravnaOdpoved, **parametry)
                    return redirect(url_for('pridat_otazku', ok=F['jmeno']))
                else:
                    zprava = "U číselné otázky musí být zadán správná odpověď."\
                            " U uzavrené otázky i špatná odpověď."
                    return render_template('pridat_otazku.html', chyba=zprava)
            else:
                zprava = "Nebyla zadána všechna požadovaná data."
                return render_template('pridat_otazku.html', chyba=zprava)

class Testy:
    def zobraz():
        #seznam testu
        if request.method == 'GET':
            testy = select((u.id, u.jmeno) for u in DbTest)
            return render_template('testy.html', testy=testy)
        elif request.method == 'POST':
            return redirect(url_for('/'))

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
                    OtazkaTestu(poradi=0, test=get(u for u in DbTest
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
            otazky_all = select((u.id, u.ucitel.login, u.ucitel.jmeno, u.jmeno,
                                u.obecneZadani) for u in DbOtazka if u.id
                                not in select(ot.otazka.id for ot in DbOtazkaTestu
                                            if ot.test.id is id_test))
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
                zadani = select((u.obecneZadani, u.spravnaOdpoved)
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
            html += '\n<form method="post">\n<b>' + tabulka + '</b>\n<input type="hidden" name="tabulka" value="' + tabulka + '">'
            html += '<input type="submit" name="ok" value="Smazat">\n'
            html += '<input type="submit" name="ok" value="Vysypat">\n</form>\n'

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
        return render_template('tabulky.html', html=Markup(html)) 

    def smazTabulku():
        R = request
        F = R.form
        tabulka = F['tabulka']

        if R.method == 'POST':
            db = psycopg2.connect(udaje)
            sql = db.cursor()
            db.autocommit = True

            if F['ok'] == "Smazat":
                sql.execute('DROP TABLE "' + tabulka + '" CASCADE;')
            elif F['ok'] == "Vysypat":
                sql.execute('TRUNCATE TABLE "' + tabulka + '" CASCADE;')

        return redirect('/tabulky/')
    
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
