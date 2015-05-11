import logging

def set_path ( file_name ):
    log = logging.getLogger ( __name__ )
    log.setLevel ( logging.DEBUG )

    if not isinstance ( file_name, str ):
        log.error ( "Non-string passed as file_name." )
        return

    
