import tuna

def get_connected_points ( position, array ):
    to_verify = [ position ]
    verified = [ ]
    value = array [ position [ 0 ] ] [ position [ 1 ] ]

    while ( len ( to_verify ) != 0 ):
        current = to_verify.pop ( )
        if array [ current [ 0 ] ] [ current [ 1 ] ] == value:
            verified.append ( current )
            neighbours = tuna.tools.get_pixel_neighbours ( position, array )
            for neighbour in neighbours:
                if neighbour not in verified:
                    to_verify.append ( neighbour )

    return verified
