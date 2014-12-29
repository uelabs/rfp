import asyncio
import parser
import pickle

@asyncio.coroutine
def test_coro():
    while True:
        lst = yield
        if lst is None:
            break
        byts = pickle.dumps(lst)
        print(byts)

with open('test/data/YHOO.O.trade.tsv') as trade:
    tfile = trade.read()
with open('test/data/YHOO.O.pos.tsv') as pos:
    pfile = pos.read()

p = parser.HopeyParser(test_coro())
g = p.parse()
g.send(None)
g.send(('http://hopey.netfonds.no/tradedump.php?csv_format=txt&date=20141031&paper=YHOO.O&', tfile))
g.send(('http://hopey.netfonds.no/posdump.php?csv_format=txt&date=20141031&paper=YHOO.O&', pfile))
