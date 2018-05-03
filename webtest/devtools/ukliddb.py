# Author:  mz10
# Licence: GNU/GPL 
# Task:    smazání celé databáze
############################################################
import psycopg2
 
udaje = {
    "host": "localhost",
    "user": "postgres",
    "database": "webtest",
    "password": "a"
}

db = psycopg2.connect(**udaje)
sql = db.cursor()
db.autocommit = True

info = "Vsechny tyto tabulky byly smazany:\n"

#smazat tabulku:
sql.execute("select * from pg_tables where schemaname = 'public';");   
for radek in sql.fetchall():
    info += radek[1] + "\n"
    sql.execute('DROP TABLE "' + radek[1] + '" CASCADE;')

print(info)

sql.close()
db.close()