import inspect
import logging
import time
import tuna

class lock ( object ):
    """
    Object to mediate access to resource from competing threads.
    """
    def __init__ ( self ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        self.__version__ = '0.1.0'
        self.changelog = {
            '0.1.0'  : "Added changelog, logging."
            }
        
        self.callee  = None
        self.timeout = 10

    def get ( self ):
        """
        Returns the lock to the requestor. If the lock is set, will block the call until the lock is unset, or the timeout elapses.
        """
        callee = inspect.stack ( ) [ 1 ] [ 0 ].f_code.co_name
        begin = time.time ( )
        while ( self.callee != None and
                self.callee != callee ):
            if time.time ( ) - begin > self.timeout:
                break
            time.sleep ( 0.1 )
        self.callee = callee
        self.log.debug ( "callee set to {}.".format ( self.callee ) )

    def let ( self ):
        """
        Unlocks this lock. Since a timeout may have released this lock before it is properly unlocked, a warning is sent to the log facility, so the user may adjust its code.
        """
        callee = inspect.stack ( ) [ 1 ] [ 0 ].f_code.co_name
        if self.callee != callee:
            self.log.warning ( "let called from non-callee!" )
            return
        callee = None
        self.log.debug ( "callee set to None." )
