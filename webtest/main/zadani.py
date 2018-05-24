from markdown import markdown
import re
from pony.orm import (sql_debug, get, select, db_session)
from .db import *
import random

from .funkce import (nahodne, nahodneDes, jednotka, 
    jednotka2, rovnice, spVypocitat, prumer, zaokrouhlit, platneMista, seznam)

import sympy
sympy.init_printing()

class Zadani:   
    promenne = {}

    def vytvorZadani(zadani):
        # smazat vsechny promenne z predchozi otazky
        Zadani.promenne = {}
        
        m = zadani

        #vybere cizí slovo ze slovniku
        m = re.compile("\$slovo[1-9]\.\w+.\w+", re.UNICODE).sub(Zadani.nahraditSlova,m)

        #nahradi textove promenne v [] nahodnymi cisly
        # příklad: [Proměnná123,10,20]     
        m = re.compile('\[\$([A-ž]+[\d+]*,.*?)\]').sub(Zadani.nahodnePromenne,m)
        
        #nahradi textove promenne vypocitanym vyrazem
        m = re.compile('\[\$([A-ž]+[\d+]*)[ ]*\=[ ]*(.*?)\]').sub(Zadani.vypocitatPromenne,m)
        
        # vyhodnoti funkce
        m = re.compile('\[([A-ž]+[\d+]*)\((.*?)\)\]').sub(Zadani.vyhodnotitFunkce,m)

        #nahradi textove promenne vypocitanym vyrazem
        m = re.compile('\[\$([A-ž]+[\d+]*)[ ]*\=[ ]*(.*?)\]').sub(Zadani.vypocitatPromenne,m)

        #dosadi vsechny ostatni promenne v []
        m = re.compile('\[(.*?)\]').sub(Zadani.dosaditPromenne,m)
              
        #vyhleda a odstrani komentare /** komentar **/
        m = re.compile(r"\/\*\*(.*?)\*\*\/?",re.DOTALL).sub("",m)
        
        #prevede markdown do HTML a nahradi novy radek
        m = markdown(m).replace("\n","<br>")

        hotovo = {}
        hotovo["promenne"] = Zadani.promenne
        hotovo["html"] = m

        return hotovo

    def vytvorOdpovedi(odpoved,promenne):
        Zadani.promenne = promenne
        m = odpoved

        # nahodna cisla 
        m = re.compile('\[\$([A-ž]+[\d+]*,.*?)\]').sub(Zadani.nahodnePromenne,m)

        #vyhleda překlad cizího slova z databáze
        m = re.compile("\$slovo[1-9]\.\w+.\w+").sub(Zadani.odpovediSlPromenne,m)

        #nahradi vsechny promenne v []
        m = re.compile('\[(.*?)\]').sub(Zadani.odpovediPromenne,m)

        # vyhodnoti funkce
        m = re.compile('\[([A-ž]+[\d+]*)\((.*?)\)\]').sub(Zadani.vyhodnotitFunkce,m)

        # odstrani [] pokud vyraz obsahuje
        m = m.replace("[","").replace("]","")

        return str(m)

    def nahraditSlova(m):
        promenne = Zadani.promenne

        vyraz = m.group(0).split(".")
        slovo = vyraz[0]
        jazyk = vyraz[1]
        kategorie = vyraz[2]
        vsechno = True if kategorie == "vsechno" else False

        slova = select((s.slovo1, s.slovo2) 
            for s in DbSlovnik if (s.kategorie is kategorie or vsechno) and s.jazyk is jazyk)
        seznamSlov = seznam(slova)

        random.shuffle(seznamSlov)

        if len(seznamSlov) == 0:
            return "[spatne zadano 1]"

        spravne1 = seznamSlov[0][0]
        spravne2 = seznamSlov[0][1]

        promenne["slovo1.spravne"] = spravne1
        promenne["slovo2.spravne"] = spravne2

        #odebere spravne slova ze seznamu a zustanou jen spatne
        seznamSlov.pop(0)
        
        promenne["slovo1.spatne"] = []
        promenne["slovo2.spatne"] = []      

        for sl in seznamSlov:
            promenne["slovo1.spatne"].append(sl[0])
            promenne["slovo2.spatne"].append(sl[1])

        if slovo == "$slovo1":
            return spravne1
        elif slovo == "$slovo2":
            return spravne2

        return str(slovo)

    def nahodnePromenne(m):
        promenne = Zadani.promenne

        rozdeleno = m.groups(0)[0].split(",")
        promenna = rozdeleno[0]

        print("roz: " + str(m.group(0)))
        
        #overi jestli promenna uz existuje
        #pokud jo, tak ji nahradi stejnou (predchozi) hodnotou   
        if promenna in promenne:
            return str(promenne[promenna])

        try:
            vysledek = "[spatne zadano 2]"
            
            # pokud najde jen - nenahrazuje
            if len(rozdeleno) == 1:
                return str("a")
            #[$pr,10] - napr od 0 do 10 
            elif len(rozdeleno) == 2:
                od = int(rozdeleno[1])
                
                if od < 0:  vysledek = nahodne(od,0)
                else:       vysledek = nahodne(0,od)
            #[$pr,20,30] - napr od 20 do 30        
            elif len(rozdeleno) == 3:
                od = int(rozdeleno[1])
                do = int(rozdeleno[2]) 
                
                if          od>do: vysledek = nahodne(do,od)
                else:       vysledek = nahodne(od,do)
            #[$pr,20,30,5] - stejne jak nahore, ale + 5 desetinych mist    
            elif len(rozdeleno) == 4:
                od = float(rozdeleno[1])
                do =  float(rozdeleno[2])  
                mista = int(rozdeleno[3])
                
                if od>do:   vysledek = nahodneDes(do,od)     
                else:       vysledek = nahodneDes(od,do)
                
                vysledek = platneMista(vysledek,mista)

        except Exception as e:
            promenne[promenna] = 0
            return "[chyba ve výrazu 1]" # + str(e)
            #return str(e)

        vysledek = str(vysledek)

        promenne[promenna] = vysledek
        return vysledek

    def vypocitatPromenne(m):
        promenne = Zadani.promenne

        promenna = m.group(1)
        vyraz = m.group(2)
        
        # testuje jestli je vyraz funkce a pokud ano, vyhodnoti se
        vyraz = re.compile('([A-ž]+[\d+]*)\((.*?)\)').sub(Zadani.vyhodnotitFunkce,vyraz)
        
        #dosadit promenne do vyrazu
        for p, hodnota in sorted(promenne.items()):
            vyraz = vyraz.replace("$" + p,str(hodnota))
    
        #zkusi vypocitat vyraz 
        try: vysledek = spVypocitat(vyraz)
        except Exception as e: vysledek = vyraz
        
        #pridat vysledek do seznamu promennych
        promenne[promenna] = vysledek
        return vysledek

    def vyhodnotitFunkce(m):
        promenne = Zadani.promenne

        funkce = m.group(1).lower()
        
        # dosadi promenne do argumentu a rozdeli je
        argumenty = re.compile('(.*)').sub(Zadani.dosaditPromenne, m.group(2))  
        argumenty = argumenty.split(",")
        delka = len(argumenty)

        # dosadi promenne do vyrazu        
        vyraz = re.compile('(.*)').sub(Zadani.dosaditPromenne, m.group(0))
        
        vysledek = ""

        try:
            if funkce == "prumer":
                vysledek = prumer(argumenty)
            elif funkce == "zk" and delka == 2:
                vysledek = zaokrouhlit(*argumenty)  
            elif funkce == "pmista" and delka == 2:
                vysledek = platneMista(*argumenty)
            elif funkce == "jednotka" and delka >= 2:
                vysledek = jednotka(*argumenty) 
            elif funkce == "jednotka2":
                vysledek = jednotka2(*argumenty)                           
            elif funkce == "r":
                vysledek = rovnice(argumenty)                              
            elif vyraz[0] == "[":
                return spVypocitat(vyraz[1:-1])
            else:
                return spVypocitat(vyraz)  
        
            return str(vysledek)
        except Exception as e:
            return "[chyba ve výrazu 3: " + str(e) + "]"

    def dosaditPromenne(m):
        promenne = Zadani.promenne      
        vyraz = m.group(1)  
        
        #dosadit promenne do vyrazu
        for p, hodnota in sorted(promenne.items()):
            vyraz = vyraz.replace("$" + p,str(hodnota)) 
         
        # zkontrolovat jestli se vyraz zmenil
        if vyraz == m.group(1): return m.group(0)
        else: return vyraz

    def odpovediPromenne(m):
        promenne = Zadani.promenne       
        vyraz = m.group()
        try: vyraz = m.group(1)
        except: True

        #nahradi promenne ze zadani a dosadi jeji hodnotou
        for promenna, hodnota in sorted(promenne.items()): 
            if type(hodnota) is list: continue         
            vyraz = vyraz.replace("$" + promenna, hodnota)

        # zkusi vypocitat vyraz:
        try: vyraz = spVypocitat(vyraz)
        except: True

        return "[" + str(vyraz) + "]"

    def odpovediSlPromenne(m):
        promenne = Zadani.promenne       
        vyraz = m.group()

        try: vyraz = m.group(1)
        except: True

        #nahradi promenne ze zadani a dosadi jeji hodnotou
        for promenna, hodnota in sorted(promenne.items()):
            # pokud promenna obsahuje seznam (slov)
            if type(hodnota) is list:
                if len(hodnota) >= 1:
                    hodnota = hodnota[0]
                    # odebere pridane slovo ze seznamu
                    promenne[promenna].pop(0)
                else:
                    hodnota = "{Chyba: málo slov v DB}"
            
            vyraz = vyraz.replace("$" + promenna, hodnota)

        return str(vyraz)        