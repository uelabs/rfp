import asyncio
import aiohttp
import queue
import threading

class FiniteConnector(aiohttp.connector.TCPConnector):
    def __init__(self, *args, maxsize=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.freed = dict([])
        self.maxsize = maxsize
        self.lock = threading.RLock()

    @asyncio.coroutine
    def connect(self, req):
        hostPort = repr(req.host) + repr(req.port)
        with self.lock as lock:
            print('Got lock: ' + hostPort) 
            print('For URL: ' + req.url)
            if hostPort not in self.freed:
                freeq = asyncio.Queue(self.maxsize)
                freeq.count = 0;
                self.freed[hostPort] = freeq
            freeq = self.freed[hostPort]
            if self.maxsize > 0 and freeq.count >= self.maxsize:
                conn = yield from freeq.get()
                return conn
            if self.maxsize > 0:
                freeq.count += 1
            print('Maxsize: {}, Count: {}'.format(self.maxsize, freeq.count)) 
        conn = yield from super().connect(req)
        return conn

    def _release(self, key, req, transport, protocol, *, should_close=False):
        hostPort = repr(req.host) + repr(req.port)
        with self.lock as lock:
            if hostPort in self.freed and should_close == False:
                freeq = self.freed[hostPort]
                freeq.put_nowait(aiohttp.connector.Connection(self, key, req, transport, protocol, asyncio.get_event_loop()))
        return super()._release(key, req, transport, protocol, should_close=should_close)
