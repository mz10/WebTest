from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from webtest.db import *
import json as _json

def json(js):
    return Response(response=_json.dumps(js),status=200,mimetype="application/json")

class Testy:
    def zobraz():
        seznam = []
        testy = select(o for o in DbTest)

        for p in testy:
            seznam.append({
                'id': p.id,
                'jmeno': p.jmeno,
                'od': p.zobrazenoOd.strftime("%d.%m.%Y %H:%M"),
                'do': p.zobrazenoDo.strftime("%d.%m.%Y %H:%M"),
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


    def pridat0():
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

    def pridat(J):
        nazev_testu = J['jmeno']
        datum_od = dt.strptime(J['od'], "%d.%m.%Y %H:%M")
        datum_do = dt.strptime(J['do'], "%d.%m.%Y %H:%M")
        otazky = J['otazky']

        DbTest(
            jmeno=nazev_testu, 
            ucitel=get(u for u in DbUcitel if u.login == session['ucitel']),
            zobrazenoOd=datum_od, 
            zobrazenoDo=datum_do
        )       

        for idOtazky in otazky:
            DbOtazkaTestu(
                poradi = 0, 
                test = get(u for u in DbTest if u.jmeno == nazev_testu),
                otazka = get(o for o in DbOtazka if o.id == idOtazky)
            )

        #zprava = 'Vytvořen test "' + nazev_testu + '"'
        #otazky = select((o.id, o.ucitel, o.ucitel.jmeno, o.jmeno, o.obecneZadani) for o in DbOtazka)
        #return render_template('pridat_test.html', zprava=zprava, otazky=otazky.order_by(1))
        return 'Vytvořen test: ' + nazev_testu
                


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