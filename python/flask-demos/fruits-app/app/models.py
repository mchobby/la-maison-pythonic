# coding: utf8
from app import app
from flask import g
import sqlite3
# ----------------------------------------
# Accès à la base de donnée
# ----------------------------------------
def get_bdd():
	if not 'bdd' in g:
		g.bdd = sqlite3.connect( 'food.db' )
	return g.bdd

@app.teardown_appcontext
def teardown_app(exception):
   # Version plus récente de Flask
   #
   #_bdd = g.pop( 'bdd', None )
   #if( _bdd):
   #   _bdd.close()
   
   _bdd = g.get( 'bdd', None )
   if( _bdd):
      _bdd.close()
      del( _bdd )

# ----------------------------------------
# Utilitaires
# ----------------------------------------

def get_fruits():
	""" Obtenir la liste des fruits (id, nom, kcal_100gr) """
	cursor = get_bdd().cursor()

	cursor.execute( "select id, name, kcal_100gr from fruits order by name")
	if cursor.rowcount == 0:
		return None
	else:
		# NB: Liste des nom des colonnes
		# colnames = [item[0] for item in cursor.description ]

		# retourne une liste de tuples
		return cursor.fetchall()  

def get_fruit( id ):
	""" obtenir les informations d'un fruit donné """
	assert type(id)==int

	cursor = get_bdd().cursor()

	cursor.execute( "select id, name, kcal_100gr from fruits where id = %s" % id )
	if cursor.rowcount == 0:
		return None
	return cursor.fetchone()

def insert_fruit( name, kcal ):
	assert type(kcal)==int
	assert type(name)==unicode

	cursor = get_bdd().cursor()

	cursor.execute( 
		"insert into fruits (name,kcal_100gr) values (?, ?)",
		(name, kcal)
		)
	if cursor.rowcount > 0:
		rowid = cursor.lastrowid 
	else:
		rowid = None

	get_bdd().commit()

	return rowid

def update_fruit( id, name, kcal ):
	assert type(id)== int
	assert type(name)==unicode
	assert type(kcal)==int

	cursor = get_bdd().cursor()

	cursor.execute( 
		"update fruits set name = ?, kcal_100gr = ? where id = ?",
		(name, kcal, id)
		)

	get_bdd().commit()
	
	return cursor.rowcount > 0

def drop_fruit(id):
	assert type(id)==int

	cursor = get_bdd().cursor()

	cursor.execute( 
		"delete from fruits where id = ?",
		(id,) # tuple necessaire -> virgule
		)

	get_bdd().commit()
	
	return cursor.rowcount 