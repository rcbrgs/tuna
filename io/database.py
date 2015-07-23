import logging
import pymysql
import sys
import threading
import time
import tuna

class database ( threading.Thread ):
    def __init__ ( self ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.7"
        self.changelog = {
            '0.1.7' : "Added a lockable queue and diverted functions to enqueue requests.",
            '0.1.6' : "Tweaked exception handling during update to be more  resilient to error.",
            '0.1.5' : "Added table noise.",
            '0.1.4' : "Wrapped values in single quotes for insert.",
            '0.1.3' : "Better logging during insert.",
            '0.1.2' : "Added type info to dataset table.",
            '0.1.1' : "Refactored to use table definitions from a single variable.",
            '0.1.0' : "Initial version."
        }
        self.log = logging.getLogger ( __name__ )
        self.log_level = logging.INFO
        self.daemon = True
        self.shutdown = False

        self.connection = None
        self.expected_tables = {
            'datasets' : "( hash varchar ( 40 ) primary key,"
                         "file_name varchar ( 255 ),"
                         "file_type varchar ( 10 ),"
                         "alias varchar ( 30 ) )",
            'noise'    : "( hash varchar ( 40 ) primary key,"
                         "radius int,"
                         "threshold int )"
        }
        self.queue = [ ]
        self.queue_lock = tuna.io.lock ( )

    def __del__ ( self ):
        self.stop ( )

    def run ( self ):
        self.log.debug ( "<%s>" % ( sys._getframe ( ).f_code.co_name ) )
                             
        # Check database connection is up.
        if not self.check_mysql_connection ( ):
            # Try to up it.
            self.open_mysql_connection ( )
            # Check again.
            if not self.check_mysql_connection ( ):
                self.log.error ( "Could not open MySQL connection, aborting." )
                #self.stop ( )
                return

        # Check config is good.
        if not self.check_tables ( ):
            # Try to reconfigure.
            self.configure_tables ( )
            # check again.
            if not self.check_tables ( ):
                self.log.error ( "Could not configure db tables." )
                self.stop ( )
                return

        while not self.shutdown:
            self.log.debug ( "Starting database loop." )
            time.sleep ( 1 )

            if not self.connection:
                self.log.warning ( "Connection became None during runtime." )
                #self.stop ( )

            self.log.setLevel ( self.log_level )

            self.dequeue ( )

        self.close_mysql_connection ( )
            
        self.log.debug ( "<%s>" % ( sys._getframe ( ).f_code.co_name ) )

    def stop ( self ):
        self.shutdown = True
        self.close_mysql_connection ( )

    # Connection methods.

    def check_mysql_connection ( self ):
        if not self.connection:
            return False
        return True

    def close_mysql_connection ( self ):
        if self.check_mysql_connection ( ):
            self.connection.close ( )
            self.connection = None

    def open_mysql_connection ( self ):
        try:
            self.connection = pymysql.connect ( host        = 'localhost',
                                                user        = 'tuna',
                                                passwd      = 'tuna',
                                                db          = 'tuna',
                                                charset     = 'utf8mb4',
                                                cursorclass = pymysql.cursors.DictCursor )
        except Exception as e:
            self.log.error ( "Exception during MySQL connection open: {}.".format ( e ) )
            self.connection = None
        self.log.debug ( "MySQL connection opened." )

    # Config methods. They suppose connection is fine.

    def check_tables ( self ):
        try:
            cursor = self.connection.cursor ( )
            cursor.execute ( "show tables" )
            self.connection.commit ( )
            result = cursor.fetchall ( )
        except Exception as e:
            self.log.error ( "Exception during check_tables: {}.".format ( e ) )
            return False
        result_tables = [ ]
        for entry in result:
            for key in entry.keys ( ):
                result_tables.append ( entry [ key ] )
        expected_tables = list ( self.expected_tables.keys ( ) )
        if sorted ( result_tables ) != sorted ( expected_tables ):
            self.log.debug ( "Tables in db '{}' differ from the expected '{}'!".format ( result,
                                                                                         expected_tables ) )
            return False
        return True

    def configure_tables ( self ):
        """
        If the db is empty, populate it with a structure defined in self.expected_tables.
        """
        try:
            cursor = self.connection.cursor ( )
            cursor.execute ( "show tables" )
            self.connection.commit ( )
            result = cursor.fetchall ( )
        except Exception as e:
            self.log.error ( "Exception during configure_tables: {}.".format ( e ) )
            return
            
        if result != ( ):
            self.log.error ( "Database '{}' is not empty AND is different from expected!".format ( result ) )
            return

        for table in self.expected_tables.keys ( ):
            try:
                cursor.execute ( "create table {} {}".format ( table, self.expected_tables [ table ] ) )
                self.connection.commit ( )
            except Exception as e:
                self.log.error ( "Exception during table creation: {}.".format ( e ) )

    # Data methods. They suppose connection and tables are valid.

    def insert_record ( self, table, columns_values, attempt = 0 ):
        """
        Enqueues request to insert_record_processor.
        """
        self.enqueue ( { 'function' : self.insert_record_processor,
                         'args' : ( table, columns_values ),
                         'kwargs' : { 'attempt' : attempt } } )
        
    def insert_record_processor ( self, table, columns_values, attempt = 0 ):
        """
        columns_values must be a dict with columns as keys.
        """
        if attempt > 10:
            self.log.info ( "Failing db action due to excessive attempts." )
            return

        columns_string = "( "
        for column in columns_values.keys ( ):
            if columns_string != "( ":
                columns_string += ", "
            columns_string += str ( column )
        columns_string += " )"
        self.log.debug ( "columns_string = '{}'.".format ( columns_string ) )

        for key in columns_values.keys ( ):
            entry = columns_values [ key ]
            try:
                values_string += ", '{}'".format ( entry )
            except UnboundLocalError:
                values_string = "'{}'".format ( entry )
        values_string = "( " + values_string + " )"

        self.log.debug ( "values_string = '{}'.".format ( values_string ) )

        cursor = self.connection.cursor ( )
        try:
            sql = "insert into {} {} values {}".format ( table, 
                                                         columns_string,
                                                         values_string )
            self.log.debug ( "sql = '{}'.".format ( sql ) )
            cursor.execute ( sql )
            self.connection.commit ( )
        except BrokenPipeError as e:
            self.log.error ( "BrokenPipeError during insert: '{}'.".format ( e ) )
            self.framework.shutdown = True
            return
        except pymysql.err.OperationalError:
            self.log.info ( "Trying to recover insert_record recursively (attemp #{}). sql = '{}'".format (
                attempt + 1, sql ) )
            return self.insert_record ( table, columns_values, attempt + 1 )
        except pymysql.err.IntegrityError:
            self.log.info ( "Trying to recover insert_record by calling update instead (attemp #{}). sql = '{}'".format ( attempt + 1, sql ) )
            return self.update_record ( table, columns_values, attempt + 1 )
        except Exception as e:
            self.log.error ( "Exception during insert_record: {}, sys.exc_info() = '{}'. sql = '{}'".format (
                e, sys.exc_info ( ), sql ) )
            return
        
    def select_record ( self, table, columns_values, attempt = 0 ):
        """
        columns_values must be a dict with columns as keys.
        """
        if attempt > 10:
            self.log.info ( "Failing db action due to excessive attempts." )
            return
        
        for key in columns_values.keys ( ):
            try:
                where_string += " and {} = '{}'".format ( key, columns_values [ key ] )
            except UnboundLocalError:
                where_string = "{} = '{}'".format ( key, columns_values [ key ] )
                continue

        cursor = self.connection.cursor ( )
        try:
            sql = "select * from {} where {}".format ( table, 
                                                         where_string )
            self.log.debug ( "sql = '{}'.".format ( sql ) )
            cursor.execute ( sql )
            self.connection.commit ( )
            res = cursor.fetchall ( )
            self.log.debug ( "res = {}".format ( res ) )
            if len ( res ) == 0:
                return None
            return res [ 0 ]
        except pymysql.err.OperationalError:
            self.log.info ( "Trying to recover select_record recursively (attemp #{}).".format ( attempt + 1 ) )
            return self.select_record ( table, columns_values, attempt + 1 )
        except Exception as e:
            self.log.error ( "Exception during select_record: {}, sys.exc_info() = '{}'.".format (
                e, sys.exc_info ( ) ) )
            return None

    def update_record ( self, table, columns_values, attempt = 0 ):
        """
        Enqueues request to update_record_processor.
        """
        self.enqueue ( { 'function' : self.update_record_processor,
                         'args' : ( table, columns_values ),
                         'kwargs' : { 'attempt' : attempt } } )
        
    def update_record_processor ( self, table, columns_values, attempt = 0 ):
        """
        columns_values must be a dict with columns as keys.
        """
        if attempt > 10:
            self.log.info ( "Failing update_record due to excessive attempts." )
            return
                
        for key in columns_values.keys ( ):
            if key == "hash":
                continue
            try:
                update_string += ", {} = '{}'".format ( key, columns_values [ key ] )
            except UnboundLocalError:
                update_string = "{} = '{}'".format ( key, columns_values [ key ] )
                continue

        where_string = "hash = '{}'".format ( columns_values [ 'hash' ] )

        cursor = self.connection.cursor ( )
        try:
            sql = "update {} set {} where {}".format ( table, 
                                                       update_string,
                                                       where_string )
            self.log.debug ( "sql = '{}'.".format ( sql ) )
            cursor.execute ( sql )
            self.connection.commit ( )
            res = cursor.fetchall ( )
            if len ( res ) == 0:
                return None
            return res [ 0 ]
        except pymysql.err.OperationalError:
            self.log.info ( "Trying to recover update_record recursively (attemp #{}).".format ( attempt + 1 ) )
            return self.update_record ( table, columns_values, attempt + 1 )
        except Exception as e:
            self.log.error ( "Exception during update_record: {}, sys.exc_info() = '{}'. sql = '{}'".format (
                e, sys.exc_info ( ), sql ) )
            return None

    # queue
           
    def enqueue ( self, data ):
        self.log.debug ( "enqueue: {}.".format ( data ) )
        self.queue_lock.get ( )
        self.queue.append ( data )
        self.queue_lock.let ( )

    def dequeue ( self ):
        self.queue_lock.get ( )
        data = None
        if len ( self.queue ) > 0:
            data = self.queue.pop ( )
        self.queue_lock.let ( )
        if data:
            self.log.debug ( "dequeue: {}.".format ( data ) )
            self.process ( data )

    def process ( self, data ):
        data [ 'function' ] ( *data [ 'args' ], **data [ 'kwargs' ] )
