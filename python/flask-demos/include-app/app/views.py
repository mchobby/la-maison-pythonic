# coding: utf8
from app import app
from flask import render_template

@app.route('/')
def page_pincipale( ):
   return render_template( 'main.html', titre='Bienvenu sur la page principale' )

