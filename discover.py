import httplib
import socket
import StringIO

# generic
SSDP_ALL = 'ssdp:all'
UPNP_ROOT = 'upnp:rootdevice'

# devices
DIAL = 'urn:dial-multiscreen-org:service:dial:1'


class SSDPResponse(object):

    class _FakeSocket(StringIO.StringIO):
        def makefile(self, *args, **kw):
            return self

    def __init__(self, response):
        r = httplib.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self._headers = r.getheaders()
        self.location = r.getheader('location')
        self.usn = r.getheader('usn')
        self.st = r.getheader('st')
        self.server = r.getheader('server')
        self.cache = r.getheader('cache-control').split('=')[1]

    def __repr__(self):
        return '<SSDPResponse({location}, {st}, {usn})'.format(**self.__dict__)


def discover(st, timeout=3, retries=1):

    group = ('239.255.255.250', 1900)        
    message = 'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 10\r\nST:urn:dial-multiscreen-org:service:dial:1\r\n\r\n';

    socket.setdefaulttimeout(timeout)

    responses = {}

    for _ in range(retries):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message.format(st=st), group)

        while 1:
            try:
                response = SSDPResponse(sock.recv(1024))
                responses[response.location] = response
            except socket.timeout:
                break

    return responses.values()


if __name__ == '__main__':
    for device in discover(SSDP_ALL, timeout=5):
        print "%s\n\t%s" % (device.location, device.server)

"""
DLNA_RENDERER = 'urn:schemas-upnp-org:device:MediaRenderer:1'
DLNA_SERVER = 'urn:schemas-upnp-org:device:MediaServer:1'
GATEWAY = 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'
PANASONIC_VIERA = 'urn:panasonic-com:device:p00RemoteController:1'
ROKU = 'roku:ecp'
SONOS = 'urn:schemas-upnp-org:device:ZonePlayer:1'
SONY_NEX = 'urn:schemas-sony-com:service:ScalarWebAPI:1'
WAN_IP = 'urn:schemas-upnp-org:service:WANIPConnection:1'
WAN_PPP = 'urn:schemas-upnp-org:service:WANPPPConnection:1'
"""