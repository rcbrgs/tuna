"""
This module's scope are database operations.
"""

import logging
import pymysql
import sys
import threading
import time
import traceback
import tuna

class database ( threading.Thread ):
    """
    This class' responsibilities are creating and maintaining a connection to a system's MySQL database. It is also the gateway through which queries are to be made.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    This module is part of the "guts" of Tuna and is not meant as a user-serviceable module.
    """
    def __init__ ( self ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.12"
        self.changelog = {
            '0.1.12' : "Tuna 0.13.0: Updated documentation to new style.",
            '0.1.11' : "Added docstrings.",
            '0.1.10' : "Added a connection check before selecting a record.",
            '0.1.9' : "Added cursor.close calls in several points.",
            '0.1.8' : "Added a traceback print in exception handler for select_record.",
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
        """
        This method is required by :ref:`threading_label`, which allows parallel exection in a separate thread.

        This method's goal is to connect to a MySQL daemon, verify that it has the appropriate tables and keep the connection open until the object is stopped.
        """
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
        """
        This method's goal is to initiate a shutdown sequence of the object, which will disconnect from the MySQL daemon and stop the thread.
        """
        self.shutdown = True
        self.close_mysql_connection ( )

    # Connection methods.

    def check_mysql_connection ( self ):
        """
        This method's goal is to verify that the connection to the database manager is working.

        Returns:
        
        unnamed variable : bool
            This value corresponds to the self.connection object being None or existing.
        """
        if self.connection == None:
            return False
        return True

    def close_mysql_connection ( self ):
        """
        This method's goal is to close the connection to the database manager.
        """
        if self.check_mysql_connection ( ):
            self.connection.close ( )
            self.connection = None

    def open_mysql_connection ( self ):
        """
        This method's goal is to connect to the database manager. Which should reside on the 'localhost', have a database 'tuna' and a user 'tuna' that has all rights on the database 'tuna', using the password 'tuna'.
        """
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
        """
        This method's goal is to verify that the database connected to contains the proper tables for running Tuna.
        """
        try:
            cursor = self.connection.cursor ( )
            cursor.execute ( "show tables" )
            self.connection.commit ( )
            result = cursor.fetchall ( )
            cursor.close ( )
        except Exception as e:
            self.log.error ( tuna.console.output_exception ( e ) )
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
        This method's goal is to populate an empty database with a structure defined in self.expected_tables.
        """
        try:
            cursor = self.connection.cursor ( )
            cursor.execute ( "show tables" )
            self.connection.commit ( )
            result = cursor.fetchall ( )
            cursor.close ( )
        except Exception as e:
            self.log.error ( tuna.console.output_exception ( e ) )
            return
            
        if result != ( ):
            self.log.error ( "Database '{}' is not empty AND is different from expected!".format ( result ) )
            return

        for table in self.expected_tables.keys ( ):
            try:
                cursor = self.connection.cursor ( )
                cursor.execute ( "create table {} {}".format ( table, self.expected_tables [ table ] ) )
                self.connection.commit ( )
                cursor.close ( )
            except Exception as e:
                self.log.error ( tuna.console.output_exception ( e ) )

    # Data methods. They suppose connection and tables are valid.

    def insert_record ( self, table, columns_values ):
        """
        This method's goal is to enqueue a request to self.insert_record_processor ( ).

        Parameters:

        * table : string
            Must contain a name for a valid table on the database.
        * columns_values : dictionary
            A dictionary where keys must contain valid column identifiers for the specified table, and the dictionary values must be valid values of the type the database specifies for that column, in that table.
        """
        self.enqueue ( { 'function' : self.insert_record_processor,
                         'args' : ( table, columns_values ),
                         'kwargs' : { } } )
        
    def insert_record_processor ( self, table, columns_values ):
        """
        This method's goal is to process a insert statement in the database manager. 

        Parameters:

        * table : string
            Must contain a name for a valid table on the database.
        * columns_values : dictionary
            A dictionary where keys must contain valid column identifiers for the specified table, and the dictionary values must be valid values of the type the database specifies for that column, in that table.
        """
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
        sql = "insert into {} {} values {}".format ( table, 
                                                     columns_string,
                                                     values_string )
        cursor = self.connection.cursor ( )
        self.log.debug ( "sql = '{}'.".format ( sql ) )
        cursor.execute ( sql )
        self.connection.commit ( )
        cursor.close ( )
        
    def select_record ( self, table, columns_values ):
        """
        This method's goal is to process a select statement in the database manager.

        Parameters:

        * table : string
            Must contain a name for a valid table on the database.
        * columns_values : dictionary
            A dictionary where keys must contain valid column identifiers for the specified table, and the dictionary values must be valid values of the type the database specifies for that column, in that table.

        Returns:

        * unnamed variable : list
            The same structure as returned by pymysql.cursor.fetchall ( ).
        * unnamed variable : bool
            Will be True if the connection is open, and data was retrieved without raising an exception. Otherwise, will return False.
        """
        for key in columns_values.keys ( ):
            try:
                where_string += " and {} = '{}'".format ( key, columns_values [ key ] )
            except UnboundLocalError:
                where_string = "{} = '{}'".format ( key, columns_values [ key ] )
                continue
        sql = "select * from {} where {}".format ( table, 
                                                   where_string )
        self.log.debug ( "sql = '{}'.".format ( sql ) )

        if not self.check_mysql_connection ( ):
            self.log.error ( "No SQL connection during select, aborting." )
            return None, False
        
        try:
            cursor = self.connection.cursor ( )
            cursor.execute ( sql )
            self.connection.commit ( )
            res = cursor.fetchall ( )
            self.log.debug ( "res = {}".format ( res ) )
            cursor.close ( )
            return res, True
        except Exception as e:
            self.log.error ( tuna.console.output_exception ( e ) )
            return None, False

    def update_record ( self, table, columns_values ):
        """
        This method's goal is to enqueue a request to update_record_processor ( ).

        Parameters:

        * table : string
            Must contain a name for a valid table on the database.
        * columns_values : dictionary
            A dictionary where keys must contain valid column identifiers for the specified table, and the dictionary values must be valid values of the type the database specifies for that column, in that table.
        """
        self.enqueue ( { 'function' : self.update_record_processor,
                         'args' : ( table, columns_values ),
                         'kwargs' : { } } )
        
    def update_record_processor ( self, table, columns_values ):
        """
        This method's goal is to process an update statement in the database manager.

        Parameters:

        * table : string
            Must contain a name for a valid table on the database.
        * columns_values : dictionary
            A dictionary where keys must contain valid column identifiers for the specified table, and the dictionary values must be valid values of the type the database specifies for that column, in that table.
        """
        for key in columns_values.keys ( ):
            if key == "hash":
                continue
            try:
                update_string += ", {} = '{}'".format ( key, columns_values [ key ] )
            except UnboundLocalError:
                update_string = "{} = '{}'".format ( key, columns_values [ key ] )
                continue

        where_string = "hash = '{}'".format ( columns_values [ 'hash' ] )
        sql = "update {} set {} where {}".format ( table, 
                                                   update_string,
                                                   where_string )
        self.log.debug ( "sql = '{}'.".format ( sql ) )

        cursor = self.connection.cursor ( )
        cursor.execute ( sql )
        self.connection.commit ( )
        res = cursor.fetchall ( )
        cursor.close ( )
        if len ( res ) == 0:
            return None
        return res [ 0 ]

    # queue
           
    def enqueue ( self, data ):
        """
        This method's goal is to add a request to the queue.

        Parameters:

        * data : dictionary
            Must contain valid entries for the following keys: function, args and kwargs.
        """
        self.log.debug ( "enqueue: {}.".format ( data ) )
        self.queue_lock.get ( )
        self.queue.append ( data )
        self.queue_lock.let ( )

    def dequeue ( self ):
        """
        This method's goal is to pop the first entry on the query queue, and attempt to process it.
        """
        self.queue_lock.get ( )
        data = None
        if len ( self.queue ) > 0:
            data = self.queue.pop ( )
        self.queue_lock.let ( )
        if data:
            self.log.debug ( "dequeue: {}.".format ( data ) )
            self.process ( data )

    def process ( self, data ):
        """
        This method's goal is to process a query request.

        Parameters:

        * data : dictionary
            Must contain valid entries for the following keys: function, args and kwargs.
        """
        
        try:
            data [ 'function' ] ( *data [ 'args' ], **data [ 'kwargs' ] )
        except Exception as e:
            self.log.error ( tuna.console.output_exception ( e ) )
