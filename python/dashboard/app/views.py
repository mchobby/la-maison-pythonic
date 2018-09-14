# coding: utf8
from app import configuration
from app import app
from flask import render_template, request, redirect, url_for, flash, abort, Response, jsonify, make_response
from models import get_db, get_data_sources, get_mqtt_sources
import json
from datetime import datetime

@app.template_filter('strftime')
def strftime_filter(value, format='hour', source_type='datetime'):
	""" Jinja filter working as the python datetime.strptime() """
	# check input format and convert it
	if source_type=='datetime':
		if type(value)!=datetime:
			return "(value is not a datetime!)"
	elif source_type=='sqlite_dt': # Sqlite default datetime format
		if type(value)!=unicode:
			return "(value is not unicode!)"
		# Sqlite store time with '%Y-%m-%d %H:%M:%S.%f' format. So convert back to datetime format
		try: 
			value = datetime.strptime( value , '%Y-%m-%d %H:%M:%S.%f' )
		except:
			return "(%s invalid format!)" % value

	if format == 'hour':
		_format="%H:%M"
	elif format == 'full':
		_format="%d/%m/%Y %H:%M:%S"
	elif format == 'elapse':
		sec = (datetime.now()-value).seconds
		min = sec / 60
		sec = sec % 60
		hour = min / 60
		min = min % 60
		day = (datetime.now()-value).days
		month = day / 30
		day = day % 30
		if (min>0) or (hour>0) or (day>0):
			_lst = []
			if month>0:
				_lst.append( "%s mois" % month )
			if day>0:
				_lst.append( "%s jour%s" % (day, ("s" if day>0 else "")) )
			if hour>0:
				_lst.append( "%s heure%s" % (hour, ("s" if hour>0 else "")) )
			if min>0:
				_lst.append( "%s minute%s" % (min, ("s" if min>0 else "")) )

			return ", ".join( _lst ) 
		else:
			return '%s secondes' % sec
	else:
		_format = format

	try:
		return value.strftime(_format)
	except Exception as err:
		app.logger.error( "format_strftime: unable to convert datetime %s with format %s due following error" % (value, format) )
		app.logger.exception( err )
		return "(strftime formatting error!)"

@app.template_filter('special_page')
def special_page_filter(value):
	""" Jinja filter that extract the name of a special page name from a dashboad title 

	     {topics} --> TOPICS """
	if ( value.find('{')>=0 ) and ( value.find('}')>=0 ):
		return value[ value.find('{')+1 : value.find('}') ].upper()
	else:
		return None

def safe_cast( value, totype, default=None):
	try:
		return totype( value )
	except Exception, e:
		return default

#-------------------------------------------------------
#  DASHBOARD LIST
#-------------------------------------------------------

@app.route('/')
def main():
	""" List available Dashboard """
	dashdb = get_db( 'db' )
	# List of dashboard
	rows = dashdb.dashes()
	# Info about application name
	application = dashdb.application() 

	return render_template( 'dash_list.html', dash_list=rows, application=application )


@app.route('/dashboard/add', methods=['GET','POST'] )
@app.route('/dashboard/edit/<int:id>', methods=['GET','POST'] )
def dashboard_add( id=None ):
	application = get_db('db').application() 
	if request.method == 'GET':
		# --- GET ----------------------------------------------------
		if id == None:
			empty_row = get_db('db').empty_dash()
			return render_template( 'dash_edit.html', row=empty_row, application=application  )
		else:
			row = get_db('db').get_dash( id )
			return render_template( 'dash_edit.html', row=row, application=application  )
	else:
		# --- POST ---------------------------------------------------
		if( request.form['action'] == u'cancel' ):
			# Abandon
			return redirect(url_for('main'))

		# Extract data (ready to save)
		#   request.form is already in unicode
		data = { 
		  'id' : (None if request.form['id'] == '' else int( request.form['id'] ) ),
		  'label' :  ('Indéfini'.decode('utf8') if request.form['label'] == '' else request.form['label'] ), 
		  'color' : (application['color'].decode('utf8') if not('color' in request.form) or (request.form['color']==u'') else request.form['color'] ),
		  'color_text' : ('black'.decode('utf8') if not('colortext' in request.form) or (request.form['colortext']==u'') else request.form['colortext'] ),
		  'icon' : (None if not('icon' in request.form) or (request.form['icon']==u'') else request.form['icon'] )
		}
		app.logger.debug( 'saving dash %s', data )
		get_db('db').save_dash( **data )
		flash( u'%s modifié' % data['label'] )
		return redirect( url_for('main') ) 

@app.route('/dashboard/<int:id>/delete', methods=['GET','POST'])
def dashboard_delete( id ):
	""" Drop a given Dashboard """
	application = get_db('db').application() 
	if request.method == 'GET':
		# --- GET ----------------------------------------------------
		row = get_db('db').get_dash( id )
		return render_template( 'dash_del_confirm.html', row=row, application=application)
	else:
		# --- POST --------------------------------------------------
		app.logger.debug( "Deleted dash")
		if request.form['action'] == u'cancel':
			return redirect( url_for('main') )
		else:
			flash( u'Dashboard %s effacé!' %  get_db('db').get_dash( id )['label'] )
			get_db('db').drop_dash( id )
			return redirect( url_for( 'main') )

#-------------------------------------------------------
#  DASHBOARD DISPLAY
#-------------------------------------------------------

@app.route('/dashboard/<int:id>')
def dashboard( id ):
	""" View the Dashboard """

	def distinct( lst ):
		""" return distinct values in the list """
		r = []
		for item in lst:
			if item in r:
				continue
			r.append( item )
		return r

	class BlockWithData( object ):
		""" carry block info (row) and block_data info (dict) """
		block = None
		block_data = None
		block_config = None # Block_config JSON string as Python structure

		def __init__( self, block, block_data, block_config ):
			self.block = block
			self.block_data = block_data
			self.block_config = block_config 

		def __repr__( self ):
			return '<block: %r, block_data: %r, block_config: %s>' % (self.block, self.block_data, self.block_config)

	db = get_db('db')	
	application = db.application()
	dashboard   = db.get_dash( id )
	block_list  = db.get_dash_blocks( id )
	mqtt_sources= get_mqtt_sources( as_dict = True )

	# === Retreive the data for the blocks ====================================
	_source_topics  = [ (block['id'], block['source'], block['topic']) for block in block_list ]
	# will be a dictionnary of {'id':<block_id>, 'block_data':<block_data>}.  
	# A <bloc_data> is a dictionnary of { 'id':<block_id>, 'topic': <topic_name>, 'value':<data_value>, 'history':<tsname> }
	_block_data  = {}
	# For each source (collect all topics at once)
	for source in distinct( [ itm[1] for itm in _source_topics ] ):
		# collect the list of topics for the source
		# app.logger.debug( _source_topics )
		_topics = []
		for id, source, topic in [ _source_topic for _source_topic in _source_topics if _source_topic[1] == source ]:
			_topics.append( topic )
		# app.logger.debug( _topics )
		# Request the corresponding data
		source_db = get_db( source )
		_rows = source_db.get_values( _topics ) # return rows: topic, value, tsname
		for _row in _rows:
			block_ids = [ source_topic[0] for source_topic in _source_topics if source_topic[2] == _row['topic'] ]
			for block_id in block_ids:
				_block_data[block_id] = {'id': block_id,
					'topic':_row['topic'], 
					'value':_row['message'], 
					'history':_row['tsname'],
					'rectime': db.str_to_datetime( _row['rectime'] ),
					'tsname' :_row['tsname'] } 
	#DEBUG: app.logger.debug( 'block_data %s' % _block_data )

	# Adding the data INSIDE each block_list's row
	block_with_data_list = []
	for row in block_list:
		try:
			_block_config = {} if row['block_config']==None or len( row['block_config'] )==0 else json.loads( row['block_config'] )
		except Exception as err:
			app.logger.error( 'Failed to convert JSON block_config for block %s to Python structure.' % row['id'] ) 
			app.logger.error( 'due to error %s on %s' % (err,row['block_config']) ) 
			_block_config = { '_error' : ['unable to convert json block_config for block %s to python structure'% row[id],
			                              'due to error %s on %s' % (err,row['block_config']) ] 
			                }
		block_with_data_list.append( BlockWithData( block=row, block_data=_block_data[row['id']], block_config=_block_config ) )
		#except:
		#	setattr( row, 'block_data', None ))

	# === render the Dashboard ===============================================
	return render_template( 'dashboard.html', 
		block_with_data_list = block_with_data_list, 
		dashboard  = dashboard, 
		application= application,
		configuration=configuration,
		mqtt_sources=mqtt_sources )

#-------------------------------------------------------
#  BLOCK LIST
#-------------------------------------------------------

@app.route('/dashboard/<int:dash_id>/block/add', methods=['GET', 'POST'])
@app.route('/dashboard/<int:dash_id>/block/<int:block_id>/edit', methods=['GET', 'POST'])
def block_add( dash_id, block_id = None ):
	db = get_db( 'db' )
	application = db.application()
	dashboard   = db.get_dash( dash_id )
	data_sources= get_data_sources() # Source databases (like those made by Push-to-db.py)

	if request.method == 'GET':
		# --- GET ----------------------------------------------------
		# identify the origin of the request (either the DASHBOARD, either the BLOCK-LIST)
		origin = 'BLOCK-LIST' if '/block/list' in request.referrer else 'DASHBOARD'

		if block_id:
			# Modify the existing block
			block = db.get_dash_block( block_id = block_id )
			dbPythonic = get_db( block['source'] )
			topics = dbPythonic.topics()
			return render_template( 'block_edit.html', row=block, dashboard=dashboard, application=application, data_sources=data_sources, topics=topics, origin=origin )
		else:
			# Create a new block 
			block = db.empty_block( dash_id )
			return render_template( 'block_edit.html', row=block, dashboard=dashboard, application=application, data_sources=data_sources, topics=None, origin=origin )
	else:
		# --- POST --------------------------------------------------
		if( request.form['action'] == u'cancel' ):
			# -- Abandon --
			# Send back to original screen (either the DASHBOARD, either the BLOCK-LIST)
			return redirect( 
				url_for('block_list', dash_id=request.form['dash_id'] ) 
					if request.form['origin']=='BLOCK-LIST' 
					else url_for('dashboard', id=request.form['dash_id']) )

		# Extract data (ready to save)
		#   request.form is already in unicode
		data = { 
		  'id' : (None if request.form['id'] == '' else int( request.form['id'] ) ),
		  'dash_id' : int( request.form['dash_id'] ),
		  'title' :  request.form['title'] , 
		  'block_type'  : request.form['block_type'],
		  'block_config': request.form['block_config'],
		  'color' : ( 'white'.decode('utf8') if not('color' in request.form) or (request.form['color']==u'') else request.form['color'] ),
		  'color_text' : ( 'black'.decode('utf8') if not('colortext' in request.form) or (request.form['colortext']==u'') else request.form['colortext'] ),
		  'icon' : (None if not('icon' in request.form) or (request.form['icon']==u'') else request.form['icon'] ),
		  'source' : request.form['source'],
		  'topic'  : request.form['topic'],
		  'hist_type' : request.form['hist_type'],
		  'hist_size' : safe_cast( request.form['hist_size'], int, 50 )
		}
		app.logger.debug( 'saving dash_block %s', data )
		get_db('db').save_dash_block( **data )
		flash( u'%s modifié' % data['title'] )
		
		# Send back to original screen (either the DASHBOARD, either the BLOCK-LIST)
		return redirect( url_for('block_list', dash_id=data['dash_id']) if request.form['origin']=='BLOCK-LIST' else url_for('dashboard', id=data['dash_id']) )

@app.route('/dashboard/<int:dash_id>/block/list')
def block_list( dash_id ):
	""" produce a list of blocks to allow editing and deletion """
	dashdb = get_db( 'db' )
	dash = dashdb.get_dash( dash_id )
	blocks = dashdb.get_dash_blocks( dash_id )
	application = dashdb.application() 

	return render_template( 'block_list.html', block_list=blocks, dash=dash ,application=application )

@app.route('/dashboard/<int:dash_id>/block/<int:block_id>/delete', methods=['GET','POST'])
def block_delete( dash_id, block_id ):
	""" delete a given block from the dashboard """
	application = get_db('db').application() 
	if request.method == 'GET':
		# --- GET ----------------------------------------------------
		row = get_db('db').get_dash_block( block_id )
		return render_template( 'block_del_confirm.html', row=row, application=application)
	else:
		# --- POST --------------------------------------------------
		app.logger.debug( "Deleted block")
		if request.form['action'] == u'cancel':
			return redirect( url_for('block_list', dash_id=dash_id ) )
		else:
			flash( u'Bloc %s effacé!' %  get_db('db').get_dash_block( block_id )['title'] )
			get_db('db').drop_dash_block( block_id )
			return redirect( url_for('block_list', dash_id=dash_id ) )

@app.route('/source/<string:source_name>/topics')
def source_topics( source_name ):
	""" for Ajax request: returns a JSON list of topic names for a given source name (eg: the Pythonic database)"""
	db_source = get_db( source_name )
	rows = db_source.topics()
	data = [ {'topic':row['topic'], 'history':row['tsname'] } for row in rows ]
	response = app.response_class(
		response=json.dumps(data),
		mimetype='application/json'
	)
	return response


#-------------------------------------------------------
#  Application Configure
#-------------------------------------------------------

@app.route('/app/config', methods=['GET','POST'] )
def app_config():
	abort( Response('La page permettant de configurer l application n est pas encore développée!') )

#-------------------------------------------------------
#  Mqtt Publish Proxy
#-------------------------------------------------------
# As mentionned in block.js::on_switch_change(event)
#    // On 06/09/2017, Javascript Paho Mqtt Client rely on WebSocket 
#    //    Mosquitto does support it by adding the following
#    //    configuration to the /etc/mosquitto/mosquitto.conf
#    //       port 1883
#    //       listener 9001
#    //       protocol websockets 
#    //    Unfortunately, on this days, the libwebsockets 2.1.0 as
#    //       uncompatibility with mosquitto 1.4 causing error message 
#    //       " Error: AMQJS0011E Invalid state not connected. "
#    //       Downgrading to libwebsockets 2.0.2 seems to solve the issue
#    //       but that's not an easy work on a Raspberry Pi.
#    //    The best would certainly to wait for libwebsockets 2.1.1 
#    //       that fix the issue.
#    //
#    //    More information: https://github.com/eclipse/mosquitto/issues/336
#    //
#    //    Workaround: rely on the Flask APP to rely the MQTT Publish
#
@app.route( '/MqttProxyPublish', methods=['POST'] )
def mqtt_publish_proxy():
	data = request.data
	app.logger.debug( u'MqttProxyPublish for %s'% data )
	try:
		dataDict = json.loads(data)
	except Exception as err:
		return make_response( (u'Invalid JSON format. %s'%err, 400) )
	
	# Must have the needed items
	# data = {"source":"mqtt_pythonic","topic":"maison/cave/chaufferie/cmd","msg":"ARRET"}
	try:
		assert 'source' in dataDict, "JSON: 'source' manquante." 
		assert 'topic'  in dataDict, "JSON: 'topic' manquante."
		assert 'msg'    in dataDict, "JSON: 'msg' manquante."
	except Exception as err:
		return make_response( (u'JSON format invalide. %s'%err,400) )

	_source = dataDict['source']
	_topic  = dataDict['topic']
	_msg    = dataDict['msg']

	try:
		mqtt_info = get_mqtt_sources(as_dict=True)[_source]
	except:
		return make_response( (u'Source invalide!', 400) )

	try:
		import paho.mqtt.client as mqtt_client
		client = mqtt_client.Client( client_id="dashboard_MqttProxyPublish" )
		if mqtt_info['username']:
			client.username_pw_set( username=mqtt_info['username'],
									password=mqtt_info['passwd'])
		client.connect( host=mqtt_info['server'], port=mqtt_info['port'] )
		client.publish( _topic, _msg ) # QoS 0
	except Exception as err:
		app.logger.error( 'MqttProxyPublish failed to relay to the broker for %s' % data  )
		app.logger.error( err )
		make_response( ( u'Erreur Broker! %s'%err , 400) )

	return make_response( (u'%s envoyé!'%_msg , 200 ) )

