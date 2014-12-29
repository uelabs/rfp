import datetime
import mqpub
import nanomsg
import pickle

val2send = [{'source': 'Auto trade', 'exch': 'US.NASDAQ', 'quantity': 100, 'ticker': 'YHOO', 'time': datetime.datetime(2014, 10, 31, 14, 30, 1, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), 'price': 46.21}, {'source': 'Auto trade', 'exch': 'US.NASDAQ', 'quantity': 100, 'ticker': 'YHOO', 'time': datetime.datetime(2014, 10, 31, 14, 30, 1, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), 'price': 46.21}, {'source': 'Auto trade', 'exch': 'US.NASDAQ', 'quantity': 100, 'ticker': 'YHOO', 'time': datetime.datetime(2014, 10, 31, 14, 30, 1, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), 'price': 46.21}, {'source': 'Auto trade', 'exch': 'US.NASDAQ', 'quantity': 100, 'ticker': 'YHOO', 'time': datetime.datetime(2014, 10, 31, 14, 30, 1, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), 'price': 46.21}, {'source': 'Auto trade', 'exch': 'US.NASDAQ', 'quantity': 100, 'ticker': 'YHOO', 'time': datetime.datetime(2014, 10, 31, 14, 30, 1, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))), 'price': 46.21}]

# create a nanosub socket prior to this test case
serverUrl = 'ipc:///tmp/nnpub'
subs = nanomsg.Socket(nanomsg.SUB)
subs.set_string_option(level=nanomsg.SUB, option=nanomsg.SUB_SUBSCRIBE, value='US.NASDAQ')
subs.bind(serverUrl)
pub = mqpub.NNPublisher(serverUrl)
gen = pub.publish()
gen.send(None)
gen.send(val2send)
gen.send(val2send)
msg = subs.recv()

# now verify if the message was made correctly
# loop until we find a NULL terminator
index = 0
for byt in msg:
    index += 1
    if byt == 0:
        break;

# now extract the data from the 
data = msg[index:]
valRecd = pickle.loads(data)
if valRecd != val2send:
    print("Error checking sent and received values")
print(valRecd)
