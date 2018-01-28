from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from typogrify.filters import typogrify
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from webtest.db import *
import time
import os
import functools

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