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

INIFILE = "/etc/pythonic/push-to-db.ini"

# Init the logger as soon as possible 
logger = logging.config.fileConfig( INIFILE )

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

	def process_message( self, topic, payload ):
		""" traite la capture et l'enregistrement, doit être surchargé!"""
		logging.getLogger('root').debug('%s.process_message() to %s.%s for topic %s' % (self.__class__.__name__, self.storage_connector, self.storage_table, topic) )
		pass

class MqttTopicCapture( MqttBaseCapture ):
	""" Classe gérant la capture des messages et stockage de la dernière valeur dans une table """
	def __init__( self, subscribe_comalist, storage_target, connector ):
		super( MqttTopicCapture, self).__init__( subscribe_comalist, storage_target, connector )

class MqttTimeserieCapture( MqttBaseCapture ):
	""" Classe gérant la capture des messages et stockage de la dernière valeur dans une table """
	def __init__( self, subscribe_comalist, storage_target, connector ):
		super( MqttTimeserieCapture, self).__init__( subscribe_comalist, storage_target, connector )

class BaseConnector( object ):
	def __init__( self, params ):
		""" Initialisation 
		Parameters:
			params (dic): dictionnaire key=valeur en provenance de la section [connector.xxx]
			              du fichier de configuration
		"""	
		# print( params )

class SqliteConnector( BaseConnector ):
	pass

class App:
	""" Classe gérant le fonctionnement applicatif 

	Attributes:
		config (:obj: Config): Fichier de configuration
		logger (:obj: Logger): Fichier log initialisé depuis le fichier de configuration
		sub_handlers ([:obj:MqttBaseCapture, ]): Liste des Handlers MqttXxxCapture créés depuis le fichier de configuration file. 
		connectors ({:obj:BaseConnector, }): Liste de connecteur XxxxConnector créés depuis le fichier de configuration.
	"""

	def __init__(self):
		self.logger = logging.getLogger('root')
		self.logger.info( 'Initializing app')

		self.mqtt = None

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
					connector
				)
			)

	def _mqtt_on_connect( self, client, userdata, flags, rc ):
		self.logger.info( "mqtt connect return code: %s" % rc )
		self.mqtt_connected = (rc == 0)

	def _mqtt_on_message( self, client, userdata, message ):
		""" receiving message from the broker """
		self.logger.debug( "getting MQTT message..." )
		self.logger.debug( "  topic: %s" % message.topic )
		self.logger.debug( "  message: %s" % message.payload )
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

			for target_id, sub_handler in to_call.items():
				sub_handler.process_message( message.topic, message.payload )

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

		try:
			self.connect_broker()
		except Exception as err:
			self.logger.error( 'connect_broker() error with %s' % err)
			raise
		
		try:
			self.mqtt.loop_forever()
		except Exception as err:
			self.logger.error( 'Error while processing broker messages! %s' % err )
			raise

if __name__ == "__main__":
	#main()
	app = App()
	app.run()

