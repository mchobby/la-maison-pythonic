# coding: utf8
from app import app
from flask import render_template, g, session, make_response
import jinja2

app.config['SECRET_KEY'] = 'la-cle-secrete'

@app.route('/<path:path>' )
@app.route('/', defaults={'path':''})
def demovar( path = None ):
   items = ['banane', 'orange', 'pomme', 'poire']
   g.db = 'connexion_db'
   g.magic_key = 12345

   session['user_id'] = 45
   session['user_name'] = 'Meurisse'
   session['user_first'] = 'Dominique'
   session['user_login'] = 'domdom'

   # Initialise un cookie dans la réponse
   resp = make_response( render_template( 'specialvar.html', elements=items ) )
   resp.set_cookie( 'projet', 'la-maison-pythonic' )
   return resp

