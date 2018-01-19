"""This module's scope covers operations related to underlying system where Tuna
is running.
"""
__version__ = "0.1.1"
__changelog = {
    "0.1.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.0": {"Tuna": "0.14.0", "Change": "updated dosctrings to new style."}
}

def status ( ):
    """
    This method's goal is to report the current amount of memory available on 
    the system.

    Returns:

    unnamed variable : string
        "XGb of RAM memory are available.", where X is substituted by the 
        current amount.
    """
    import psutil
    return str(int(psutil.virtual_memory().available / (1024 * 1024 * 1024))) \
        + "Gb of RAM memory are available."
