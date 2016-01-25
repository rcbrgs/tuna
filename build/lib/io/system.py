"""
This module's scope covers operations related to underlying system where Tuna is running.
"""

def status ( ):
    """
    This method's goal is to report the current amount of memory available on the system.

    Returns:

    unnamed variable : string
        "XGb of RAM memory are available.", where X is substituted by the current amount.
    """
    __version__ = "0.1.0"
    changelog = {
        "0.1.0" : "Tuna 0.14.0 : updated dosctrings to new style."
        }
    import psutil
    return str ( int ( psutil.virtual_memory ( ).available / ( 1024 * 1024 * 1024 ) ) ) + "Gb of RAM memory are available."
