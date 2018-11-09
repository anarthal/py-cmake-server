import asyncio
import json

class InvalidMessageHeadError(Exception):
    pass

class CmakeProtocol(asyncio.Protocol):
    _MSG_HEAD = b'\n[== "CMake Server" ==[\n'
    _MSG_TAIL = b'\n]== "CMake Server" ==]\n'
    def __init__(self, message_handler):
        self._buffer = b''
        self._transport = None
        self.message_handler = message_handler
        self.message_handler.protocol = self
       
    def connection_made(self, transport):
        asyncio.Protocol.connection_made(self, transport)
        self._transport = transport
        print('Connection made')
        
    def connection_lost(self, exc):
        asyncio.Protocol.connection_lost(self, exc)
        print('Connection lost: {}'.format(exc))
        self.message_handler.connection_lost(exc)
        
    def data_received(self, data):
        asyncio.Protocol.data_received(self, data)
        print('RX << {}'.format(data))
        self._buffer += data
        try:
            self._process_new_data()
        except (json.JSONDecodeError, InvalidMessageHeadError) as err:
            print('WARNING: error while processing data, discarding fragment')
            print('{}: {}'.format(type(err).__name__, err))
            self._buffer = b''
        
    def write(self, msg):
        tx = self._MSG_HEAD + json.dumps(msg).encode('utf_8') + self._MSG_TAIL
        print('TX >> {}'.format(tx))
        self._transport.write(tx)
    
    def close(self):
        self._transport.close()
        
    def _process_new_data(self):
        while True:
            if len(self._buffer) < len(self._MSG_HEAD):
                return
            if not self._buffer.startswith(self._MSG_HEAD):
                raise InvalidMessageHeadError(str(self._buffer[:len(self._MSG_HEAD)]))
            idx = self._buffer.find(self._MSG_TAIL)
            if idx == -1:
                return
            chunk = self._buffer[len(self._MSG_HEAD):idx]
            msg = json.loads(chunk)
            self.message_handler.handle(msg)
            self._buffer = self._buffer[idx + len(self._MSG_TAIL):]
        
