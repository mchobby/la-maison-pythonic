# coding: utf8
from app import app
from flask import render_template

@app.route('/')
@app.route('/<string:nom>')
def demovar( nom = None ):
   items = ['banane', 'orange', 'pomme', 'poire']
   return render_template( 'demovar.html', name=nom, elements=items )

