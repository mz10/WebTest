from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from pony.orm import (sql_debug, get, select, db_session)
import psycopg2
from datetime import datetime as dt
from .db import *

udaje = "host='localhost' user='postgres' password='a' dbname='webtest'"

from .funkce import (json, uzivatel, uzJmeno)
from .tridy import Trida

class Ostatni:
    def registrace(J):
        odpoved = ""
        
        with db_session:
            if J['typ'] == "student":
                DbStudent(
                    login = J['login'],
                    jmeno = J['jmeno'],
                    prijmeni = J['prijmeni'],
                    hash =  J['heslo'],
                    trida = get(t for t in DbTridy if t.id == J['trida'])
                )

                odpoved = "Nový student byl přidán"

            elif J['typ'] == "ucitel":
                DbUcitel(
                    login = J['login'],
                    jmeno = J['jmeno'],
                    prijmeni = J['prijmeni'],
                    hash =  J['heslo'],
                    admin = J['admin']
                )

                odpoved = "Nový učitel byl přidán"
            
            return json({"odpoved": odpoved})

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