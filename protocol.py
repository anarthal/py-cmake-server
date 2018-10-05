import asyncio
import json

class CmakeClientProtocol(asyncio.Protocol):
    _MSG_HEAD = b'\n[== "CMake Server" ==[\n'
    _MSG_TAIL = b'\n]== "CMake Server" ==]\n'
    def __init__(self, loop, src_dir, build_dir, generator='Unix Makefiles'):
        self._data = b''
        self._loop = loop
        self._outstanding_req = {}
        self._current_cookie = 0
        self._transport = None
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.generator = generator
        self.connected = asyncio.Event(loop=loop)
        self.disconnected = asyncio.Event(loop=loop)
        
    def connection_made(self, transport):
        asyncio.Protocol.connection_made(self, transport)
        self._transport = transport
        print('Connection made')
    def connection_lost(self, exc):
        asyncio.Protocol.connection_lost(self, exc)
        self.disconnected.set()
        print('Connection lost: {}'.format(exc))
    def data_received(self, data):
        asyncio.Protocol.data_received(self, data)
        print('RX << {}'.format(data))
        self._data += data
        self._process_new_data()
    
    async def request_reply(self, req, on_progress=None, on_message=None):
        # Assign a cookie
        cookie = str(self._current_cookie)
        req['cookie'] = cookie
        self._current_cookie += 1
        
        # Insert into outstanding request dict
        future = self._loop.create_future()
        self._outstanding_req[cookie] = (future, on_progress, on_message)
        
        # Actually send the data
        self._send(req)
        
        # Wait for a reply
        return await future
    
    async def connect(self, hello_msg):
        req = {
            'type': 'handshake',
            'protocolVersion': hello_msg['supportedProtocolVersions'][0],
            'sourceDirectory': self.src_dir,
            'buildDirectory': self.build_dir,
            'generator': self.generator
        }
        await self.request_reply(req)
        self.connected.set()
        
    def disconnect(self):
        self._transport.close()
        
    def _send(self, msg):
        tx = self.encode(msg)
        print('TX >> {}'.format(tx))
        self._transport.write(tx)
    def _process_new_data(self):
        while True:
            idx = self._data.find(self._MSG_TAIL)
            if idx == -1:
                return
            chunk = self._data[len(self._MSG_HEAD):idx]
            msg = json.loads(chunk)
            self._process_new_message(msg)
            self._data = self._data[idx + len(self._MSG_TAIL):]

    def _process_new_message(self, msg):
        msg_type = msg['type']
        if msg_type == 'hello':
            asyncio.ensure_future(self.connect(msg), loop=self._loop)
        elif msg_type == 'signal':
            # TODO: proper handling here
            print('Signal received: {}'.format(msg))
        elif msg_type == 'reply' or msg_type == 'error':
            cookie = msg['cookie']
            future = self._outstanding_req.pop(cookie)[0]
            future.set_result(msg)
        
    @classmethod
    def encode(cls, obj):
        return cls._MSG_HEAD + json.dumps(obj).encode('utf_8') + cls._MSG_TAIL
    @classmethod
    def decode(cls, msg):
        lbegin = len(cls._MSG_HEAD)
        lend = len(cls._MSG_TAIL)
        body = msg[lbegin:-lend]
        return json.loads(body)
    
