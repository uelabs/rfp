import asyncio

class Filter:
    @asyncio.coroutine
    def do_filter(self):
        pass
    def __init__(self, coro):
        self.ping_coro = coro
        self.ping_coro.send(None)

class HttpResponseTypeFilter(Filter):
    def __init__(self, coro):
        super().__init__(coro)

    @asyncio.coroutine
    def do_filter(self):
        while True:
            try:
                tupl = yield
                print("From respfilter: " + tupl[0])
                if tupl is None:
                    break
                if tupl[2]['Content-Type'].lower().startswith("text/plain"):
                    self.ping_coro.send((tupl[0], tupl[1]))
            except (StopIteration, GeneratorExit) as e:
                break
