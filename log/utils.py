import logging
import sys
import tuna

def function_header ( ):
    """
    Attempts to log function entry-point capturing relevant debug information.
    """

    line            = sys._getframe ( ).f_back.f_lineno

    function_name   = sys._getframe ( ).f_back.f_code.co_name
    script_file     = sys._getframe ( ).f_back.f_code.co_filename
    variables       = sys._getframe ( ).f_back.f_code.co_varnames

    result = ""
    result += script_file.split ( "/" ) [ -1 ]
    result += ", " + str ( line ) + ": " + function_name + " ( "
    variables_names = ""
    for variable in variables:
        if variables_names == "":
            variables_names += variable
        else:
            variables_names += ", " + variable
    result += variables_names + " )"

    return result

def function_name ( ):
    """
    Returns the name of the caller function.
    """
    return sys._getframe ( ).f_back.f_code.co_name

def line_number ( ):
    """
    Returns the line number from which the caller called this function, for logging purposes.
    """
    return sys._getframe ( ).f_back.f_lineno

def script_name ( ):
    """
    Returns the name of the script currently being processed.
    """
    return sys._getframe ( ).f_back.f_code.co_filename.split ( "/" ) [ -1 ]

def set_path ( file_name ):
    log = logging.getLogger ( __name__ )
    log.setLevel ( logging.INFO )

    if not isinstance ( file_name, str ):
        log.error ( "Non-string passed as file_name." )
        return

    if tuna._log_handler != None:
        tuna._log.removeHandler ( tuna._log_handler )

    tuna._log_handler   = logging.FileHandler ( file_name )
    tuna._log_formatter = logging.Formatter ( fmt = "%(asctime)s %(levelname)5s %(message)s", 
                                              datefmt = '%Y-%m-%d %H:%M:%S' )
    tuna._log_handler.setFormatter ( tuna._log_formatter )
    tuna._log.addHandler ( tuna._log_handler )

    log.info ( "Log file set to %s." % file_name )
