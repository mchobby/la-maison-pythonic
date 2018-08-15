# coding: utf-8
""" DEMO - Insertion dans une base de donnée SQLite3.
 
    Insertions d'un enregistrement dans la table fruits (food.db).
"""

import sqlite3 as sqlite

# capture un nom et un kcal/100gr
fruit_name = raw_input( "Nom fruit: ")
fruit_kcal = int( raw_input( "KCal/100gr: ") )
reponse = raw_input( 'insérer (o/...)?' )
if reponse.lower().strip() != 'o':
	import sys
	sys.exit(0)

dbfile = "food.db"

conn = sqlite.connect( dbfile )
cursor = conn.cursor()

cursor.execute( 
	"insert into fruits (name,kcal_100gr) values (?, ?)",
	(fruit_name.decode('UTF-8'), fruit_kcal)
	)
if cursor.rowcount > 0:
	print( "Enregistrement inséré" )
	print( "id = %s" % cursor.lastrowid )

conn.commit()

print( "\r\r" )
# Afficher les enregistrements
cursor.execute( "select * from fruits order by name" ) 
if cursor.rowcount > 0:
	colnames = [item[0] for item in cursor.description]
	print( " | ".join(colnames) )
for row in cursor.fetchall():
	print("|".join(["%s"%value for value in row]))

conn.close()


if __name__ == "__main__":
	pass;
