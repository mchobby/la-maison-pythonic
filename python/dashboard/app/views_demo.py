# coding: utf8
from app import app
from flask import render_template
from app import configuration # __init__.py -> configuration


@app.route('/demo')
def demo():
	app.logger.debug( 'Entering DEMO' )
	# Show a configuration 
	app.logger.debug( 'configuration.db = %s' % configuration.db )
	return render_template( 'demo/demo.html' ) 

@app.route('/demo/main')
def demo_main( ):
	app.logger.debug( 'test the main' )
	app.logger.debug( 'configuration.db = %s' % configuration.db )
	return render_template( 'demo/demo_main.html' )

@app.route('/demo/list')
def demo_list( ):
	return render_template( 'demo/demo_list.html' )

@app.route('/demo/form')
def demo_form( ):
	return render_template( 'demo/demo_form.html' )
