from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from markdown import markdown
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt

from .db import *

import psycopg2
import time
import os
import functools
import random
import sys
import re

from .funkce import (json)

class Slovnik:
    def pridat(J):
        DbSlovnik(
            slovo1 = J["slovo1"],
            slovo2 = J["slovo2"],
            kategorie = J["kategorie"],           
            jazyk = J["jazyk"]
        )
        
        return

    def nahrat(J):
        text = J["data"].split("\n")
        for radek in text:
            bunka = radek.split(";")       
            if len(bunka) < 4: continue
            
            DbSlovnik(
                slovo1 = bunka[0],
                slovo2 = bunka[1],
                kategorie = bunka[2],         
                jazyk = bunka[3]
            )            
        return "CSV soubor byl úspěšně nahrán"


    def stahnout():
        slovnik = select((s.slovo1, s.slovo2, s.kategorie, s.jazyk) for s in DbSlovnik).order_by(3)
        #utf-8 hlavnicka, aby csv sel spravne zobrazit v Excelu
        csv = '\ufeff'

        for sloupec in slovnik:
            csv += sloupec[0] + ";" + sloupec[1] + ";" + sloupec[2] + ";" + sloupec[3] + "\r\n"

        r = Response(response=csv,status=200,mimetype="text/plain")
        r.headers["Content-Disposition"] = 'attachment; filename="slovnik.csv"'
        return r
        
    def zobraz():
        slovnik = select((s.id, s.slovo1, s.slovo2, s.kategorie, s.jazyk)
                    for s in DbSlovnik).order_by(3)

        seznamSlov = []
        
        for sloupec in slovnik:
            seznamSlov.append({
                "id": sloupec[0],
                "slovo1": sloupec[1],
                "slovo2": sloupec[2],
                "kategorie": sloupec[3],
                "jazyk": sloupec[4],
            })

        return json({'slovnik': seznamSlov})


    def zmenObsah(J):
        if J["tabulka"] != "Slovnik":
            return "Nemáš oprávnění měnit obsah této tabulky!!!"
        
        if J["id"] == "":
            DbSlovnik(
                slovo1 = J["bunky"][0],
                slovo2 =  J["bunky"][1],
                kategorie = J["bunky"][2],
                jazyk = J["bunky"][3],
            )

            return "Byl přidán nový záznam do tabulky."

        id = int(J["id"])

        dbId = get(o.id for o in DbSlovnik if o.id is id)

        if not dbId:
            return "Toto id neexistuje!"

        slovnik = DbSlovnik[id]

        if J["akce"] == "smazat":
            slovnik.delete()
            return "Řádek tabulky byl smazán"

        elif J["akce"] == "zmenit":
            slovnik.slovo1 = J["bunky"][0]
            slovnik.slovo2 =  J["bunky"][1]
            slovnik.kategorie = J["bunky"][2]
            slovnik.jazyk = J["bunky"][3]   
            
            return "Řádek tabulky byl změněn"