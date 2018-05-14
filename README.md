WebTest
=========

WebTest je webov� rozhran� pro testy a dom�c� �koly ��k�. Tento projekt se
zam��uje hlavn� na (elektro-)technick� �lohy. Tento projekt nab�z�:

* Z�pis �loh pomoc� jazyka [Markdown](https://cs.wikipedia.org/wiki/Markdown).
* Vkl�d�n� matematick�ch vzorc� 
  ala [LaTeX](https://cs.wikipedia.org/wiki/LaTeX)
  moc� knihovny [MathJax](https://cs.wikipedia.org/wiki/MathJax).
* Mo�nost vlo�it do zad�n� n�hodn� ��slo a o�ek�van� v�sledek
  zapsat jako vzorec. 


Prom�nn�
--------
Do editoru jdou zad�vat prom�nn�, kter� m��eme pou��t v odpov�di jako vzorec. Prom�nn� mus� za��nat znakem $.
V odpov�di m��e b�t v�raz a m��ou se pou��t prom�nn� definovan� v zad�n�. V�raz mus� b�t mezi [] :

[$a+$b+5]

Jdou tak� pou��t funkce Min, Max a Prumer a funkce z knihovny Sympy:
[Prumer($a,$b,$c)]


P��klad z�pisu �lohy
--------------------
Kolik je [a,20] + [b,-5,100] - [c=$b*2] ?

Jako spr�vnou odpov�� uvedeme nap�:
[$a + $b - $c]

N�hodn� ��sla
---------------
* [a,20] 		  ��slo od 0 do 20
* [b,-20]		  z�porn� ��slo od -20 do 0
* [c,5,100]	  ��slo od 5 do 100
* [d,2000,5000,2]	desetinn� ��slo od 20 do 30, zaokrouhlen� na 2  platn� m�sta � nap�. 2500
* [e=$a+5]    	do prom�nn� e se p�i�ad� prom�nn� a + 5

Z�vislosti
-----------

* [Flask](http://flask.pocoo.org/) --- Python web framework.
* [Python-Markdown](http://pythonhosted.org/Markdown/) --- Python implementace pro
  [Markdown](http://daringfireball.net/projects/markdown/) Johnyho Grubera.
* [psycopg](http://initd.org/psycopg/) --- 
  [PostgreSQL](http://www.postgresql.org/) adapt�r pro [Python](https://www.python.org/).
* [Pony](http://ponyorm.com/) ---
  [ORM](http://cs.wikipedia.org/wiki/Objektov�_rela�n�_mapov�n�) pro [Python](https://www.python.org/).
* [Sympy](http://www.sympy.org/cs/) --- kalkula�ka pro Python - po��t� v�razy
* [SimpleMDE](https://simplemde.com/) --- editor v JS pro Markdown
    

Datab�ze
--------

* [ERD]() datab�ze: <https://editor.ponyorm.com/user/mz10/webtest/>
* Definice datab�zov�ch tabulek je v modulu `db.py`.

### P�ihl�en� do datab�ze

P�ihl�en� se d�je pomoc� modulu `spojeni.py`. Soubor m��e vypadat takto:

    # -*- coding: utf8 -*-
    "P�ihla�ovac� �daje k datab�zi."
    DB = {
        "host": "localhost",
        "user": "webtest",
        "database": "webtest",
        "password": "mojetajneheslo"
    }

V adres��i `devtools/` je n�kolik pomocn�ch skript�, kter� maj� usnadnit v�voj
a pr�ci s lok�ln� datab�z�.

* `autoMakeF5.zsh`: p�i zm�n� soubor� automaticky odes�l� 
   do prohl�e�e stisk F5.
* `create-psql.usr.db`: vytvo�� v PostgreSQL u�ivatele a zalo�� mu 
   datab�zi.
* `drop-psql.usr.db`: zru�� v PostgreSQL u�ivatele a v�echny jeho 
   datab�ze.
* `db-insert_dev_data.py`: vlo�� do v�vojov� datab�ze po��te�n� data.
* `db-drop_create_insert.zsh`: v�vojovou datab�zi zru��, znovu vytvo��
   a vlo�� do n� po��te�n� data.
* `devserver.zsh`: spust� v�vojov� server.


