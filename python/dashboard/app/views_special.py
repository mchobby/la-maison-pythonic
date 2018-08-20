# coding: utf8
from app import app
from flask import render_template, request, redirect, url_for, flash, abort, Response
from models import get_db, get_data_sources
import json
from datetime import datetime

""" Handle the special page for dashboard having special titles like {TOPICS} """

#-------------------------------------------------------
#  SPECIAL PAGE
#-------------------------------------------------------

@app.route('/{<string:name>}', methods=['GET'] )
def special_page( name ):
	""" Affiche des dashboards spéciaux basé sur un code indiqué entre { } """
	name = name.upper()
	if name == 'TOPICS':
		db = get_db( 'db' )
		application  = db.application()
		sources = get_data_sources()
		# Get the first source
		if len( sources )==0:
			flash( "Pas de sources renseignée dans le fichier de configuration", 'error' )
			return redirect(url_for('main'))

		source_db = get_db( sources[0] )
		topic_rows = source_db.get_values( topic_list = None )
		return render_template( 'special/topic_list.html',  application=application, source=sources[0], rows=topic_rows  )
	elif name == 'DEMO':
		return render_template( 'demo/demo.html' )
	
	flash( "Pas de page speciale pour {%s}" % name )
	return redirect(url_for('main'))