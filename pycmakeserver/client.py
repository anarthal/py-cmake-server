
from .protocol import CmakeProtocol
from .message_handler import MessageHandler

class CmakeClient(object):
    def __init__(self, loop, src_dir, build_dir, generator='Unix Makefiles', on_signal=None):
        # TODO: inject handler and protocol factory
        self._loop = loop
        self._proto = None
        self._message_handler = MessageHandler(loop, src_dir, build_dir, generator, on_signal)
  
    async def connect(self, pipe):
        def protocol_factory():
            return CmakeProtocol(self._message_handler)
        _, self._proto = await self._loop.create_unix_connection(protocol_factory, pipe)
        await self._message_handler.wait_for_connected()
        
    async def disconnect(self):
        self._proto.close()
        await self._message_handler.wait_for_disconnected()

    
    async def global_settings(self):
        return await self._message_handler.request_reply({'type': 'globalSettings'})

    async def set_global_settings(self, args):
        msg = args.copy()
        msg['type'] = 'setGlobalSettings'
        await self._message_handler.request_reply(msg)
    
    # TODO: support for cache arguments
    async def configure(self, on_progress=None, on_message=None):
        await self._message_handler.request_reply({'type': 'configure'}, on_progress, on_message)

    async def compute(self, on_progress=None, on_message=None):
        await self._message_handler.request_reply({'type': 'compute'}, on_progress, on_message)

    async def codemodel(self):
        return await self._message_handler.request_reply({'type': 'codemodel'})

    async def cmake_inputs(self):
        return await self._message_handler.request_reply({'type': 'cmakeInputs'})

    async def cache(self):
        return await self._message_handler.request_reply({'type': 'cache'})

    async def filesystem_watchers(self):
        return await self._message_handler.request_reply({'type': 'fileSystemWatchers'})
    
    # TODO: support for ctestinfo

