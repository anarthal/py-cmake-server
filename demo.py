
import asyncio
from pycmakeserver import CmakeClient
from pprint import pprint
from os import path

# Will be called for cmake 'messages', sent while configure and compute
def message_cb(msg):
    print('Received message: {}'.format(msg))

# Will be called for cmake progress reports, sent while configure and compute 
def progress_cb(msg):
    print('Received progress: {}'.format(msg))
    
# Note: coroutine
async def async_main(loop):
    # Create a cmake client
    cli = CmakeClient(
        loop,
        path.abspath('demo'), # Absolute path to the project (where the root CMakeLists.txt is)
        '/tmp/build', # Build directory
        'Unix Makefiles', # The cmake generator
        lambda msg: pprint(msg) # Will be called on cmake signals (ej. if a file changes)
    )
    
    # Connect to cmake server
    # Pass in the pipe where cmake is waiting; should be the value passed to --pipe
    await cli.connect('/tmp/pipe')
    
    try:
        # Get settings like the cmake version, the available generators...
        pprint(await cli.global_settings())
        
        # Set one of the above settings; this one will trigger a more verbose cmake build
        #await cli.set_global_settings({'debugOutput': True})
    
        # Start the configuration process; callbacks will be called
        # to report the state of the configuration process
        await cli.configure(progress_cb, message_cb)
        
        # Generate the build system files (e.g. the Makefiles); you may also
        # pass callbacks here
        await cli.compute()
        
        # Get the code model. This contains a summary of the project structure
        # as known to cmake. codemodel() requires a previous compute()
        pprint(await cli.codemodel())
        
        # Get all the variables in the cmake cache
        pprint(await cli.cache())
    finally:
        await cli.disconnect()
    
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(loop))
    finally:
        loop.close()
        
if __name__ == '__main__':
    main()
    