import crawler
import asyncio

@asyncio.coroutine
def my_coro():
    while True:
        resp = (yield)
        print(resp)

c = crawler.HttpCrawler(my_coro())
coro = c.fetch()
coro.send(None)
coro.send({'scheme': 'http', 'host_port': 'hopey.netfonds.no', 'path':'/tradedump.php', 'query':'?csv_format=txt&date=20141124&paper=ORCL.N&'})
coro.send({'scheme': 'http', 'host_port': 'hopey.netfonds.no', 'path':'/tradedump.php', 'query':'?csv_format=txt&date=20141124&paper=AAPL.O&'})
coro.send({'scheme': 'http', 'host_port': 'hopey.netfonds.no', 'path':'/tradedump.php', 'query':'?csv_format=txt&date=20141124&paper=YHOO.O&'})
coro.send({'scheme': 'http', 'host_port': 'hopey.netfonds.no', 'path':'/tradedump.php', 'query':'?csv_format=txt&date=20141124&paper=GOOG.O&'})
coro.send({'scheme': 'http', 'host_port': 'hopey.netfonds.no', 'path':'/tradedump.php', 'query':'?csv_format=txt&date=20141124&paper=FB.O&'})
coro.send({'scheme': 'http', 'host_port': 'hopey.netfonds.no', 'path':'/tradedump.php', 'query':'?csv_format=txt&date=20141124&paper=VMW.O&'})
try:
    coro.send(None)
except StopIteration:
    pass

