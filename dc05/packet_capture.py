import socket
import struct
import sys

class EthernetFrame(object):
    def __init__(self, buf):
        packet = struct.unpack("!6s6s2s", buf[0][0:14])
        self.nextData = buf[0][14:]        
        self.dstMac = ':'.join([packet[0].encode('hex')[x:x+2] for x in range(0, len(packet[0].encode('hex')), 2)])
        self.srcMac = ':'.join([packet[1].encode('hex')[x:x+2] for x in range(0, len(packet[1].encode('hex')), 2)])
        self.frameType = '0x'+packet[2].encode('hex')
        self.nextFrame = None
        if self.frameType == '0x0800':
            self.nextFrame = IPv4Header(self.nextData)
   
    def dump(self):
        print "==========================="
        print "Ethernet II"
        print "===========================\n"
        print "Destination MAC Address : ", self.dstMac
        print "Source MAC Address : ", self.srcMac
        print "Type : ", self.frameType
        
        if self.nextFrame is not None:
            self.nextFrame.dump()

class IPv4Header(object):
    def __init__(self, buf):
        packet = struct.unpack("!2s2s2s2s2s2s4s4s", buf[0:20])
        self.totalLength = int(packet[1].encode('hex'), 16)
        self.sourceIp = socket.inet_ntoa(packet[6])
        self.destIp = socket.inet_ntoa(packet[7])
   
    def dump(self):
        print "==========================="
        print "IPv4 Header"
        print "==========================="
        print "Toal Length : ", self.totalLength
        print "Source IP Address : ", self.sourceIp
        print "Destination IP Address : ", self.destIp       

if __name__ == '__main__':
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    #print 'test'
    while True:
        packet = sock.recvfrom(4096)
        print 'packet: ', sys.getsizeof(packet)
        eth_header = EthernetFrame(packet)
        eth_header.dump()
