WebTest
=========

WebTest je webové rozhraní pro testy a domácí úkoly žákù. Tento projekt se
zamìøuje hlavnì na (elektro-)technické úlohy. Tento projekt nabízí:

* Zápis úloh pomocí jazyka [Markdown](https://cs.wikipedia.org/wiki/Markdown).
* Vkládání matematických vzorcù 
  ala [LaTeX](https://cs.wikipedia.org/wiki/LaTeX)
  mocí knihovny [MathJax](https://cs.wikipedia.org/wiki/MathJax).
* Možnost vložit do zadání náhodné èíslo a oèekávaný výsledek
  zapsat jako vzorec. 


Promìnné
--------
Do editoru jdou zadávat promìnné, které mùžeme použít v odpovìdi jako vzorec. Promìnná musí zaèínat znakem $.
V odpovìdi mùže být výraz a mùžou se použít promìnné definované v zadání. Výraz musí být mezi [] :

[$a+$b+5]

Jdou také použít funkce Min, Max a Prumer a funkce z knihovny Sympy:
[Prumer($a,$b,$c)]


Pøíklad zápisu úlohy
--------------------
Kolik je [a,20] + [b,-5,100] - [c=$b*2] ?

Jako správnou odpovìï uvedeme napø:
[$a + $b - $c]

Náhodná èísla
---------------
* [a,20] 		  èíslo od 0 do 20
* [b,-20]		  záporné èíslo od -20 do 0
* [c,5,100]	  èíslo od 5 do 100
* [d,2000,5000,2]	desetinné èíslo od 20 do 30, zaokrouhlené na 2  platná místa – napø. 2500
* [e=$a+5]    	do promìnné e se pøiøadí promìnná a + 5

Závislosti
-----------

* [Flask](http://flask.pocoo.org/) --- Python web framework.
* [Python-Markdown](http://pythonhosted.org/Markdown/) --- Python implementace pro
  [Markdown](http://daringfireball.net/projects/markdown/) Johnyho Grubera.
* [psycopg](http://initd.org/psycopg/) --- 
  [PostgreSQL](http://www.postgresql.org/) adaptér pro [Python](https://www.python.org/).
* [Pony](http://ponyorm.com/) ---
  [ORM](http://cs.wikipedia.org/wiki/Objektovì_relaèní_mapování) pro [Python](https://www.python.org/).
* [Sympy](http://www.sympy.org/cs/) --- kalkulaèka pro Python - poèítá výrazy
* [SimpleMDE](https://simplemde.com/) --- editor v JS pro Markdown
    

Databáze
--------

* [ERD]() databáze: <https://editor.ponyorm.com/user/mz10/webtest/>
* Definice databázových tabulek je v modulu `db.py`.

### Pøihlášení do databáze

Pøihlášení se dìje pomocí modulu `spojeni.py`. Soubor mùže vypadat takto:

    # -*- coding: utf8 -*-
    "Pøihlašovací údaje k databázi."
    DB = {
        "host": "localhost",
        "user": "webtest",
        "database": "webtest",
        "password": "mojetajneheslo"
    }

V adresáøi `devtools/` je nìkolik pomocných skriptù, které mají usnadnit vývoj
a práci s lokální databází.

* `autoMakeF5.zsh`: pøi zmìnì souborù automaticky odesílá 
   do prohlížeèe stisk F5.
* `create-psql.usr.db`: vytvoøí v PostgreSQL uživatele a založí mu 
   databázi.
* `drop-psql.usr.db`: zruší v PostgreSQL uživatele a všechny jeho 
   databáze.
* `db-insert_dev_data.py`: vloží do vývojové databáze poèáteèní data.
* `db-drop_create_insert.zsh`: vývojovou databázi zruší, znovu vytvoøí
   a vloží do ní poèáteèní data.
* `devserver.zsh`: spustí vývojový server.


