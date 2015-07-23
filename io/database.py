import logging
import pymysql
import sys
import threading
import time

class database ( threading.Thread ):
    def __init__ ( self ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.1"
        self.changelog = {
            '0.1.1' : "Refactored to use table definitions from a single variable.",
            '0.1.0' : "Initial version."
        }
        self.log = logging.getLogger ( __name__ )
        self.log_level = logging.INFO
        self.daemon = True

        self.connection = None
        self.expected_tables = {
            'datasets' : "( hash varchar ( 20 ) primary key )"
            }

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
            time.sleep ( self.framework.preferences.loop_wait )

            # STARTMOD

            if not self.connection:
                self.log.warning ( "Connection became None during runtime." )
                #self.stop ( )
            
            # ENDMOD                             

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
        self.log.info ( "MySQL connection opened." )

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
            self.log.error ( "Tables in db '{}' differ from the expected '{}'!".format ( result,
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
            self.log.error ( "db '{}' is not empty!".format ( result ) )
            return

        for table in self.expected_tables.keys ( ):
            try:
                cursor.execute ( "create table {} {}".format ( table, self.expected_tables [ table ] ) )
                self.connection.commit ( )
            except Exception as e:
                self.log.error ( "Exception during table creation: {}.".format ( e ) )

    # Data methods. They suppose connection and tables are valid.

    def insert_record ( self, table, columns_values ):
        """
        columns_values must be a dict with columns as keys.
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
                values_string += ", {}".format ( entry )
            except UnboundLocalError:
                values_string = "{}".format ( entry )
        values_string = "( " + values_string + " )"

        self.log.info ( "values_string = '{}'.".format ( values_string ) )

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
        except Exception as e:
            self.log.error ( "Exception during insert: {}.".format ( e ) )
            if e == ( 2014, 'Command Out of Sync' ):
                self.log.info ( "Trying to recover resursively." )
                return self.select_record ( table, columns_values )
            return
        
    def select_record ( self, table, columns_values ):
        """
        columns_values must be a dict with columns as keys.
        """
        
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
        except Exception as e:
            self.log.error ( "Exception during select: {}.".format ( e ) )
            if e == ( 2014, 'Command Out of Sync' ):
                self.log.info ( "Trying to recover resursively." )
                return self.select_record ( table, columns_values )
            return None

    def update_record ( self, table, columns_values ):
        """
        columns_values must be a dict with columns as keys.
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
        except Exception as e:
            self.log.error ( "Exception during update: {}.".format ( e ) )
            return None
