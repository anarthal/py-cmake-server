from unittest import TestCase, mock
from pycmakeserver.protocol import CmakeProtocol

class CmakeProtocolTest(TestCase):
    def setUp(self):
        self.handler = mock.Mock(['handle', 'connection_lost'])
        self.proto = CmakeProtocol(self.handler)
        self.hello = b'''\n[== "CMake Server" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n'''
        
    def error_recovery_test(self, data_bad):
        ''' Sends a bad message, then a good one, and asserts for recovery '''
        self.proto.data_received(data_bad)
        self.proto.data_received(self.hello)
        self.handler.handle.assert_called_once_with({'type': 'hello'})
    
    # coonnection_lost
    def test_connection_lost_calls_handler_connection_lost(self):
        err = Exception('myerror')
        self.proto.connection_lost(err)
        self.handler.connection_lost.assert_called_once_with(err)
    
    # data_received success cases
    def test_data_received_exactly_one_msg_decodes_calls_handler_handle(self):
        self.proto.data_received(self.hello)
        self.handler.handle.assert_called_once_with({'type': 'hello'})
        
    def test_data_received_message_in_two_pieces_decodes_calls_handle(self):
        self.proto.data_received(self.hello[:10])
        self.proto.data_received(self.hello[10:])
        self.handler.handle.assert_called_once_with({'type': 'hello'})
        
    def test_data_received_two_messages_at_once_decodes_calls_handle_for_the_two(self):
        additional_data = b'''\n[== "CMake Server" ==[\n
            { "type": "signal" }
            \n]== "CMake Server" ==]\n'''
        self.proto.data_received(self.hello + additional_data)
        expected_calls = [
            mock.call({'type': 'hello'}),
            mock.call({'type': 'signal'})
        ]
        self.assertEqual(self.handler.handle.mock_calls, expected_calls)
        
    def test_data_received_complete_message_and_incomplete_calls_handle_retains_incomplete(self):
        data0 = self.hello + b'''\n[== "CMake Server" ==[\n'''
        data1 = b'''{ "type": "signal" }
            \n]== "CMake Server" ==]\n'''
        self.proto.data_received(data0)
        self.proto.data_received(data1)
        expected_calls = [
            mock.call({'type': 'hello'}),
            mock.call({'type': 'signal'})
        ]
        self.assertEqual(self.handler.handle.mock_calls, expected_calls)
        
    def test_data_received_non_ascii_values_calls_handle(self):
        data = b'''\n[== "CMake Server" ==[\n
            { "type": "\xc3\xa1" }
            \n]== "CMake Server" ==]\n''' # \xc3\xa1 = a accute
        self.proto.data_received(data)
        self.handler.handle.assert_called_once_with({'type': 'á'})

    # data_received error conditions
    def test_data_received_message_does_not_start_with_adequate_prefix_shorter_discards(self):
        data_bad = b'''\n[== "Bad" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n'''
        self.error_recovery_test(data_bad)
        
    def test_data_received_message_does_not_start_with_adequate_prefix_equal_length_discards(self):
        data_bad = b'''\n[== "CMake Serve_" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n'''
        self.error_recovery_test(data_bad)
        
    def test_data_received_message_does_not_start_with_adequate_prefix_longer_discards(self):
        data_bad = b'''\n[== "Invalid Very Long Message Head" ==[\n
            { "type": "hello" }
            \n]== "CMake Server" ==]\n'''
        self.error_recovery_test(data_bad)
        
    def test_data_received_incomplete_prefix_does_not_discard(self):
        # Bad prefix recovery should not discard good but incomplete prefixes
        self.proto.data_received(self.hello[:5]) # Prefix is OK but incomplete
        self.proto.data_received(self.hello[5:])
        self.handler.handle.assert_called_once_with({'type': 'hello'})
        
    def test_data_received_invalid_utf8_discards(self):
        data_bad = b'''\n[== "CMake Server" ==[\n
            { "type": "\9cinvalid" }
            \n]== "CMake Server" ==]\n'''
        self.error_recovery_test(data_bad)
        
    def test_data_received_invalid_json_discards(self):
        data_bad = b'''\n[== "CMake Server" ==[\n
            { "type": "hello" ]
            \n]== "CMake Server" ==]\n'''
        self.error_recovery_test(data_bad)
    
    # write => writes prefix, suffix, serializes, writes to transport
    # close => Calls transport close