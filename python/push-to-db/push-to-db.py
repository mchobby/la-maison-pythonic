#!/usr/bin/python
# -*- coding: utf8 -*-
""" La Maison Pythonic - push-to-db  

	Pousse les données MQTT dans une DB SQLite en fonction du paramètrage contenu dans le fichier de configuration.

	Script pour Python 2.7
 """ 
import ConfigParser
import re
import logging, logging.config
import paho.mqtt.client as mqtt_client
import time
import datetime
import threading
from Queue import Queue
import sqlite3 as sqlite

INIFILE = "/etc/pythonic/push-to-db.ini"

# Init the logger as soon as possible 
logger = logging.config.fileConfig( INIFILE )

# -------------------------------------------------------------------------------
#
#  CONFIG        - lecture du fichier de configuration, 
#  QueuedMessage - Structure du message mis en queue
#
# -------------------------------------------------------------------------------

# Classe maintenant les informations du fichier de config
class Config:
	""" Contient les informations de configuration. 
		Les sections et clés sont maitenu en minuscule 

	Example: 
		config = Config( INIFILE )
		config._dump()
		
		# Retourne la valeur d'une clé dans une section
		print( '[app].db -> %s' % config.get( 'app', 'db'))

		# Retourne la valeur par défaut si la clé est manquante 
		print( config.get( 'app', 'pas-present', 'valeur-par-defaut') )

		# Lève une exception AttributeError car par de valeur par défaut
		# si la clé est manquante 
		print( config.get( 'app', 'pas-present' ) )
	"""
	sections = {}
	inifilename = ""
	logger = None

	def __init__(self, inifile ):
		self.sections = {}
		self.logger = logging.getLogger('root')
		self._readini( inifile )

	def _ConfigSectionMap(self, config_parser, section):
		dict1 = {}
		option_names = config_parser.options(section)
		for option_name in option_names:
			try:
				dict1[option_name.lower()] = config_parser.get(section, option_name)
				if dict1[option_name.lower()] == -1:
					self.logger.warning("skip: %s" % option_name)
			except Exception as err:
				self.logger.warning("exception %s on key '%s'! Key value set to None" % (err,option_name) )
				dict1[option_name] = None
		return dict1

	def _readini( self, inifile ):
		""" Lecture du fichier et stockage des valeurs """
		# Eviter l'interpolation des %(xxx) dans la config du logger
		parser = ConfigParser.RawConfigParser()
		parser.read( inifile )
		self.inifilename = inifile
		for section in parser.sections():
			self.sections[section.lower()] = self._ConfigSectionMap(parser, section)

	def _dump( self ):
		""" affiche le contenu de la config sur le terminal """
		print( "== Dump Config %s" % ("="*20) )
		print( self.inifilename )
		for section_name, section_values in self.sections.items():
			for key,value in section_values.items():
				print( "[%s].%s = %s" % (section_name, key, value) )

	def search_section( self, reg_exp ):
		""" Retrouve tous les noms de section répondant à l'expression régulière """
		_result = []
		_re = re.compile( reg_exp )
		for section in self.sections.keys():
			if _re.match( section ):
				_result.append( section )
		return _result

	def get( self, section, key, default = Exception ):
		""" Retourne la valeur d'une clé dans une section .
		    Si la valeur est manquante alors la valeur par défaut (default). 
			Si la valeur par défaut est Exception alors lance une exception AttributeError si section et name non trouvé """
		if not( section in self.sections ):
			if default == Exception:
				raise AttributeError( "Invalid section request [%s].%s" %(section,key) )
			else:
				return default
		else:
			dic = self.sections[section] 
			if not( key in dic ):
				if default == Exception:
					raise AttributeError( "Invalid name request [%s].%s" % (section,key) )
				else:
					return default
			else:
				return dic[key]

	def getint( self, section, key, default = Exception ):
		""" return the value as an integer """
		return int( self.get(section, key, default) )

class QueuedMessage( object ):
	""" Definit la strucutre des messages MQTT empilé dans une queue dans message_queue en attente de 
	    leurs traitements (enregistrement en DB par le thread MessageLazyWriter) 
	"""

	__slots__ = ['receive_time', 'topic', 'payload', 'sub_handler', 'qos', 'timeserie_sub_handlers']

	def __init__(self, receive_time, topic, payload, qos, sub_handler, timeserie_sub_handlers = None ):
		self.receive_time = receive_time
		self.topic = topic
		self.payload = payload
		self.qos = qos
		# Une des classes MqttXxxCapture "subscripter handler class" capable
		# d'utiliser d'écrire le message en DB en utilisant son connecteur. 
		self.sub_handler = sub_handler
		# Les objets MqttTimeserieCapture (et descendant) "subscripter handler class" 
		# ayant également stocké le même message que pour le sub_hander. NB: les messages sont stockés en timeserie avant le stockage en capture. 
		self.timeserie_sub_handlers = timeserie_sub_handlers

# -------------------------------------------------------------------------------
#
#  MQTTxxxCapture - Identifie les messages MQTT à capturer (utilise des filtres), 
#                 - Aussi denommé Sub_Hanlder (Subcription_Handler) car capable
#                   de gérer la souscription correspondante.
#                 - Pilote le connector pour stocker le message en DB
#
# -------------------------------------------------------------------------------

class MqttBaseCapture( object ):
	""" Classe de base pour gérer les différentes souscriptions 

	Attributes:
		sub_filters ([str, ]): Liste des filtres de souscription
		sub_regexps ([:obj:`compiled regexp`]): Liste des expressions régulières correspond aux filtres de souscription
		storage_connector (str): Connecteur/Adaptateur permettant d'accéder au storage_table. 
		storage_table (str): Table/fichier/etc qui recevra les données
	"""

	def __init__( self, subscribe_comalist, storage_target, connector ):
		""" Initialisation.

		Parameters:
			subcribe_comalist (str): liste des soucriptions (séparées par une virgule)
			storage_target (str): Contient la destination de stockage sous la forme storage_connector.storage_table
			connector (:obj:BaseConnector): objet connector pour accéder au stockage (ex: Sqlite database)
		"""
		#logging.getLogger('root').debug( 'Register %s @ %s for subscriptions %s' % (self.__class__.__name__, self, subscribe_comalist) )
		self.sub_filters = subscribe_comalist.split(",")
		self.sub_regexps = []
		self.connector   = connector
		for sub_filter in self.sub_filters:
			self.sub_regexps.append( self.mqtt_filter_to_re(sub_filter) )
		self.storage_connector = (storage_target.split('.')[0]).strip()			 
		self.storage_table     = (storage_target.split('.')[1]).strip()

		#logging.getLogger('root').debug(' --list of sub_filters' )
		#for s in self.sub_filters:
		#	logging.getLogger('root').debug('  * %s' % s )
		#logging.getLogger('root').debug(' --list of regexp registered' )
		#for _re in self.sub_regexps:
		#	logging.getLogger('root').debug('  * %s' % _re.pattern )

	def mqtt_filter_to_re( self, sub_filter ):
		""" converti un filtre de souscription mqtt en expression régulière """
		s = sub_filter.replace( '+', '[^/]+' ) # remplacer le +
		s = s.replace('#', '.+') # remplacer le #
		s = s.replace( '/', '\/' ) # escape des /
		return re.compile( s )

	def match_subscription( self, topic ):
		""" Indique si le topic correspond à une des souscriptions enregistrées pour la capture"""
		#logging.getLogger('root').debug('Match_subscription() --- list of regexp' )
		#for _re in self.sub_regexps:
		#	logging.getLogger('root').debug('  * %s' % _re.pattern )

		#logging.getLogger('root').debug('Match subscription for topic %s @ %s' % (topic, self) )
		for _re in self.sub_regexps:
			if _re.match( topic ):
				return True
		return False

	def target_id( self ):
		""" Retourne une valeur qui permet d'identifier de façon univoque 
		    la destination où sera sauvé le message traité par la classe """
		return '%s.%s' % (self.storage_connector.lower(), self.storage_table.lower() )

	def store_data( self, queued_message ):
		""" traite le message capturé pour l'enregistré à l'aide du connecteur, doit être surchargé!"""
		#logging.getLogger('root').debug('%s.store_data() to %s.%s for topic %s' % (self.__class__.__name__, \
		#	self.storage_connector, self.storage_table, queued_message.topic) )
		logging.getLogger('root').warning( '%s.store_data() must be overloaded' % self.__class__.__name__ )
		

class MqttTopicCapture( MqttBaseCapture ):
	""" Classe gérant la capture des messages et stockage de la dernière valeur dans une table """
	def __init__( self, subscribe_comalist, storage_target, connector ):
		super( MqttTopicCapture, self).__init__( subscribe_comalist, storage_target, connector )

	def store_data( self, queued_message ):
		""" traite le message capturé pour l'enregistré à l'aide du connecteur! 

		MqttTopicCapture enregistre juste la dernière valeur dans la table."""

		# Est-ce que le message à également été stocké dans une ou plusieurs tables timeserie ? ... sur le même connecteur?
		tsname = None
		if queued_message.timeserie_sub_handlers:
			# Uniquement les timeserie_sub_handler partageant la même db (donc le même storage_connector [le nom]) 
			for ts_sub_handler in [ sub_handler for sub_handler in queued_message.timeserie_sub_handlers if sub_handler.storage_connector == self.storage_connector ]:
				# Juste recupérer le 1ier nom de table 
				tsname = ts_sub_handler.storage_table
				break;
		# Le connecteur sait comment accéder à la table
		self.connector.update_value( self.storage_table, queued_message.receive_time, 
			queued_message.topic, queued_message.payload, queued_message.qos, tsname = tsname )

class MqttTimeserieCapture( MqttBaseCapture ):
	""" Classe gérant la capture des messages et stockage de la dernière valeur dans une table """
	def __init__( self, subscribe_comalist, storage_target, connector ):
		super( MqttTimeserieCapture, self).__init__( subscribe_comalist, storage_target, connector )

	def store_data( self, queued_message ):
		""" traite le message capturé pour l'enregistré à l'aide du connecteur! 

		MqttTimeserieCapture enregistre la nouvelle valeur dans une table historique."""
		# Le connecteur sait comment accéder à la table
		self.connector.timeserie_append( self.storage_table, queued_message.receive_time, 
			queued_message.topic, queued_message.payload, queued_message.qos )

# -------------------------------------------------------------------------------
#
#  Les CONNECTORS - accès à la DB et aux tables
#
# -------------------------------------------------------------------------------

class BaseConnector( object ):
	def __init__( self, params ):
		""" Initialisation 
		Parameters:
			params (dic): dictionnaire key=valeur en provenance de la section [connector.xxx]
			              du fichier de configuration
		"""	
		self.params = params

class SqliteConnector( BaseConnector ):
	""" Connector to Sqlite database """
	def __init__( self, params ):
		super( SqliteConnector, self ).__init__( params )
		# fichier de stockage de la DB
		# typiquement /var/local/sqlite/pythonic.db
		self.db_file = params['db']
		# reference vers le moteur DB
		self._conn = None 

	def is_connected( self ):
		return (self._conn != None)

	def connect( self ):
		if not self.is_connected():
			logging.getLogger('connector').debug( 'Connect to sqlite db %s' % self.db_file )
			self._conn = sqlite.connect( self.db_file )

	def disconnect( self ):
		if self.is_connected():
			logging.getLogger('connector').debug( 'disconnect() sqlite' )
			self._conn.close()
			self._conn = None

	def commit( self ):
		if self.is_connected():
			logging.getLogger('connector').debug( 'commit() on sqlite' )
			# sauver les modifications
			self._conn.commit()

	def update_value( self, table_name, receive_time, topic, payload, qos, tsname=None ):
		""" Stocke la dernière valeur connue dans la table """
		logging.getLogger('connector').debug( 'update_value() on sqlite' )

		if tsname:
			# Sauver le nom du TimeSerie si on l'a sous la main
			sSql = "UPDATE %s SET message = ?, qos = ?, rectime = ?, tsname = ?  where topic = ?" % table_name
			_data = (payload, qos, receive_time, tsname, topic)
		else:
			sSql = "UPDATE %s SET message = ?, qos = ?, rectime = ? where topic = ?" % table_name
			_data = (payload, qos, receive_time, topic)

		self.connect()
		cur = self._conn.cursor()
		r = cur.execute( sSql, _data )
		# Si record pas encore mis-à-jour --> insérer
		if r.rowcount == 0:
			if tsname:
				sSql = "INSERT INTO %s (topic,message,qos,rectime, tsname) VALUES (?,?,?,?,?)" % table_name
				r = cur.execute( sSql, (topic,payload,qos,receive_time, tsname) )			
			else:
				sSql = "INSERT INTO %s (topic,message,qos,rectime) VALUES (?,?,?,?)" % table_name
				r = cur.execute( sSql, (topic,payload,qos,receive_time) )

	def timeserie_append( self, table_name, receive_time, topic, payload, qos ):
		""" Stocke l'historique de valeurs (timeseries) dans la table """
		logging.getLogger('connector').debug( 'timeserie_append() on sqlite' )

		sSql = "INSERT INTO %s (topic,message,qos,rectime) VALUES (?,?,?,?)" % table_name

		self.connect()	
		cur = self._conn.cursor()
		r = cur.execute( sSql, (topic,payload,qos,receive_time) )			



# -------------------------------------------------------------------------------
#
#  THREAD MessageLazyWriter - traitement de la queue des messages MQTT capturés 
#
# -------------------------------------------------------------------------------

class MessageLazyWriter(threading.Thread):
	""" Thread qui traite la queue des messages MQTT (voir QueuedMessage) pour stocker ceux-ci en DB en
	    en utilisant les connecteurs.

	    Le thread doit attendre un minimum de messages (ou max de temps) avant de lancer une opération
	    d'écriture car celles-ci peuvent être bloquantes (suivant le moteur DB utilisé) 
	    """ 
	def __init__( self, params, message_queue, connectors, stopper_event ):
		""" Initialisation
		Parameters:
			params (dic): dictionnaire key=valeur en provenance de la section [lazywriter]
			              du fichier de configuration
		"""
		super( MessageLazyWriter, self ).__init__()
		# Params provient de la secion [lazywriter] du fichier de config
		self.max_queue_latency   = int(params['maxqueuelatency'])
		self.max_queue_size      = int(params['maxqueuesize'])
		self.pause_after_process = int(params['pauseafterprocess'])
		# Queue FiFo synchronisée
		self.message_queue = message_queue
		# Liste des connecteurs
		self.connectors = connectors
		# Event pour signaler l'arrêt du thread
		self.stopper_event = stopper_event

		self.logger = logging.getLogger('root')

	def run( self ):
		self.logger.debug( 'LazyWriter thread started')
		# contient l'heure a laquelle le compte à rebours du 
		# du temps de latence débute (lors de l'arrivé de la
		# première valeur dans la queue)
		latency_start = None 
		while not self.stopper_event.is_set():
			if self.message_queue.empty():
				# time.sleep( self.pause_after_process )
				latency_start = None
				continue 
			else:
				# Si queue pas vide alors débuter temps de latence
				# si ce n'est pas encore fait 
				if latency_start == None:
					self.logger.debug( 'LazyWriter latency_start set to now')
					latency_start = datetime.datetime.now()

			if self.message_queue.qsize() > self.max_queue_size:
				self.logger.info( 'LazyWriter queue size %s reached -> Process_message_queue.' % self.max_queue_size )
				self.process_message_queue()
				latency_start = None
				time.sleep( self.pause_after_process )

			elif latency_start and ((datetime.datetime.now()-latency_start).seconds > self.max_queue_latency):
				self.logger.info( 'LazyWriter latency %s sec reached -> Process_message_queue.' % self.max_queue_latency )
				self.process_message_queue()
				latency_start = None
				time.sleep( self.pause_after_process )

		self.logger.debug( 'LazyWriter thread exit')

	def process_message_queue( self ):
		""" Ecrit les messages de la Queue dans la DB """
		con_list = []
		pmq_logger = logging.getLogger('pmq')
		while not self.message_queue.empty():
			queued_message = self.message_queue.get()
			try:
				pmq_logger.debug( 'process_message_queue %s for handler %s on %s with payload %s' % \
					(queued_message.topic, queued_message.sub_handler.__class__.__name__, \
						queued_message.sub_handler.target_id(), queued_message.payload) )
				# Collecter les connecteur mis-en-oeuvre
				connector = queued_message.sub_handler.connector
				if not connector in con_list:
					con_list.append( connector )
				# Demander au sub_handler (donc MqttxxxCapture) de stocker les données en DB
				# grace a son connector.
				queued_message.sub_handler.store_data( queued_message )
			except Exception as err:
				pmq_logger.error( 'process_message_queue encounter an error while processing the message' )
				pmq_logger.error( '  %s with %s' % (err.__class__.__name__, err) )				
				pmq_logger.error( '  handler: %s' % queued_message.sub_handler.__class__.__name__ )
				pmq_logger.error( '  topic  : %s' % queued_message.topic )
				pmq_logger.error( '  payload: %s' % queued_message.payload )
			finally:
				self.message_queue.task_done()
		# Faire un commit sur tous les connecteurs
		for connector in con_list:
			connector.commit()
			connector.disconnect()
				



# -------------------------------------------------------------------------------
#
#  Class Application 
#
# -------------------------------------------------------------------------------
class App:
	""" Classe gérant le fonctionnement applicatif 

	Attributes:
		config (:obj: Config): Fichier de configuration
		logger (:obj: Logger): Fichier log initialisé depuis le fichier de configuration
		sub_handlers ([:obj:MqttBaseCapture, ]): Liste des Handlers MqttXxxCapture créés depuis le fichier de configuration file. 
		connectors ({connector_name, :obj:BaseConnector, }): Liste de connecteur XxxxConnector créés depuis le fichier de configuration.
		message_queue (:obj:Queue): Liste des messages MQTT reçu et a traiter sous forme de tuple(datetime_reception,topic,message)
	"""

	def __init__(self):
		self.logger = logging.getLogger('root')
		self.logger.info( 'Initializing app')

		self.mqtt = None
		self.message_queue = None 
		self.connectors = None
		self.sub_handlers = None
		# Event utilisé pour arrêter les Thread
		self.stopper = None  

		self.config = Config( INIFILE )
		# self.config._dump()

		self.build_connectors()
		self.build_sub_handlers()

	def build_connectors( self ):
		""" construire la liste des objects BaseConnector depuis la configuration """
		self.connectors = {} # Réinitialiser la liste
		# collecter la liste des sections "connector.xxxx"
		lst = self.config.search_section( "^connector\.\w+$" )
		for section in lst:
			connector_classname = self.config.get( section, 'class')
			# reference vers la classe
			connector_class = globals()[connector_classname]
			# créer la classe et l'enregistrer sous son nom simple
			self.connectors[ section.replace('connector.','') ] = \
				connector_class( self.config.sections[section] )

	def build_sub_handlers( self ):
		""" construire la liste des objets MqttBaseCapture depuis la configuration"""
		self.sub_handlers = [] # Réinitialiser la liste
		# collecter la liste des sections "mqtt.capture.x"
		lst = self.config.search_section( "^mqtt\.capture\.\d+$" )
		for section in lst:
			handler_classname = self.config.get( section, 'class' )
			# reference vers la classe
			handler_class = globals()[handler_classname]
			# Identify the connector instance
			connector_name = self.config.get( section, 'storage').split('.')[0]
			if not(connector_name in self.connectors):
				raise Exception( 'No [connector.%s] defined for storage=%s (see [%s])' % (connector_name,self.config.get( section, 'storage'),section) )
			connector = self.connectors[connector_name]
			self.sub_handlers.append(
			    # Create an instance of the class 
				handler_class( 
					self.config.get( section, 'subscribe' ),
					self.config.get( section, 'storage'),
					connector # Chaque Subscription_Handler à déjà une référence vers le connecteur DB à utiliser.
				)
			)

	def _mqtt_on_connect( self, client, userdata, flags, rc ):
		self.logger.info( "mqtt connect return code: %s" % rc )
		self.mqtt_connected = (rc == 0)

	def _mqtt_on_message( self, client, userdata, message ):
		""" receiving message from the broker """
		self.logger.info( "getting MQTT message..." )
		self.logger.info( "  topic  : %s" % message.topic )
		self.logger.info( "  message: %s" % message.payload )
		self.logger.info( "  QoS    : %s" % message.qos )
		try:
			to_call = {} # sub handler to call
			for sub_handler in self.sub_handlers:
				if sub_handler.match_subscription( message.topic ):
					# Identifier la destination de sauvegarde pour eviter
					# de sauvegarder plusieurs fois le message dans le
					# même table
					target_id = sub_handler.target_id()
					if not( target_id in to_call ):
						to_call[target_id] = sub_handler

			# Handle TimeSerie capture first
			queued_timeserie = []
			for target_id, sub_handler in to_call.items() : 
				if not isinstance( sub_handler, MqttTimeserieCapture ):
					continue
				to_queue = QueuedMessage( receive_time=datetime.datetime.now(), \
					topic=message.topic, payload=message.payload, \
					qos=message.qos, sub_handler=sub_handler  )
				self.message_queue.put( to_queue )
				# Remember the queued timeserie for this message
				queued_timeserie.append( sub_handler )
			
			# Handle Message Capture after
			for target_id, sub_handler in to_call.items() : 
				if isinstance( sub_handler, MqttTimeserieCapture ):
					continue
				to_queue = QueuedMessage( receive_time=datetime.datetime.now(), \
					topic=message.topic, payload=message.payload, \
					qos=message.qos, sub_handler=sub_handler, \
					timeserie_sub_handlers=queued_timeserie if len(queued_timeserie)>0 else None  )
				self.message_queue.put( to_queue )

				#sub_handler.process_message( message.topic, message.payload )

		except Exception as err:
			self.logger.error( 'Exception while processing MQTT message')
			self.logger.error( "  topic: %s" % message.topic )
			self.logger.error( "  message: %s" % message.payload )
			self.logger.error( "  exception: %s" % err )

	def connect_broker( self ):
		""" Connect the broker and perform all the needed subscriptions """
		
		if self.mqtt:
			del( self.mqtt )
			self.mqtt = None
		self.mqtt_connected = False

		self.mqtt = mqtt_client.Client( client_id = 'push-to-db' )
		self.mqtt.on_connect = self._mqtt_on_connect
		self.mqtt.on_message = self._mqtt_on_message
		if not( self.config.get( 'mqtt.broker', 'username', default = None ) in (None, 'None') ):
			self.mqtt.username_pw_set( 
				username = self.config.get( 'mqtt.broker', 'username'),
				password = self.config.get( 'mqtt.broker', 'password')
				)
		self.mqtt.connect(
				host = self.config.get( 'mqtt.broker', 'mqtt_broker' ),
				port = self.config.getint( 'mqtt.broker', 'mqtt_port' ),
				keepalive = self.config.getint( 'mqtt.broker', 'mqtt_keepalive')
			)

		# effectue toutes les souscriptions nécessaires
		sub_done = [] 
		for sub_handler in self.sub_handlers:
			for sub in sub_handler.sub_filters:
				# Ne pas faire deux fois la même souscription
				if not sub in sub_done:
					self.logger.info( 'subscribing %s' % sub )
					self.mqtt.subscribe( sub )
					sub_done.append( sub )

	def run( self ):
		self.logger.info( 'Running app')
		self.message_queue = Queue() 
		self.stopper = threading.Event()

		# Thread de traitement des QueuedMessage
		lazyWriter = MessageLazyWriter( self.config.sections['lazywriter'], \
			self.message_queue, self.connectors, \
			self.stopper )
		lazyWriter.start()

		try:
			self.connect_broker()
		except Exception as err:
			self.logger.error( 'connect_broker() error with %s' % err)
			raise
		
		try:
			self.mqtt.loop_forever()
		except Exception as err:
			self.logger.error( 'Error while processing broker messages! %s' % err )
		except KeyboardInterrupt:
			self.logger.info( 'User abord with KeyboardInterrupt exception' )
		except SystemExit:
			self.logger.info( 'System exit with SystemExit exception!' )

		# signal threads to stop
		self.stopper.set()

		# Wait the thread to finish
		self.logger.info( 'Waiting for LazyWriter thread...')
		lazyWriter.join()

if __name__ == "__main__":
	#main()
	app = App()
	app.run()

