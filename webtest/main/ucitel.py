from flask import (Flask, render_template, Markup, request, redirect, session, flash, Markup, url_for, Response)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.routing import BaseConverter
from pony.orm import (sql_debug, get, select, db_session)
from datetime import datetime as dt
import random

from .db import *
from .funkce import (json, jsonStahnout, uzivatel, uzJmeno, seznam)
from .zadani import Zadani
from .otazka import Odpovedi

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
        if J["bunky"][4] == "true": admin = True

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

        # nove heslo:
        heslo = J["bunky"][3]
        if heslo != "." or heslo != "":
            heslo = generate_password_hash(heslo)

        if (student or ucitel):
            login = dbUcitel.login 

        if J["akce"] == "smazat":
            dbUcitel.delete()
            return "Učitel byl smazán"

        elif J["akce"] == "zmenit":
            hash = dbUcitel.hash
            heslo = J["bunky"][3]
            if heslo != "." and heslo != "":
                hash = generate_password_hash(heslo)

            dbUcitel.login = login
            dbUcitel.jmeno = J["bunky"][1]
            dbUcitel.prijmeni = J["bunky"][2]
            dbUcitel.hash = hash
            dbUcitel.admin = admin

            return "Učitel byl změněn."

        return "Chyba - záznam nebyl přidán."

    #zjednodusena verze funkce Student.vyplnitTest:
    def ukazatTest(id): 
        test = get(u for u in DbTest if u.id is id)
        otTestu = select(o for o in DbOtazkaTestu if o.test.id is id)
        seznamOtazek = [] 
        
        for otT in otTestu: 
            opakovat = 1
            if otT.pocet:
                opakovat = otT.pocet

            for i in range(0,opakovat):
                seznamOdpovedi = []
                idOtazky = otT.otazka.id 
                otazka = DbOtazka[idOtazky]
                zadani = Zadani.vytvorZadani(otazka.obecneZadani)
                odpovedi = Odpovedi(idOtazky, zadani["promenne"])

                for (odpoved, typ) in odpovedi.vypocitatVsechny():
                    if typ == "O":
                        seznamOdpovedi.append("_OTEVRENA_")
                    else:
                        seznamOdpovedi.append(odpoved)
            
                random.shuffle(seznamOdpovedi)            
                
                seznamOtazek.append({
                    'id':           0,
                    'jmeno':        otazka.jmeno,
                    'zadani':       zadani["html"],
                    'zaokrouhlit':  otazka.zaokrouhlit,
                    'tolerance':    otazka.tolerance,
                    'spravnych':    len(odpovedi.tridit("D")),
                    'odpovedi':     seznamOdpovedi
                })

        if test.nahodny:
            random.shuffle(seznamOtazek)

        # oreze seznam otazek na maximalni pocet
        if test.maxOtazek > 0:
            seznamOtazek = seznamOtazek[:test.maxOtazek]

        jsTest = {
            'id':           0,
            'do':           "limit",
            'jmeno':        test.jmeno,
            'typHodnoceni': test.typHodnoceni,
            'hodnoceni':    test.hodnoceni,
            'limit':        seznam(test.limit)[0],
            'otazky':       seznamOtazek
        }

        return json({"test": jsTest})