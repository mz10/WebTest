from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from webtest.db import *
import json as _json

from .funkce import (json)

formatCasu = "%d.%m.%Y %H:%M"

class Testy:
    def zobraz():
        seznam = []
        testy = select(o for o in DbTest)

        for t in testy:
            seznamOtazek = []

            for o in select(o for o in DbOtazkaTestu if o.test.id is t.id):
                seznamOtazek.append(o.otazka.id)

            seznam.append({
                'id': t.id,
                'jmeno': t.jmeno,
                'od': t.zobrazenoOd.strftime(formatCasu),
                'do': t.zobrazenoDo.strftime(formatCasu),
                'autor': t.ucitel.login,
                'otazky': seznamOtazek
            })

        return json({"testy": seznam})

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


    def uprav(J):
        nazev_testu = J['jmeno']
        datum_od = dt.strptime(J['od'], formatCasu)
        datum_do = dt.strptime(J['do'], formatCasu)
        zprava = "Vytvořen"
        test = DbTest
        idTestu = J['id']
        test = DbTest[idTestu]

        test.jmeno = nazev_testu
        test.ucitel = get(u for u in DbUcitel if u.login == session['ucitel'])
        test.zobrazenoOd = datum_od
        test.zobrazenoDo = datum_do
        
        #smaz puvodni otazky z testu
        select(o for o in DbOtazkaTestu if o.test.id is idTestu).delete()
        
        for idOtazky in J['otazky']:
            DbOtazkaTestu(
                poradi = 0, 
                test = get(u for u in DbTest if u.jmeno == nazev_testu),
                otazka = get(o for o in DbOtazka if o.id == idOtazky)
            )

        return 'Upraven test: ' + nazev_testu


    def pridat(J):
        nazev_testu = J['jmeno']
        datum_od = dt.strptime(J['od'], formatCasu)
        datum_do = dt.strptime(J['do'], formatCasu)

        DbTest(
            jmeno = nazev_testu,
            ucitel = get(u for u in DbUcitel if u.login == session['ucitel']),
            zobrazenoOd = datum_od,
            zobrazenoDo = datum_do
        )

        for idOtazky in J['otazky']:
            DbOtazkaTestu(
                poradi = 0, 
                test = get(u for u in DbTest if u.jmeno == nazev_testu),
                otazka = get(o for o in DbOtazka if o.id == idOtazky)
            )

        return 'Vytvořen test: ' + nazev_testu
            

    def testy():
        if request.method == 'GET':
            pritomnost = dt.strptime(
                time.strftime(formatCasu), formatCasu)
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