
import protocol

class CmakeClient(object):
    def __init__(self, loop):
        self._loop = loop
        self._proto = None
        self._transport = None
  
    async def connect(self, pipe, src_dir, build_dir, generator='Unix Makefiles'):
        def protocol_factory():
            return protocol.CmakeClientProtocol(self._loop, src_dir, build_dir, generator)
        temp = await self._loop.create_unix_connection(protocol_factory, pipe)
        self._transport, self._proto = temp
        return await self._proto.connected.wait()
        
    async def disconnect(self):
        self._transport.close()
        await self._proto.disconnected.wait()

    
    async def global_settings(self):
        return await self._proto.request_reply({'type': 'globalSettings'})

    async def set_global_settings(self, args):
        msg = args.copy()
        msg['type'] = 'setGlobalSettings'
        await self._proto.request_reply(msg)
    
    async def configure(self, on_progress=None, on_message=None):
        await self._proto.request_reply({'type': 'configure'}, on_progress, on_message)

    async def compute(self, on_progress=None, on_message=None):
        await self._proto.request_reply({'type': 'compute'}, on_progress, on_message)

    async def codemodel(self):
        return await self._proto.request_reply({'type': 'codemodel'})

    async def cmake_inputs(self):
        return await self._proto.request_reply({'type': 'cmakeInputs'})

    async def cache(self):
        return await self._proto.request_reply({'type': 'cache'})

    async def filesystem_watchers(self):
        return await self._proto.request_reply({'type': 'fileSystemWatchers'})

