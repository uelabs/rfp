import asyncio
import builtins
import configparser
import datetime
import re
import urllib.parse

class Parser:
    @asyncio.coroutine
    def parse(self):
        pass

class TextParser(Parser):
    @asyncio.coroutine
    def parserecords(self, rec, url, rownum):
        pass

    def __init__(self, coro, config_file="parser.ini", section="DEFAULT"):
        confParser = configparser.ConfigParser()
        confParser.read(config_file)
        self.record_sep = chr(int(confParser[section]['RecordSeparator']))
        self.field_sep = chr(int(confParser[section]['FieldSeparator']))
        field_names = confParser[section]['FieldsLine']
        self.confParser = confParser
        self.coro = coro
        try:
            # prime the coroutine
            coro.send(None)
            self.fields = int(field_names)
            self._is_int = True
        except (TypeError, ValueError):
            self._is_int = False
            self.fields = re.split(self.field_sep, field_names)

    @asyncio.coroutine
    def parse(self):
        while True:
            try:
                (url, content) = yield
                if url is None or content is None:
                    break
                records = re.split(self.record_sep, content)
                count = 0
                plist = []
                recgen = self.parserecords(url, *records)
                for rec in recgen:
                    if rec is not None or isinstance(rec, str) and rec.repr().strip() == "":
                        plist.append(rec)
                self.coro.send(plist)
            except GeneratorExit:
                break

class HopeyParser(TextParser):
    def __init__(self, coro):
        section = "hopey.netfonds.no"
        super().__init__(coro, section=section)
        self.timezone = self.confParser[section]['TimeZone']
        self.ticker_param = self.confParser[section]['TickerParam']
        dataTypes = re.split('\s+', self.confParser[section]['DataTypes'])
        self.typeDetector = {}
        self.typeSpecificLambdaGen = {}
        for dataType in dataTypes:
            fieldTypesList = re.split('\s+', self.confParser[section]['FieldTypes.' + dataType])
            self.typeSpecificLambdaGen[dataType] = HopeyParser.lambdaGenerator(*fieldTypesList)
            self.typeDetector[dataType] = self.confParser[section]['Detect.' + dataType]
        exch_suffixes = re.split('\s+', self.confParser[section]['Exchanges'])
        self.exchanges = {}
        for exch in exch_suffixes:
            self.exchanges[exch] = self.confParser[section]['Exchange.' + exch]

    def lambdaGenerator(*args):
        while True:
            for fieldType in args:
                (fn, *fnargs) = re.split(':', fieldType)
                fnhierarchy = re.split('\.', fn)
                module = globals()[fnhierarchy[0]]
                for i in range(1, len(fnhierarchy)):
                    module = getattr(module, fnhierarchy[i])
                fn = lambda x: module(x, *fnargs)
                yield fn

    def parseTicker(self, url):
        parsed_url = urllib.parse.urlparse(url)
        parsed_qs = urllib.parse.parse_qs(parsed_url.query)
        if self.ticker_param in parsed_qs:
            full_tickr = parsed_qs[self.ticker_param]
            (ticker, exch) = re.split('\.', full_tickr[0] if len(full_tickr) > 0 else "")
            if len(ticker) > 0 and len(exch) > 0:
                return (ticker, self.exchanges[exch])
        return None

    def detectType(self, url):
        for key in self.typeDetector.keys():
            mobj = re.search(self.typeDetector[key], url)
            if mobj is not None:
                return key

    @asyncio.coroutine
    def parserecords(self, url, *records):
        fieldType = self.detectType(url)
        dataDict = {}
        count = 0
        colgen = None
        for rec in records:
            if len(rec) <= 0:
                break
            count += 1
            fields = re.split(self.field_sep, rec)
            if count == 1:
                fs = list(fields)
                def columngen():
                    while True:
                        for f in fs:
                            yield f
                colgen = columngen()
                yield None
                continue
            firstField = True
            for tupl in zip(fields, self.typeSpecificLambdaGen[fieldType], colgen):
                key = tupl[2]
                val = tupl[0]
                fn = tupl[1]
                if firstField:
                    val += self.timezone
                    firstField = False
                if val is not None and len(val) > 0:
                    dataDict[key] = fn(val)
            (dataDict['ticker'], dataDict['exch']) = self.parseTicker(url)
            dataDict['type'] = fieldType
            yield dataDict
