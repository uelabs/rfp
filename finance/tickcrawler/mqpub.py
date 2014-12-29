import nanomsg
import asyncio
import pickle

class Publisher:
    @asyncio.coroutine
    def publish(self, subject, msg):
        pass

class NNPublisher(Publisher):
    def __init__(self, url): 
        self.url = url
        self.pubsock = nanomsg.Socket(nanomsg.PUB)
        self.pubsock.connect(url)

    @asyncio.coroutine
    def publish(self):
        while True:
            kvList = (yield)
            subject = None
            if len(kvList) > 0:
                tick = kvList[0]['ticker']
                exch = kvList[0]['exch']
                subject = exch + '.' + tick
            serializedValue = pickle.dumps(kvList)
            if subject is not None:
                msg = subject.encode() + b'\x00' + serializedValue;
                self.pubsock.send(msg)

    def __del__(self):
        if self.pubsock is not None:
            self.pubsock.close()
