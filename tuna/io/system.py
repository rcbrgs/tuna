def status ( ):
    """
    Convenience function that returns the current amount of memory available.
    """
    import psutil
    return str ( int ( psutil.virtual_memory ( ).available / ( 1024 * 1024 * 1024 ) ) ) + "Gb of RAM memory are available."
