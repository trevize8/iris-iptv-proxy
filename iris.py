import gzip
import json
import time
import urllib
import urllib.request
from io import StringIO

import config

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'
defaultHeaders = {'User-Agent': USER_AGENT,
                  'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                  'Accept-Encoding': 'gzip,deflate,sdch',
                  'Cookie': 'qlqhzyhjljcfffyy=21636d1e642c874112d9674ac8e8b002',
                  'Accept-Language': 'en-US,en;q=0.8'}
channelsUrl = '/json/channel/list'
epgUrl = '/json/epg/daily'
channelSwitchUrl = '/api/channel/switch'
currentStream = '/live.ts'
UTF8 = 'utf-8'


def SwitchChannel(cid):
    print("Changing to channel " + cid)
    channels = getChannels()
    current_id = channels['current']['channel_id']
    while str(cid) != str(current_id):
        requestSwitchChannel(cid)
        time.sleep(2)
        channels = getChannels()
        current_id = channels['current']['channel_id']


def WatchCurrentStream(request):
    try:
        # Using port 9891 as is the one really used to stream.
        response = urllib.request.urlopen('http://' + config.Config.IRIS_DEVICE_HOST + ':9891' + currentStream)
        request.send_response(response.code)

        respheaders = response.headers
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                request.send_header(key, respheaders[key])
        request.end_headers()

        CHUNK = 16 * 1024
        for chunk in iter(lambda: response.read(CHUNK), ''):
            if not chunk:
                break
            request.wfile.write(chunk)

        request.wfile.close()
    except urllib.request.URLError as e:
        print("Error trying to watch current stream", e)


def GenerateM3U(request):
    print("GenerateM3U start")
    channels = getChannels()
    print("Obtained channel list from http://" + config.Config.IRIS_DEVICE_HOST + channelsUrl + " and " + str(
        len(channels['chnlist'])) + " channels")
    request.wfile.write(b"#EXTM3U\n")
    for i in channels['chnlist']:
        request.wfile.write(
            b"#EXTINF:-1 tvh-chnum=" + bytes(str(i['id']), UTF8) + b"," + bytes(i['name'], UTF8) + b"\n")
        request.wfile.write(
            b"http://" + bytes(config.Config.IRIS_PROXY_HOST, UTF8) + b":" + bytes(config.Config.IRIS_PROXY_PORT,
                                                                                   UTF8) + b"/channel/" + bytes(
                str(i['id']), UTF8) + b"\n")

    request.wfile.close
    print("GenerateM3U end")


def GenerateEPG(request):
    print("GenerateEPG start")
    channels = getChannels()
    print("Obtained channel list from http://" + config.Config.IRIS_DEVICE_HOST + channelsUrl + " and " + str(
        len(channels['chnlist'])) + " channels")

    request.wfile.write(b'<?xml version="1.0" encoding="UTF-8"?>')
    request.wfile.write(b'<tv generator-info-name="TV Guide Scraper - by Arbe">')

    for i in channels['chnlist']:
        # Write channel
        request.wfile.write(b'<channel id="' + bytes(str(i['id']), UTF8) + b'">')
        request.wfile.write(b'<display-name lang="en">' + bytes(i['name'], UTF8) + b'</display-name>')
        request.wfile.write(b'</channel>')

        # Write programme (from EPG)
        epg = getEPG(str(i['id']))
        print("Programs for " + i['name'] + " is " + str(epg['epg_daily']['programs']))
        for program in epg['epg_daily']['programs']:
            request.wfile.write(
                b'<programme start="' + bytes(str(program['start']), UTF8) + b'" end="' + bytes(str(program['end']),
                                                                                                UTF8) + b'" channel="' + bytes(
                    str(i['name']), UTF8) + b'">')
            request.wfile.write(b'<title lang="en">' + bytes(program['name'], UTF8) + b'</title>')
            request.wfile.write(b'</programme>')
        time.sleep(1.5)

    request.wfile.write(b'</tv>')
    request.wfile.close
    print("GenerateEPG end")


def getChannels():
    return json.loads(requestChannels())


def requestChannels():
    azheaders = defaultHeaders
    azheaders['X-Requested-With'] = 'XMLHttpRequest'
    return getRequest("http://" + config.Config.IRIS_DEVICE_HOST + channelsUrl, None, azheaders)


def requestSwitchChannel(cid):
    azheaders = defaultHeaders
    azheaders['X-Requested-With'] = 'XMLHttpRequest'
    values = {'cid': urllib.parse.quote_plus(cid)}
    data = urllib.parse.urlencode(values)
    return getRequest("http://" + config.Config.IRIS_DEVICE_HOST + channelSwitchUrl, bytes(data, UTF8), azheaders)


def getEPG(cid):
    return json.loads(requestEPG(cid))


def requestEPG(cid):
    azheaders = defaultHeaders
    azheaders['X-Requested-With'] = 'XMLHttpRequest'
    return getRequest("http://" + config.Config.IRIS_DEVICE_HOST + epgUrl + "?cid=" + cid, None, azheaders)


def getRequest(url, user_data=None, headers=defaultHeaders):
    print("getRequest URL:" + str(url))
    opener = urllib.request.build_opener()
    urllib.request.install_opener(opener)
    req = urllib.request.Request(url, user_data, headers)

    try:
        response = urllib.request.urlopen(req)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            link1 = f.read()
        else:
            link1 = response.read()

    except urllib.request.URLError as e:
        print("Error getting the request ", e)
        link1 = ""

    if not (str(url).endswith('.zip')):
        link1 = str(link1.decode(UTF8)).replace('\n', '')
    return link1
