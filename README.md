# IRIS IPTV PROXY

This is an http proxy that helps interacting with IRIS 9900 HD digital tuner (tuner).

It was written mainly to overcome the integration issues of the tuner streaming capabilities with TV Headend, which does not work very well with a unique stream URL ("/live.ts" receiver URL).

The iris-iptv-proxy provides unique channel URLs for the receiver, and also an endpoint to generate a M3U playlist out of all the channels in the IRIS digital tuner.

It could be useful for:
* Load the playlist on a media player such as VLC from the M3U playlist endpoint
* Use the proxy to integrate IRIS streaming capabilities into TV Headend.

The development has been inspired in a kodi plugin for iris 9900hd (https://github.com/viruslogic/plugin.video.iris-9900-hd),
 reusing python code from the plugin to make http requests to the device, or just to understand which URLs could be used,
 as there is no documentation about them.


## Why?

As an owner of an IRIS 9900HD I want to use the capabilities for http streaming provided out of the box with this device.
The device has a stream URL by default, which is streaming whatever channel is currently tuned. In addition, it supports
some endpoints that allow to change channel, list them or get epg information (used by the WebRemote application the device supports)

This is great, but not very useful if you want to easily change channel from say VLC, or if you want to use TVHeadend in
front of your device, which will allow you to access the contents from multiples interfaces and devices 
(more info on TV Headend integration issue here https://tvheadend.org/boards/4/topics/32434)

## Installation

You need Python 3.5 or later to run iris-iptv-proxy.

First you need to install dotenv:

```shell script
pip install -U python-dotenv
```
(or perhaps pip3, depending on how you have your python 3 setup)


Then you can clone the repository, and run it as follows:

```shell script
python iris-iptv-proxy.py
```

This will start the server on port 8000 by default. You can test if it's running using curl:

```shell script
➜ curl   http://localhost:8000
Please try a url in the form of 
 * /channel/{channelNumber}
 * /m3u
 * /epg
 * /watch%                                                                                                                                                                            
```
### Configuration

It supports following configuration env variables:

* *IRIS_DEVICE_HOST*: The ip for the IRIS device. It defaults to *192.168.1.101*
* *IRIS_PROXY_HOST*: The IP or host for this proxy. It will be used to generate the right iris-iptv-proxy URLs for all the channels in the m3u playlist. It defaults to *localhost*
* *IRIS_PROXY_PORT*: The port used for running this proxy. It defaults to 8000

### Docker

It also supports docker although it is currently not published on Docker hub

You can build it yourself:

````shell script
docker build -t iris-iptv-proxy .
````

And then run it, mapping port 8000 from the container to the host:

````shell script
docker run -it -p8000:8000 --name iris-proxy iris-iptv-proxy
````

If you need to pass configurations, you can do as follows:

````shell script
docker run -it -p8000:8000 -e IRIS_DEVICE_HOST=192.168.1.50 --name iris-proxy iris-iptv-proxy
````

## Endpoints

* /channel/{channelNumber} : This endpoint will switch first the IRIS digital tuner to that channel, and then will return as response the actual live streaming from the tuner.
* /m3u : Generates a m3u playlist with all the channels on the IRIS digital tuner
* /watch : Returns as response the current streaming from the tuner (tuner's /live.ts url)
* /epg (experimental) : Returns the tuner epg in xmltv format. Did not turn to be very useful, as it only provides epg data from channels that have been seen.


## TV Headend

Just reusing an ascii drawing to understand better the iris-iptv-proxy role on the TVH integration

```shell script
  User              TVH              iris-iptv-proxy      STB
+------+    +-------------------+    +---------------+    +--------------+
|      |    |          |Playlist+--> | /m3u          +--> | /json/chlist |
|      +--> |                   |    |               |    |              |
+------+    |          |ch1     +--> | /channel/1    +--> | /api/switch..|
            |          |ch2     |    |               |    | /live.ts     |
            |          |ch3     |    +----+----------+    +-+------------+
            |          |ch4     |         ^                 |
            |          |ch5     |         +-----------------+
            |          |ch6     |
            |          |ch7     |         Stream from STB
            |          |chXXX   |
            +-------------------+
```

Basically you can run this iris-iptv-proxy from the same machine where you have TVH running, and just proceed at 
configuring an IPTV Automatic Network using the specific M3U url (i.e. http://localhost:8000/m3u).

 
When configuring the IPTV Automatic Network, make sure you set "Maximum # input streams:" to 1. This is needed as only
one channel can be scanned at a time. Once TVH has scanned all the muxes, you can change this setting, and you would be
 able to have more than one client streaming at a time, as long as they watch the same channel.

Once everything is setup, you can automatically map services to channels and you are done.