
import asyncio
import client
import pprint

def message_cb(msg):
    print('Received message: {}'.format(msg))
    
def progress_cb(msg):
    print('Received progress: {}'.format(msg))
     
async def async_main(loop):
    cli = client.CmakeClient(loop)
    await cli.connect(
        '/tmp/pipe',
        '/home/ruben/workspace/cmakeserver/myproj',
        '/tmp/build',
        'Unix Makefiles'
    )

    #await cli.configure(progress_cb, message_cb)
    #await cli.compute()
    await cli.codemodel()
    await cli.disconnect()
    
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(loop))
    finally:
        loop.close()
        
if __name__ == '__main__':
    main()
    