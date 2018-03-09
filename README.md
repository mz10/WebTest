WebTest
=========

WebTest je webové rozhraní pro testy a domácí úkoly žáků. Tento projekt se
zaměřuje hlavně na (elektro-)technické úlohy. Tento projekt nabízí:

* Zápis úloh pomocí jazyka [Markdown](https://cs.wikipedia.org/wiki/Markdown).
* Vkládání matematických vzorců 
  ala [LaTeX](https://cs.wikipedia.org/wiki/LaTeX)
  mocí knihovny [MathJax](https://cs.wikipedia.org/wiki/MathJax).
* Možnost vložit do zadání náhodné číslo a očekávaný výsledek
  zapsat jako vzorec. 


Proměnné
--------
Do editoru jdou zadávat proměnné, které můžeme použít v odpovědi jako vzorec. Proměnná musí začínat znakem $.
V odpovědi může být výraz a můžou se použít proměnné definované v zadání. Výraz musí být mezi [] :

[$a+$b+5]

Jdou také použít funkce Min, Max a Prumer:
[Prumer($a,$b,$c)]


Příklad zápisu úlohy
--------------------
Kolik je [a,20] + [b,-5,100] - [c=$b*2] ?

Jako správnou odpověď uvedeme např:
[$a + $b - $c]

Typy proměnných
---------------
* [a]		      nejjednodušší definice proměnné, studentovi se ukáže jako číslo od 0 do 1000
* [b,20] 		  číslo od 0 do 20
* [c,-20]		  záporné číslo od -20 do 0
* [d,5,100]	  číslo od 5 do 100
* [e,20,30,3]	desetinné číslo od 20 do 30, zaokrouhlené na 3 desetinná místa – např. 21.463
* [f=$a+5]    do proměnné f se přiřadí proměnná a + 5

Závislosti
-----------

* [Flask](http://flask.pocoo.org/) --- Python web framework.
* [Python-Markdown](http://pythonhosted.org/Markdown/) --- Python implementace pro
  [Markdown](http://daringfireball.net/projects/markdown/) Johnyho Grubera.
* [psycopg](http://initd.org/psycopg/) --- 
  [PostgreSQL](http://www.postgresql.org/) adaptér pro [Python](https://www.python.org/).
* [Pony](http://ponyorm.com/) ---
  [ORM](http://cs.wikipedia.org/wiki/Objektově_relační_mapování) pro [Python](https://www.python.org/).
* [Typogrify](https://github.com/mintchaos/typogrify) --- typografická vylepšení pro HTML.
* [Sympy](http://www.sympy.org/cs/) --- kalkulačka pro Python - počítá výrazy
* [SimpleMDE](https://simplemde.com/) --- editor v JS pro Markdown
    

Databáze
--------

* [ERD]() databáze: <https://editor.ponyorm.com/user/mz10/webtest3>
* Definice databázových tabulek je v modulu `db.py`.

### Přihlášení do databáze

Přihlášení se děje pomocí modulu `spojeni.py`. Soubor může vypadat takto:

    # -*- coding: utf8 -*-
    "Přihlašovací údaje k databázi."
    DB = {
        "host": "localhost",
        "user": "webtest",
        "database": "webtest",
        "password": "mojetajneheslo"
    }

Vzhled a CSS
------------

Pro tvorbu vzhledu je použit:
* [SASS](http://sass-lang.com/guide)
* [Semantic](http://semantic.gs/)
* [Compass](http://compass-style.org/)

Pomocný Skript `devtools/autoMakeF5.zsh` sleduje pomocí `inotify` adresář a pokud
se nějaký soubor změní, provede se kompilace `scss` a pomocí `xdotool`
se do prohlížeče odešle stisk F5.

devtools
-----------

V adresáři `devtools/` je několik pomocných skriptů, které mají usnadnit vývoj
a práci s lokální databází.

* `autoMakeF5.zsh`: při změně souborů automaticky odesílá 
   do prohlížeče stisk F5.
* `create-psql.usr.db`: vytvoří v PostgreSQL uživatele a založí mu 
   databázi.
* `drop-psql.usr.db`: zruší v PostgreSQL uživatele a všechny jeho 
   databáze.
* `db-insert_dev_data.py`: vloží do vývojové databáze počáteční data.
* `db-drop_create_insert.zsh`: vývojovou databázi zruší, znovu vytvoří
   a vloží do ní počáteční data.
* `devserver.zsh`: spustí vývojový server.


