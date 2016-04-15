import socket
import struct
import sys

class BaseFrame(object):
    def __init__(self):
        pass

    def printTitle(self):
        print "==========================="
        print self.name
        print "==========================="


class EthernetFrame(BaseFrame):
    def __init__(self, buf):
        packet = struct.unpack("!6s6s2s", buf[0][0:14])
        self.name = "Ethernet II"
        self.nextData = buf[0][14:]        
        self.dstMac = ':'.join([packet[0].encode('hex')[x:x+2] for x in range(0, len(packet[0].encode('hex')), 2)])
        self.srcMac = ':'.join([packet[1].encode('hex')[x:x+2] for x in range(0, len(packet[1].encode('hex')), 2)])
        self.frameType = '0x'+packet[2].encode('hex')
        self.nextFrame = None
        if self.frameType == '0x0800':
            self.nextFrame = IPv4Header(self.nextData)
   
    def dump(self):
        self.printTitle()
        print "Destination MAC Address : ", self.dstMac
        print "Source MAC Address : ", self.srcMac
        print "Type : ", self.frameType
        
        if self.nextFrame is not None:
            self.nextFrame.dump()

class IPv4Header(BaseFrame):
    def __init__(self, buf):
        packet = struct.unpack("!2s2s2s2s2s2s4s4s", buf[0:20])
        self.name = "Internet Protocol Version 4"
        self.totalLength = int(packet[1].encode('hex'), 16)
        self.checksum = int(packet[5].encode('hex'), 16)
        self.sourceIp = socket.inet_ntoa(packet[6])
        self.destIp = socket.inet_ntoa(packet[7])
        self.version = int(packet[0].encode('hex'), 16) >> 12
        self.headerLength= (int(packet[0].encode('hex'), 16) >> 8 & 0x0f)*4
        self.identification = int(packet[2].encode('hex'), 16)
        self.reserved = int(packet[3].encode('hex'), 16) >> 15
        self.df = int(packet[3].encode('hex'), 16) >> 14 & 0x01
        self.mf = int(packet[3].encode('hex'), 16) >> 13 & 0x01
        self.fragmentOffset = int(packet[3].encode('hex'), 16) & 0x1fff
        self.ttl = (int(packet[4].encode('hex'), 16) >> 8)
        self.protocol = (int(packet[4].encode('hex'), 16) &0xff)
        self.serviceType = (int(packet[0].encode('hex'),16) >> 2 ) & 0x3f
 
    def dump(self):
        self.printTitle()
        print "Version :", self.version
        print "Header Length :", self.headerLength
        print "Service Type :", self.serviceType
        print "Total Length :", self.totalLength
        print "Identification :", self.identification
        print "Reserved bit :",self.reserved
        print "Don't Fragment :", self.df
        print "More Fragment :", self.mf
        print "Fragment Offset :",self.fragmentOffset
        print "Time To Live : ", self.ttl
        print "Protocol :",self.protocol
        print "Header Checksum :", self.checksum
        print "Source IP Address :", self.sourceIp
        print "Destination IP Address :", self.destIp       


if __name__ == '__main__':
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    while True:
        packet = sock.recvfrom(4096)
        print "==========================="
        print 'Frame size: ', sys.getsizeof(packet[0])
        eth_header = EthernetFrame(packet)
        eth_header.dump()
        print ""
