import aiohttp
import asyncio
import configparser
import connector

class Crawler:
    @asyncio.coroutine
    def crawl(self, url, connector):
        pass

    def __init__(self, coro, config_file="crawler.ini"):
        section = 'DEFAULT'
        self.confParser = configparser.ConfigParser()
        self.confParser.read(config_file)
        urlTemplate = self.confParser[section]['UrlTemplate']
        poolSz = int(self.confParser[section]['PoolSize'])
        self._connector = connector.FiniteConnector(maxsize=poolSz)
        self._url_template = urlTemplate

        # prime the coro passed and make it an instance variable
        coro.send(None)
        self.sendto_coro = coro

    @asyncio.coroutine
    def fetch(self):
        evloop = asyncio.get_event_loop()
        fetchTasks = []
        while True:
            try:
                subs = yield
                if subs is not None:
                    url = self._url_template.format(**subs)
                    print(url)
                    future = asyncio.async(self.crawl(url, self._connector))
                    future.add_done_callback(self.postprocess)
                    fetchTasks.append(future)
                else:
                    break
            except GeneratorExit:
                break
        print ('Out of the yield loop: ' + repr(len(fetchTasks)))
        evloop.run_until_complete(asyncio.wait(fetchTasks))

    def postprocess(self, fut):
        try:
            self.sendto_coro.send(fut.result())
        except StopIteration:
            pass
        except BaseException as e:
            print ("Xception: {}, {}".format(type(e), e))

class HttpCrawler(Crawler):
    def __init__(self, coro, config_file="crawler.ini", section="HTTP"):
        super().__init__(coro, config_file)
        self.method = self.confParser[section]['Method']

    @asyncio.coroutine
    def crawl(self, url, connector):
        print ("Inside httpcrawler: " + url)
        cliResp = yield from aiohttp.request(self.method, url, connector=connector)
        print(cliResp)
        actualResp = yield from cliResp.text()
        tupl = (url, actualResp, cliResp.headers)
        cliResp.close()
        return tupl

