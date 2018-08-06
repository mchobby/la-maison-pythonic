# coding: utf8
from app import app
from app.models import get_fruits, get_fruit, insert_fruit, update_fruit, drop_fruit
from flask import render_template, request, abort, redirect, url_for

def safe_cast( value, totype, default=None):
	try:
		return totype( value )
	except Exception, e:
		return default

@app.route('/')
def fruit_list():
	fruits = get_fruits() 
	app.logger.debug( 'get_fruits(): %s', fruits )
	return render_template( 'fruit_list.html', rows=fruits )

@app.route('/fruit-edit/<int:id>', methods=['GET','POST'] )
@app.route('/fruit-edit/new', methods=['GET','POST'] )
def fruit_edit( id=-1 ):
	""" Edition et sauvegarde d'un fruit """
	if request.method == 'GET':
		if id == -1: # New record ?
			nom = 'Nouveau'
			kcal = 0
			title = 'Nouveau fruit'
		else:
			fruit = get_fruit( id )
			if not(fruit):
				raise Exception( 'Impossible de charger id %s' % id )
				
			nom = fruit[1]
			kcal = fruit[2]
			title = 'Modifier %s' % nom 
		return render_template( 'fruit_edit.html', id=id, nom=nom, kcal=kcal, title=title )

	else: # C'est un POST
		# recupérer les paramètres
		nom = request.form['nom']
		kcal = safe_cast( request.form['kcal'], int, 0 )
		id   = safe_cast( request.form['id'], int, None )
		if id == None:
			raise Exception( 'Malformed ID dans le POST!')

		if id == -1: # New record?
			rowid = insert_fruit( nom, kcal )
			app.logger.debug( 'Insertion fruit à id=%s', rowid)
		else: # It is an update
			update_fruit( id, nom, kcal )
		return redirect( url_for('fruit_list') )


@app.route('/fruit-delete/<int:id>')
def fruit_delete( id ):
	""" Effacer un enregistrement """
	count = drop_fruit( safe_cast(id, int) )
	app.logger.info( 'dropped %s fruit records for id=%s', count, id )
	return redirect( url_for('fruit_list') )
