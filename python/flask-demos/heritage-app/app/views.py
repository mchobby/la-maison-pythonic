# coding: utf8
from app import app
from flask import render_template

@app.route('/')
@app.route('/<string:nom>')
def main( nom = None ):
   return render_template( 'main.html', name=nom )

@app.route('/super')
def super():
   return render_template( 'super.html' )
