# coding: utf-8
""" DEMO - Lecture d'une base de donnée SQLite3.
 
    Affiche le contenu de la table fruits (food.db).
"""

import sqlite3 as sqlite

dbfile = "food.db"

conn = sqlite.connect( dbfile )

cursor = conn.cursor()

cursor.execute( "select * from fruits order by name")
if cursor.rowcount == 0:
	print( "Pas de données disponible" )
else:
	# Affiche le nom des colonnes
	colnames = [item[0] for item in cursor.description ]
	print( " | ".join( colnames ) )
	print( '-'*40 )
	# Fetchall() une liste de tuple
	# [(1, u'Abricot', 43), (2, u'Ananas', 55), ... ]
	for row in cursor.fetchall():
		# Afficher le données des tuples
		print( "%s | %s | %s" % (row[0], row[1], row[2]) ) 

print( "\r\r" )
# Utiliser fetchone()
cursor.execute( 
	  """select name,kcal_100gr 
	    from fruits 
	    where name like 'p%' 
	    order by id desc""" )
row = cursor.fetchone()
while row:
	# row = (u'Pomme', 52)
	print( " | ".join(
        # transforme tout en string
		["%s"%item for item in row]) 
		)
	row = cursor.fetchone()


conn.close()


if __name__ == "__main__":
	pass;
