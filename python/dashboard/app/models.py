# coding: utf8
from app import configuration
from app import app
from flask import g
import sqlite3
from datetime import datetime

class GetDbError( Exception ):
   pass

def get_db( db_key ):
   """ Retreive or Construct a database Helper object base .cfg file content.
       This routine will extract the <db_key>=<sqlite3-database-file> and
       <db_key>_class=<helper_db_ClassName_to_create>  

   :param db_key: name of the database parameter in the dashboard.cfg file (db or db_pythonic)
   :type db_key: string 
   :return: a connection helper to the database"""

   # dict of database connexion helpers
   if not 'dbs' in g:
      g.dbs = {}
   
   # Connexion already registered in the dict
   if not( db_key in g.dbs ):
      classname_key = '%s_class' % db_key
      #DEBUG: app.logger.debug('extract attributes "%s" and "%s" from configuration!' % (db_key,classname_key) )
      
      try:
         db_filename = getattr( configuration, db_key )
      except:
         raise GetDbError( 'Missing %s entry in configuration file!' % db_key )
      # retreive the classname from db_class= or db_pythonic_class= entry
      try:
         classname = getattr( configuration, classname_key )
      except:
         raise GetDbError( 'Missing %s entry in configuration file!' % classname_key )
      
      #DEBUG: app.logger.debug('  +->  %s = %s' % (db_key,db_filename)  )
      #DEBUG: app.logger.debug('  +->  %s = %s' % (classname_key,classname)  )
      # reteive the reference to the class
      try: 
         Class = globals()[ classname ]
      except:
         raise GetDbError( 'class %s does not exists!' % classname )
      # create an object from the class
      db_helper = Class( db_filename )
      g.dbs[ db_key ] = db_helper
   else:
      db_helper = g.dbs[ db_key ]

   return db_helper

def get_data_sources():
   """ List the databases sources available in the config file """
   data_sources = getattr( configuration, 'data_sources' ) 
   assert data_sources, "No data_sources defined in the config file"
   assert type( data_sources ) == list, "the config file data_sources must be a list of string"
   return data_sources

def get_mqtt_sources( as_dict = False ):
   """ List the MQTT server sources available in the config file 

   :param as_dict: False -> returns a list of string (like get_data_source does). True -> return a dictionnary of dictionnary to embed the configuration parameters
   :type as_dict: boolean 
   :return: a list of string -OR- { '<mqtt_source_1>' : {'server':<mqtt_server>, 'port':..., 'username':..., 'passwd':....} , 
                                    '<mqtt_source_2>' : {...}  
                                  }
   """
   def extract_config( key, default='_' ):
      """ Extract a named value from configuration """
      try:
         _result = getattr( configuration, key )
      except:
         if default=='_':
            raise GetDbError( 'Missing %s entry in configuration file!' % key )
         else:
            _result = default
      return _result

   mqtt_sources = getattr( configuration, 'mqtt_sources' )
   if not( mqtt_sources ):
      mqtt_sources =  []  
   assert type( mqtt_sources ) == list, "the config file mqtt_sources must be a list of string"

   if not( as_dict ):
      return mqtt_sources
   else:
      _dic = {}
      for _source in mqtt_sources:
         _params = {}
         _params['server']  = extract_config( _source )
         _params['port']    = extract_config( '%s_port' % _source )
         _params['username']= extract_config( '%s_username' % _source, None )
         _params['passwd']  = extract_config( '%s_passwd'   % _source, None )
         _dic[_source] = _params
      return _dic


class DashboardDB( object ):
   """ Helper class to easily request data """
   _db = None

   def __init__( self, db_filename ):
      self._db = sqlite3.connect( db_filename )
      self._db.row_factory = sqlite3.Row

   def __del__( self ):
      self.close()

   def close( self ):
      if self._db :
         self._db.close()
         del(self._db)
         self._db = None

   def str_to_datetime( self, str ):
      """ Sqlite store time with '%Y-%m-%d %H:%M:%S.%f' format. This function convert it bask to datetime format """
      try: 
         return datetime.strptime( str , '%Y-%m-%d %H:%M:%S.%f' )
      except:
         return None

   def application(self):
      """ Return a row with the application data """
      cursor = self._db.cursor()
      # Should returns one row only
      cursor.execute( "select id, label, 'red darken-4' as color from application order by id" )
      if cursor.rowcount == 0:
         # mimic an empty record
         return { 'id' : None, 'label' : None, 'color': 'red darken-4'}
      else: 
         return cursor.fetchone()

   # == DASHBOARDS =====================================================

   def dashes( self ):
      """ Return a list of Dashes rows (id, label, color, icon)"""
      cursor = self._db.cursor()
      cursor.execute( "select id, label, color, icon, color_text from dashes order by label" )
      if cursor.rowcount == 0:
         return []
      else: 
         return cursor.fetchall()
      
   def empty_dash( self ):
      """ Return an empty dashboard record """
      # mimic the record into a dict
      return {'id':None, 'label':None, 'color':None, 'icon':None, 'color_text':None }

   def get_dash( self, id ):
      """ return a dashboard record """
      cursor = self._db.cursor()
      cursor.execute( "select id, label, color, icon, color_text from dashes where id = ?" , (id,) )
      if cursor.rowcount == 0:
         return empty_dash()
      else: 
         return cursor.fetchone()

   def save_dash( self, **kwarg ):
      """ Save a dashboard record/dict. id=None inserts the record, id!=None update the record """
      cursor = self._db.cursor()
      if kwarg['id']:
         cursor.execute( "update dashes set label = ?, icon = ?, color = ?, color_text = ? where id = ?", 
            (kwarg['label'],kwarg['icon'],kwarg['color'],kwarg['color_text'],kwarg['id']) )
         self._db.commit()
      else:
         cursor.execute( "insert into dashes (id, label, icon, color, color_text ) values (?,?,?,?,?)", 
            (None,kwarg['label'],kwarg['icon'],kwarg['color'],kwarg['color_text']) )
         self._db.commit()

   def drop_dash( self , id ):
      """ Drop the dashboard record and associated items """
      cursor = self._db.cursor()
      cursor.execute( "delete from dash_blocks where dash_id = ?", (id,) )
      cursor.execute( "delete from dashes where id = ?", (id,) )
      self._db.commit()

   # == BLOCKS =====================================================

   def get_dash_blocks( self, dash_id ):
      """ return the list of blocks inside à dashboard """
      cursor = self._db.cursor()
      cursor.execute( "select id, dash_id, title, icon, color, color_text, block_type, block_config, source, topic, hist_type, hist_size from dash_blocks where dash_id = ? order by dash_id", (dash_id,) )
      if cursor.rowcount == 0:
         return []
      else: 
         return cursor.fetchall()

   def save_dash_block( self, **kwarg ):
      """ Save a dash_block record/dic. id=None inserts the record. id!=None update the record """
      cursor = self._db.cursor()
      if kwarg['id']:
         cursor.execute( "update dash_blocks set dash_id = ?, title = ?, block_type=?, block_config = ?, color = ?, color_text = ?, icon = ?, source = ?, topic = ?, hist_type = ?, hist_size = ? where id = ?", 
            (kwarg['dash_id'],kwarg['title'],kwarg['block_type'],kwarg['block_config'],kwarg['color'],kwarg['color_text'],kwarg['icon'],kwarg['source'],kwarg['topic'],kwarg['hist_type'],kwarg['hist_size'],kwarg['id']) )
         self._db.commit()
      else:
         cursor.execute( "insert into dash_blocks (id, dash_id, title, block_type, block_config,  color, color_text, icon, source, topic, hist_type, hist_size ) values (?,?,?,?,?,?,?,?,?,?,?,?)", 
            (None,kwarg['dash_id'],kwarg['title'],kwarg['block_type'],kwarg['block_config'],kwarg['color'],kwarg['color_text'],kwarg['icon'],kwarg['source'],kwarg['topic'],kwarg['hist_type'],kwarg['hist_size']) )
         self._db.commit()

   def get_dash_block( self, block_id ):
      """ return a BLOCK record """
      cursor = self._db.cursor()
      cursor.execute( "select id, dash_id, title, icon, color, color_text, block_type, block_config, source, topic, coalesce(hist_type,'LIST') as hist_type, coalesce(hist_size,50) as hist_size from dash_blocks where id = ?" , (block_id,) )
      if cursor.rowcount == 0:
         return empty_block()
      else: 
         return cursor.fetchone()

   def drop_dash_block( self , block_id ):
      """ Drop the block record and associated items """
      cursor = self._db.cursor()
      cursor.execute( "delete from dash_blocks where id = ?", (block_id,) )
      self._db.commit()

   def empty_block( self, dash_id ):
      """ Return an empty dashboard block record """
      # mimic the record into a dict
      return {'id':None, 'dash_id': dash_id, 'title':None, 'color':None, 'color_text':None, 'icon':None, 
              'block_type':None, 'block_config':None, 'source':None, 'topic':None, 'hist_type':'LIST', 'hist_size':50 }    

class PythonicDB( object ):
   """ Helper class to easily access the push-to-db data """
   
   _db = None 

   def __init__( self, db_filename ):
      self._db = sqlite3.connect( db_filename )
      self._db.row_factory = sqlite3.Row

   def __del__( self ):
      self.close()

   def close( self ):
      if self._db :
         self._db.close()
         del(self._db)
         self._db = None

   def topics( self ):
      """ return a collection of topics available in the database """
      cursor = self._db.cursor()
      cursor.execute( "select topic, tsname from topicmsg order by topic" )
      if cursor.rowcount == 0:
         return []
      else: 
         return cursor.fetchall()

   def get_values( self, topic_list ):
      """ Return the data from a list of topics names.

      :param topic_list: list of topic (string) to collect the data. None will connect tge data for all entries .

      Remark:
       * rectime returns an unicode string at format '%Y-%m-%d %H:%M:%S.%f' """

      cursor = self._db.cursor()
      if topic_list:
         # create a string '?,?,?' having the length topic_lst
         _interrogation_list = ','.join( ['?']*len(topic_list) )
         cursor.execute( "select topic, message, tsname, rectime from topicmsg where topic in ( %s )" % _interrogation_list, tuple(topic_list) )
      else:
         cursor.execute( "select topic, message, tsname, rectime from topicmsg order by topic" )

      if cursor.rowcount == 0:
         return []
      else: 
         return cursor.fetchall()

   def get_history( self, tsname, topic, from_id = None, _len=50 ):
      """ Retreive the history record from the tsname table for the given topic. 
      record set is returned descending from the last row (or from_id) with a maximum size """

      sSql = "select id, message, qos, rectime from %s where topic = '%s' %s order by id desc limit %s" % (tsname, topic, "and id <= %s"%from_id if from_id else "", _len )

      cursor = self._db.cursor()
      cursor.execute( sSql )
      if cursor.rowcount == 0:
         return []
      else: 
         return cursor.fetchall()      


@app.teardown_appcontext
def teardown_app(exception):
   # Version plus récente de Flask
   #
   #_bdd = g.pop( 'bdd', None )
   #if( _bdd):
   #   _bdd.close()

   _dbs = g.get( 'dbs', None )
   if( _dbs):
      for name, _db in _dbs.items():
         _db.close()
         del( _db )
   del( _dbs )
