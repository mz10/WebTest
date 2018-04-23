from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.routing import BaseConverter
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt

from .db import *

from .funkce import (json, jsonStahnout, uzivatel, uzJmeno)

class Ucitel:
    def seznamUcitelu():
        ucitele = select(s for s in DbUcitel).sort_by("s.id")
        seznam = []

        for ucitel in ucitele:
            seznam.append({
                "id":       ucitel.id,
                "login":    ucitel.login,
                "jmeno":    ucitel.jmeno,
                "prijmeni": ucitel.prijmeni,
                "admin":    ucitel.admin
            })
            
        return json({"ucitele": seznam})

    def zmenObsah(J):
        if J["tabulka"] != "Ucitel" or not uzivatel("admin"):
            return "Nemáš oprávnění měnit obsah této tabulky!!!"
        
        admin = False
        if J["bunky"][3] == "true": admin = True

        # zkontroluje, jestli uz v tabulkach neni stejny login
        login = J["bunky"][0]
        ucitel = get(s.id for s in DbUcitel if s.login == login)
        student = get(s.id for s in DbStudent if s.login == login)

        if J["id"] == "":
            if (student or ucitel):
                return "Tento login už existuje!"

            DbUcitel(
                login = login,
                jmeno =  J["bunky"][1],
                prijmeni = J["bunky"][2],
                admin = admin
            )

            return "Byl přidán nový učitel."

        id = int(J["id"])

        dbId = get(o.id for o in DbUcitel if o.id is id)

        if not dbId:
            return "Toto id neexistuje!"

        dbUcitel = DbUcitel[id]

        if (student or ucitel):
            login = dbUcitel.login 

        if J["akce"] == "smazat":
            dbUcitel.delete()
            return "Učitel byl smazán"

        elif J["akce"] == "zmenit":
            dbUcitel.login = login
            dbUcitel.jmeno = J["bunky"][1]
            dbUcitel.prijmeni = J["bunky"][2]
            dbUcitel.admin = admin

            return "Učitel byl změněn."

        return "Chyba - záznam nebyl přidán."