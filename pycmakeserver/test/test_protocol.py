from unittest import TestCase, mock
from pycmakeserver.protocol import CmakeProtocol

class CmakeProtocolTest(TestCase):
    def setUp(self):
        self.handler = mock.Mock(['handle', 'connection_lost'])
        self.proto = CmakeProtocol(self.handler)
    
    # coonnection_lost
    def test_connection_lost_calls_handler_connection_lost(self):
        err = Exception('myerror')
        self.proto.connection_lost(err)
        self.handler.connection_lost.assert_called_once_with(err)
    
    # data_received success cases
    def test_data_received_exactly_one_msg_decodes_calls_handler_handle(self):
        data = b'''\n[== "CMake Server" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n'''
        self.proto.data_received(data)
        self.handler.handle.assert_called_once_with({'type': 'hello'})
        
    def test_data_received_message_in_two_pieces_decodes_calls_handle(self):
        data = b'''\n[== "CMake Server" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n'''
        self.proto.data_received(data[:10])
        self.proto.data_received(data[10:])
        self.handler.handle.assert_called_once_with({'type': 'hello'})
        
    def test_data_received_two_messages_at_once_decodes_calls_handle_for_the_two(self):
        data = b'''\n[== "CMake Server" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n\n[== "CMake Server" ==[\n
            { "type": "signal" }
            \n]== "CMake Server" ==]\n'''
        self.proto.data_received(data)
        expected_calls = [
            mock.call({'type': 'hello'}),
            mock.call({'type': 'signal'})
        ]
        self.assertEqual(self.handler.handle.mock_calls, expected_calls)
        
    def test_data_received_complete_message_and_incomplete_calls_handle_retains_incomplete(self):
        data0 = b'''\n[== "CMake Server" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n\n[== "CMake Server" ==[\n'''
        data1 = b'''{ "type": "signal" }
            \n]== "CMake Server" ==]\n'''
        self.proto.data_received(data0)
        self.proto.data_received(data1)
        expected_calls = [
            mock.call({'type': 'hello'}),
            mock.call({'type': 'signal'})
        ]
        self.assertEqual(self.handler.handle.mock_calls, expected_calls)

    
    # data received
    #   Bad message (does not start with adequate prefix)
    #   Bad message (error decoding UTF8)
    #   Bad message (cannot find termination in a reasonable message size)
    #   Bad message (not a JSON)
    # write => writes prefix, suffix, serializes, writes to transport
    # close => Calls transport close