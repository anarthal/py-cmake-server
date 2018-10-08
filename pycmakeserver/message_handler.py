import asyncio
from .errors import CommunicationError, ErrorReply

class MessageHandler(object):
    def __init__(self, loop, src_dir, build_dir, generator, on_signal=None):
        self._loop = loop
        self._connected = asyncio.Event(loop=loop)
        self._disconnected = asyncio.Event(loop=loop)
        self._outstanding_req = {}
        self._current_cookie = 0
        self._is_closing = False # TODO: this flag is better in protocol
        
        self.protocol = None
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.generator = generator
        self.on_signal = on_signal
  
    def connection_lost(self, exc):
        # Order here is important: prevent deadlocks
        self._is_closing = True
        for elm in self._outstanding_req.items():
            # TODO: improve this diagnostic
            elm[0].set_exception(CommunicationError('Connection lost'))
        
        self._connected.clear()
        self._disconnected.set()
        
    def handle(self, msg):
        msg_type = msg['type']
        if msg_type == 'hello':
            self._is_closing = False
            asyncio.ensure_future(self._connect(msg), loop=self._loop)
        elif msg_type == 'signal':
            self._invoke(self.on_signal, msg)
        else:
            cookie = msg['cookie']
            if msg_type == 'progress':
                self._invoke(self._outstanding_req[cookie][1], msg)
            elif msg_type == 'message':
                self._invoke(self._outstanding_req[cookie][2], msg)
            elif msg_type == 'reply':
                self._outstanding_req.pop(cookie)[0].set_result(msg)
            elif msg_type == 'error':
                exc = ErrorReply(msg['errorMessage'])
                self._outstanding_req.pop(cookie)[0].set_exception(exc)
            else:
                print('Warning: unknown message type: {}'.format(msg_type))

    
    async def request_reply(self, req, on_progress=None, on_message=None):
        # Assign a cookie
        cookie = str(self._current_cookie)
        req['cookie'] = cookie
        self._current_cookie += 1
        
        # Insert into outstanding request dict
        future = self._loop.create_future()
        self._outstanding_req[cookie] = (future, on_progress, on_message)
        
        # Safety check, to prevent deadlocks
        if self._is_closing:
            raise CommunicationError('Client is closing')
        
        # Actually send the data
        self.protocol.write(req)
        
        # Wait for a reply
        return await future
    
    async def wait_for_connected(self):
        await self._connected.wait()
        
    async def wait_for_disconnected(self):
        await self._disconnected.wait()
    
    
    async def _connect(self, hello_msg):
        req = {
            'type': 'handshake',
            'protocolVersion': hello_msg['supportedProtocolVersions'][0],
            'sourceDirectory': self.src_dir,
            'buildDirectory': self.build_dir,
            'generator': self.generator
        }
        await self.request_reply(req)
        
        self._disconnected.clear()
        self._connected.set()
           
    @staticmethod
    def _invoke(cb, msg):
        if cb is not None:
            cb(msg)
        
