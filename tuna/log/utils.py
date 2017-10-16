"""
This module's scope covers interactions with the logging facilities.
"""
__version__ = "0.1.0"
__changelog__ = {
    "0.1.0" : { "Tuna" : "0.16.0", "Change" : "Fixed setting verbosity on the console would also set it on the file. Added defaults to verbose() parameters, and an 'all' option to the handler_type parameter." }
    }

import logging
import sys
import tuna

def function_header ( ):
    """
    This method's goal is to log function entry-point capturing relevant debug information.

    No parameter is needed, since all relevant information is obtained through the sys Python module.

    Returns:

    * result : string
        Containing the signature of the caller function.
    """

    line            = sys._getframe ( ).f_back.f_lineno

    arguments       = sys._getframe ( ).f_back.f_code.co_argcount
    function_name   = sys._getframe ( ).f_back.f_code.co_name
    script_file     = sys._getframe ( ).f_back.f_code.co_filename
    variables       = sys._getframe ( ).f_back.f_code.co_varnames

    result = ""
    result += script_file.split ( "/" ) [ -1 ]
    result += ", " + str ( line ) + ": " + function_name + " ( "

    if arguments != 0:
        for variable_number in range ( arguments ):
            variable_name = variables [ variable_number ]
            if variable_number == 0:
                variables_string = str ( variables [ 0 ] )
            else:
                variables_string += ", " + str ( variables [ variable_number ] )
            variables_string += " = "
            variables_string += str ( sys._getframe ( ).f_back.f_locals [ variable_name ] )

    result += variables_string + " )"

    return result

def function_name ( ):
    """
    This method's goal is to access the name of the caller function.

    Returns:
    
    * unnamed variable : string
        Containing the function name of the caller.
    """
    return sys._getframe ( ).f_back.f_code.co_name

def line_number ( ):
    """
    This method's goal is to provide the line number from which the caller called this function, for logging purposes.

    Returns:

    * unnamed variable : int
        Containing the line number (in the relevant source file) from which the caller called.
    """
    return sys._getframe ( ).f_back.f_lineno

def script_name ( ):
    """
    This method's goal is to access the name of the script currently being processed.

    Returns:

    * unnamed variable : string
        Containing the name of the command used to start the current session.
    """
    return sys._getframe ( ).f_back.f_code.co_filename.split ( "/" ) [ -1 ]

def set_path ( file_name ):
    """
    This method's goal is to set the path and file name where the log output will be saved.

    Parameters:

    * file_name : string
        Containing a valid path and file name for a text file, where new log entries will be appended.
    """
    log = logging.getLogger ( __name__ )
    log.setLevel ( logging.INFO )

    if not isinstance ( file_name, str ):
        log.error ( "Non-string passed as file_name." )
        return

    new_handler = logging.FileHandler ( file_name )
    new_formatter = logging.Formatter ( fmt = "%(asctime)s %(name)s %(levelname)5s %(message)s", 
                                        datefmt = '%Y-%m-%d %H:%M:%S' )
    new_handler.setFormatter ( new_formatter )
    tuna._log.addHandler ( new_handler )
    tuna._log_handlers.append ( new_handler )

    log.info ( "Log file set to %s." % file_name )

def verbose ( handler_type = "all", verbosity = "WARNING" ):
    """
    This method's goal is to set the specified logging handler type to the specified verbosity.

    Parameters:

    * handler_type : string : "all"
        Can be either "all", "console" or "file".

    * verbosity : string : "WARNING"
        Must be the name of a level from the logging module, such as "DEBUG" or "INFO".
    """
    try:
        level = getattr ( logging, verbosity )
    except:
        print ( "Unrecognized logging level." )
        return

    if handler_type == "all":
        for handler in tuna._log_handlers:
            handler.setLevel ( level )
            print ( "Handler {} set to {}.".format ( handler, level ) )
        return
            
    if handler_type == "console":
        for handler in tuna._log_handlers:
            if isinstance ( handler, logging.StreamHandler ):
                if isinstance ( handler, logging.FileHandler ):
                    continue
                handler.setLevel ( level )
                print ( "Handler {} set to {}.".format ( handler, level ) )
        return
    
    if handler_type == "file":
        for handler in tuna._log_handlers:
            if isinstance ( handler, logging.FileHandler ):
                handler.setLevel ( level )
                print ( "Handler {} set to {}.".format ( handler, level ) )
        return
