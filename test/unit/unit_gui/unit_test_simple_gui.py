import unittest
#import sys
#sys.path.append ( '/home/nix/sync/tuna/github' )

class unit_test_tuna_simple_gui ( unittest.TestCase ):
    def setUp ( self ):
        pass

    def test_dock_widget ( self ):
        # dock can be created
        mock_simple_gui = unittest.mock.MagicMock ( )
        # dock can be hidden
        # dock can be moved
        # dock can be restored
        # dock can be destroyed
        pass

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
