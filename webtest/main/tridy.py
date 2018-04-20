from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
from .db import *
import json as _json

from .funkce import (nahodne, json, jsonStahnout, vypocitej, chyba, uzivatel, uzJmeno)
from .student import Student

class Trida:
    def pridat(J):
        DbTridy(
            poradi = int(J["poradi"]),
            nazev = J["nazev"],
            rokUkonceni = J["rok"]
        )

        return "Třída byla přidána"

    def zobrazTridy():
        seznamTrid = []
        tridy = select(t for t in DbTridy).order_by(1)

        for trida in tridy:
            seznamTrid.append(
                Trida.zobrazTridu(trida)
            )

        return json({"tridy": seznamTrid})

    def zobrazTridu(trida):
        return {
            'id':           trida.id,
            'poradi':       trida.poradi,
            'nazev':        trida.nazev,
            'rokUkonceni':  trida.rokUkonceni
        }

    def zobrazCelouTridu(id):
        trida = get(t for t in DbTridy if t.id is id)
        if not trida: return chyba("Špatné id!")

        tridaInfo = Trida.zobrazTridu(trida)
        studenti = select(s for s in DbStudent if s.trida.id is id)      
        seznamStudentu = []

        if studenti:
            for student in studenti:
                seznamStudentu.append(Student.zobrazStudenta(student))
        
        tridaInfo.update({"studenti": seznamStudentu})
        return json({"trida": tridaInfo})

    def zmenObsah(J):
        if J["tabulka"] != "Tridy" or not uzivatel("admin"):
            return "Nemáš oprávnění měnit obsah této tabulky!!!"
        
        if J["id"] == "":
            DbTridy(
                poradi = int(J["bunky"][0]),
                nazev =  J["bunky"][1],
                rokUkonceni = int(J["bunky"][2])
            )

            return "Byl přidán nový záznam do tabulky."

        id = int(J["id"])

        dbId = get(o.id for o in DbTridy if o.id is id)

        if not dbId:
            return "Toto id neexistuje!"

        tridy = DbTridy[id]

        if J["akce"] == "smazat":
            tridy.delete()
            return "Řádek tabulky byl smazán"

        elif J["akce"] == "zmenit":
            tridy.poradi = J["bunky"][0]
            tridy.nazev = J["bunky"][1]
            tridy.rok = J["bunky"][2]       
            
            return "Řádek tabulky byl změněn"