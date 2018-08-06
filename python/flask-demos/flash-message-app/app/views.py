# coding: utf8
from app import app
from flask import render_template, request, redirect, url_for, flash

app.secret_key = 'la_cle_secrete'

@app.route('/')
def main( nom = None ):
   return render_template( 'main.html' )

@app.route('/edit/name')
def edit_name():
   return render_template( 'edit_nom.html' )

@app.route('/save/name', methods=['POST'] )
def save_name():
	if request.form['act'] == 'Abandonner':
		flash( u'Opération abandonnée', 'error' )
	else:	
		# Sauvegarder les données

		flash( u'Nom "%s" enregistré' % request.form['name'] )

	return redirect( url_for( 'main' ) )

@app.route('/edit/message')
def edit_message():
   return render_template( 'edit_message.html' )

@app.route('/save/message', methods=['POST'] )
def save_message():
	if request.form['act'] == 'Abandonner':
		flash( u'Opération abandonnée', 'error' )
	else: # soit 'Envoyer+Saisir Nom', soit 'Envoyer'

		# Sauvegarder les données
		for err,msg in [ ('error1','message1'), ('error2','message2') , ('error3','message3') ]:
			flash_type = 'error' if err in request.form else 'message'
			msg_content = request.form[ msg ] if msg in request.form else None
			if msg_content:
				flash( msg_content, flash_type )

	if request.form['act'] == u'Envoyer+Saisir Nom':
		return redirect( url_for( 'edit_name' ) )
	else:
		return redirect( url_for( 'main' ) )