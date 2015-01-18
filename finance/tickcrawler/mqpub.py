import customserializers
import nanomsg
import asyncio
import msgpack

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
            try:
                kvList = (yield)
            except (GeneratorExit, StopIteration) as e:
                kvList = None
            if kvList is None:
                break
            subject = None
            if len(kvList) > 0:
                tick = kvList[0]['ticker']
                exch = kvList[0]['exch']
                dtype = kvList[0]['type']
                if exch is not None and dtype is not None and tick is not None:
                    subject = exch + '.' + dtype + '.' + tick
            if subject is not None:
                serializedValue = msgpack.packb(kvList, default=customserializers.encode, use_bin_type=True)
                msg = subject.encode() + b'\x00' + serializedValue;
                self.pubsock.send(msg)

    def __del__(self):
        if self.pubsock is not None:
            self.pubsock.close()
