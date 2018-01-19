import random
import re
import math

text0 = """
[z,0,50]
"""


text = """
[a] --- normalni od 0 do 1000
[b,-20] --- normalni od 0 do 1000
[b,5,10] --- 0 az 50
[c,5,100,5.2] --- desetinne cislo zaokrouhleny na 5 mist
"""
promenne = []

def nahradit(m):
    try:
        rozdeleno = m.groups(0)[0].split(",")
        vysledek = "[spatne zadano]"
        
        if len(rozdeleno) == 1:
            vysledek = random.randint(0,1000)
        elif len(rozdeleno) == 2:
            od = int(rozdeleno[1])
            
            if od < 0:
                vysledek = random.randint(od,0)
            else:
                vysledek = random.randint(0,od)
        elif len(rozdeleno) == 3:
            od = int(rozdeleno[1])
            do = int(rozdeleno[2]) 
            
            if od>do:
                vysledek = random.randint(do,od)
            else:
                vysledek = random.randint(od,do)
        elif len(rozdeleno) == 4:
            od = float(rozdeleno[1])
            do =  float(rozdeleno[2])  
            zaokrouhlit = int(rozdeleno[3])
            
            if od>do:
                vysledek = random.uniform(do,od)     
            else:
                vysledek = random.uniform(od,do)
        
    except:
        promenne.append(None)
        return "[chyba ve vyrazu]" 
        
    promenne.append(vysledek)
    return str(vysledek)


n = re.compile('\[([a-z][,\-*\d+[.d+]*]*)\]').sub(nahradit,text)

print(n)
print(promenne)