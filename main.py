
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
    i = 0
    while True:
        i += 1
        if i % 2:
            pprint.pprint(await cli.filesystem_watchers())
        else:
            pprint.pprint(await cli.global_settings())
        await asyncio.sleep(0.5, loop=loop)
    await cli.disconnect()
    
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(loop))
    finally:
        loop.close()
        
if __name__ == '__main__':
    main()
    