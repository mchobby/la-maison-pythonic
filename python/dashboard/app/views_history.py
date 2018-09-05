# coding: utf8
from app import app
from flask import render_template, request, redirect, url_for, flash, abort, Response
from models import get_db, get_data_sources
import json
from datetime import datetime


""" Handle the display of VALUE'S HISTORY stored by push-to-db.py into the "ts_xxx" history tables.
	
    History can be displayed as: 
      * LIST : display a list of row in the list
      * VALUE-GRAPH : (to be implement) represent the values as a graphic (eg: temperature)

	Remarks:
	The kind of history to display for a block should be set in the block_edit.html template.
	It supposed to be an ComboBox in the final release but still communicated with an hidden field (during development stage).

    """
#-------------------------------------------------------
#  TOPIC HISTORY  
#-------------------------------------------------------
@app.route('/dashboard/<int:dash_id>/block/<int:block_id>/history/<int:_from>-<int:_len>')
@app.route('/dashboard/<int:dash_id>/block/<int:block_id>/history/<int:_from>' )
def topic_history( dash_id, block_id, _from=0, _len=None ):
	""" Display the history for a given block in the dashboad.

		Note:
		* _from=0 is equivalent of _from=None. 

		Remark:
		* The block_id allows to retreive the source and topic.
		* The source dans topic allows to retreive the topic record.
		* The topic record allows to identify the timeserie tablename
	"""
	dashdb = get_db( 'db' )
	dash   = dashdb.get_dash( dash_id )
	block  = dashdb.get_dash_block( block_id )
	topic  = block['topic']
	hist_type = block['hist_type'] 
	hist_size = _len if _len else block['hist_size']
	db_source = get_db( block['source'] )
	values    = db_source.get_values( [topic] )
	tsname    = values[0]['tsname']
	hist_rows = db_source.get_history( tsname=tsname, topic=topic, from_id = None if _from <= 1 else _from, _len=hist_size )
	# print( type(hist_rows[0]["rectime"]) )
	# print( hist_rows[0]["rectime"] )
	if hist_type=='LIST':
		return render_template( 'history/list.html', block=block, dash=dash, rows=hist_rows, _from=_from, _len=hist_size )
	else:
		flash( ('Type d''historique %s non supporté' % hist_type).decode('utf-8'), 'error' )
		return redirect( url_for('dashboard', id=dash_id) )
		