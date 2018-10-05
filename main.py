
import json
import asyncio
import client
import pprint
     
async def async_main(loop):
    cli = client.CmakeClient(loop)
    await cli.connect(
        '/tmp/pipe',
        '/home/ruben/workspace/cmakeserver/myproj',
        '/tmp/build',
        'Unix Makefiles'
    )

    await cli.configure()
    await cli.compute()
    pprint.pprint(await cli.filesystem_watchers())
    await cli.disconnect()
    
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(loop))
    finally:
        loop.close()
        
if __name__ == '__main__':
    main()
    