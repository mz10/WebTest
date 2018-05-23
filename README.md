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

Příklad zápisu úlohy
--------------------
Kolik je [$a,20] + [$b,-5,100] - [$c=$b*2] ?

Jako správnou odpověď uvedeme např:
[$a + $b - $c]

Náhodná čísla
---------------
* [$a,20] 			číslo od 0 do 20
* [$b,-20]			záporné číslo od -20 do 0
* [$c,5,100]		číslo od 5 do 100
* [$d,2000,5000,2]		číslo od 2000 do 30000, zaokrouhlené na 2  platná místa – např. 2500
* [$e=$a+5] 		do proměnné e se přiřadí proměnná a + 5

Funkce, které se dají zadávat do odpovědi a do editoru:

Matematické funkce
---------------
Příklady zápisu:
[$a=Abs(-5)]		Absolutní hodnota -> 5
[$a=Prumer(1,2,3,4)]	Průměr -> 2,5
[$a=Jednotka(0.05,mV)]	Převede na správnou jednotku -> 50 µuV
[$a=Max(1,4,3,2)]		Maximum nebo minimum -> 4 nebo 1

Komplexní čísla
---------------
[(-3-I)/(1+I)]		-2 + 1*I
[I**3+I**6+I**9]		-1

Základní funkce
---------------
Příklady zápisu a výsledek:
[Prumer(1,2,3,4]        		Průměr -> 2.5
[Max(2,45,4,8,7]        		Maximum nebo minimum -> 45 nebo 2
[Jednotka(51234,µV)]            	Zobrazí číslo ve správné jednotce -> 51.234 mV
[sin(3)]           		Sinus -> 0.1411
[simplify(sin(3)*2)]        	Vypočítá výraz -> 0.2822
[simplify(pi)]            		Konstanta pí    -> 3.14159
[Abs(-5)]            		Absolutní hodnota -> 5
[R(3/9)]            		Vytvoří zlomek -> 1/3

Další funkce
---------------
Derivace:			[diff(sin(x), x)]
Integrál:			[integrate(x**2 * cos(x), x)]
Limit:			[limit((sin(x)-x)/x**3, x, 0)]

Rovnice
--------
Příklad zápisu - výraz musí být mezi $$ $$, editor umí zobrazí náhled
$$x = {[$a,20]  \over x} +  {[$a,20]  \over 5} - \sqrt{{x}  \over [$a,20]} $$

Závislosti
-----------
* [Flask](http://flask.pocoo.org/) - Python web framework.
* [Python-Markdown](http://pythonhosted.org/Markdown/) - Python implementace pro
  [Markdown](http://daringfireball.net/projects/markdown/) Johnyho Grubera.
* [psycopg](http://initd.org/psycopg/) -
  [PostgreSQL](http://www.postgresql.org/) adaptér pro [Python](https://www.python.org/).
* [Pony](http://ponyorm.com/) -
  [ORM](http://cs.wikipedia.org/wiki/Objektově_relační_mapování) pro [Python](https://www.python.org/).
* [Sympy](http://www.sympy.org/cs/) --- kalkulačka pro Python - počítá výrazy
* [SocketIO](http://flask-socketio.readthedocs.io/en/latest/) - Websockety - flask
* [LDAP3](http://ldap3.readthedocs.io/) - LDAP - vzdálené přihlašování
* [SimpleMDE](https://simplemde.com/) --- editor v JS pro Markdown
    

Databáze
--------
* [ERD]() databáze: <https://editor.ponyorm.com/user/mz10/webtest>
* Definice databázových tabulek je v modulu `db.py`.

### Přihlášení do databáze

Přihlášení se děje pomocí modulu `spojeni.py`. Soubor může vypadat takto:

    "Přihlašovací údaje k databázi."
    DB = {
        "host": "localhost",
        "user": "webtest",
        "database": "webtest",
        "password": "tajneheslo"
    }

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


