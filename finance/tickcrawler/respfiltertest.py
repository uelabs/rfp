import respfilter
import aiohttp
import asyncio

def fetchPage(url):
    resp = yield from aiohttp.request('get', url)
    body = yield from resp.read()
    return (url, body, resp.headers)

@asyncio.coroutine
def my_coro():
    count = 0
    try:
        tupl = yield
        print(tupl[0])
    except (GeneratorExit, StopIteration):
        return count

fltr = respfilter.HttpResponseTypeFilter(my_coro())
fcoro = fltr.do_filter()
fcoro.send(None)
fut1 = asyncio.async(fetchPage('http://hopey.netfonds.no/posdump.php?csv_format=txt&date=20150116&paper=ACHC.O&'))
fut2 = asyncio.async(fetchPage('http://hopey.netfonds.no/posdump.php?csv_format=txt&date=20150116&paper=FCCY.O&'))
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([fut1, fut2]))
tupl1 = fut1.result()
tupl2 = fut2.result()
try:
    fcoro.send(tupl1)
    fcoro.send(tupl2)
except:
    pass
