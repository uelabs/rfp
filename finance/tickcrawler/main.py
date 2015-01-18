import codecs
import configparser
import crawler
import csv
import datetime
import getopt
import mqpub
import parser
import respfilter
import sys
import urllib
import urllib.request

def usage():
    print("Usage: {} -c <Two Letter Country Code> [-d <Date YYYYMMDD> -e <Exchange> -s <Socket>] -h".format(sys.argv[0]))
    print("Example: {} -c US -d 20150102 -e NASDAQ -s ipc:///tmp/tick.ipc".format(sys.argv[0]))
    print("Following are the supported options:")
    print("-c|--country US <Error if unspecified>")
    print("-d|--date 20150102 <Defaults to todays date>")
    print("-e|--exchange NYSE <Defaults to All exchanges in the country>")
    print("-h|--help")
    print("-s|--socket tcp://127.0.0.1:5152 <Defaults to ipc:///tmp/tick.ipc>")

def fetch_companies(url, exch, ua):
    url = url.format(exchange=exch)
    req = urllib.request.Request(url, headers={'User-Agent': ua})
    resp = urllib.request.urlopen(req)
    if resp.getcode() is not None and resp.getcode() == 200:
        resp = None
    charset = 'utf-8'
    if resp.headers.get_content_charset():
        charset =  resp.headers.get_content_charset()
    return codecs.iterdecode(resp, charset)

# check if we got adequate arguments
opts, args = getopt.getopt(sys.argv[1:], "c:d:e:s:h", ['country=', 'date=', 'exchange=', 'socket=', 'help'])
country = None
exch = []
date = datetime.date.today();
sock = 'ipc:///tmp/tick.ipc'
for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage() 
        sys.exit(0)
    elif opt in ('-c', '--country'):
        country = arg
    elif opt in ('-d', '--date'):
        try:
            date = datetime.datetime.strptime(arg, '%Y%m%d')
        except ValueError:
            usage()
            sys.exit(-1)
    elif opt in ('-e', '--exchange'):
        exch.append(arg)
    elif opt in ('-s', '--socket'):
        sock = arg

# now parse the config file
confp = configparser.ConfigParser()
confp.read("main.ini")
if not country or len(country) != 2:
    usage()
    sys.exit(-2)
if not confp.has_section(country):
    print("Unsupported country: " + country)
    sys.exit(-3)
userAgent = confp[country]['UserAgent']
tickUrl = confp[country]['UrlTemplate']
scheme = confp[country]['Scheme'] 
paths = confp[country]['Path'].split()
query = confp[country]['Query'] 
hostPort = confp[country]['HostPort'] 
allexch = confp[country]['Exchanges'].split(',')
exchanges = {}
if not exch:
    exch = allexch
for e in exch:
    try:
        exchanges[e] = confp[country][e]
    except:
        pass

# instantiate the system from the bottom up
pub = mqpub.NNPublisher(sock)
parser = parser.HopeyParser(pub.publish())
fltr = respfilter.HttpResponseTypeFilter(parser.parse())
crawler = crawler.HttpCrawler(fltr.do_filter())
crawlgen = crawler.fetch()
crawlgen.send(None)

# now start the chain of actors after priming the coro
for exch in exchanges:
    if exch in exchanges.keys():
        content = fetch_companies(tickUrl, exch, userAgent)
        if content is not None:
            reader = csv.DictReader(content)
            for row in reader:
                qry = query.format(date.strftime('%Y%m%d'), row["Symbol"] + '.' + exchanges[exch])
                for path in paths:
                    crawlgen.send({'scheme': scheme, 'host_port': hostPort, 'path': path, 'query': qry})
