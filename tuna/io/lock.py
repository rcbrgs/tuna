"""This module's scope covers operations related to mutexes, especially locks.
"""
__version__ = '0.1.2'
__changelog = {
    "0.1.2": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.1": {"Tuna": "0.14.0", "Change": "improved docstrings."},
    "0.1.1": {"Change": "Added changelog, logging."}
}

import inspect
import logging
import time
import tuna

class Lock(object):
    """This class' responsibility is to provide a lock mechanism to mediate access to resource from competing threads.

    It is not meant to be user-serviceable.
    """
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        
        self.callee  = None
        self.timeout = 10

    def get(self):
        """
        This method's goal is to give the lock to the requestor. If the lock is
        set, will block the call until the lock is unset, or the timeout 
        elapses.
        """
        callee = inspect.stack()[1][0].f_code.co_name
        begin = time.time()
        while(self.callee != None and
              self.callee != callee):
            if time.time() - begin > self.timeout:
                break
            time.sleep(0.1)
        self.callee = callee
        self.log.debug("callee set to {}.".format(self.callee))

    def let(self):
        """
        This method's goal is to unlocks the lock. Since a timeout may have 
        released this lock before it is properly unlocked, a warning is sent to
        the log facility, so the user may adjust the relevant code.
        """
        callee = inspect.stack()[1][0].f_code.co_name
        if self.callee != callee:
            self.log.warning("let called from non-callee!")
            return
        callee = None
        self.log.debug("callee set to None.")
