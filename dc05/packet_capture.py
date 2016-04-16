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
        elif self.frameType == '0x0806':
            self.nextFrame = ARPHeader(self.nextData)
   
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
        self.nextData = buf[20:]
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
        self.ttl = (int(packet[4].encode('hex'), 16) >> 8 & 0xff)
        self.protocol = (int(packet[4].encode('hex'), 16) & 0xff)
        self.serviceType = (int(packet[0].encode('hex'),16) >> 2 ) & 0x3f
        self.nextFrame = None
        if self.protocol == 6:
            self.nextFrame = TCPHeader(self.nextData)
 
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
    
        if self.nextFrame is not None:
            print self.nextFrame.dump()

class ARPHeader(BaseFrame):
    def __init__(self, buf):
        self.name = 'Address Resolution Protocol'
        packet = struct.unpack("!2s2s2s2s6s4s6s4s", buf[0:28])
        self.HardwareType = int(packet[0].encode('hex'), 16)
        self.ProtocolType = int(packet[1].encode('hex'), 16)
        self.text = packet[2].encode('hex')
        self.HLEN = (int(packet[2].encode('hex'), 16) >>8) & 0xf
        self.PLEN = (int(packet[2].encode('hex'), 16)) & 0xf
        self.operation = int(packet[3].encode('hex'), 16)
        self.SHA =  ':'.join([packet[4].encode('hex')[x:x+2] for x in range(0, len(packet[4].encode('hex')), 2)])
        self.SPA = socket.inet_ntoa(packet[5]) 
        self.THA = ':'.join([packet[6].encode('hex')[x:x+2] for x in range(0, len(packet[6].encode('hex')), 2)])
        self.TPA = socket.inet_ntoa(packet[7])       
    def dump(self):
        self.printTitle()
        print 'Hardware Type :', self.HardwareType
        print 'Protocol Type :', self.ProtocolType
        print 'Hardware Length :', self.HLEN
        print 'Protocol Length :', self.PLEN
        print 'Operation :', self.operation
        print 'Source Hardware address :', self.SHA
        print 'Source Protocol address :', self.SPA
        print 'Destination Hardware address :', self.THA
        print 'Destination Protocol address :', self.TPA

class TCPHeader(BaseFrame):
    def __init__(self, buf):
        self.name = "Transmission Control Protocol"
        packet = struct.unpack("!2s2s4s4s1s1s2s2s2s", buf[0:20])
        self.srcPort = int(packet[0].encode('hex'), 16)
        self.dstPort = int(packet[1].encode('hex'), 16)
        self.SEQ = int(packet[2].encode('hex'), 16)
        self.ACK = int(packet[3].encode('hex'), 16)
        self.URG = (int(packet[4].encode('hex'), 16) >> 5) & 0x1
        self.ACK = (int(packet[4].encode('hex'), 16) >> 4) & 0x1
        self.PSH = (int(packet[4].encode('hex'), 16) >> 3) & 0x1
        self.RST = (int(packet[4].encode('hex'), 16) >> 2) & 0x1
        self.SYN = (int(packet[4].encode('hex'), 16) >> 1) & 0x1
        self.FIN = (int(packet[4].encode('hex'), 16)) & 0x1
        self.headerLength = 20 + (int(packet[4].encode('hex'), 16)>>4 & 0xf)
        self.windowSize = int(packet[6].encode('hex'), 16)
        self.checksum = "0x"+packet[7].encode('hex')
        self.urgentPointer = int(packet[8].encode('hex'), 16)

    def dump(self):
        self.printTitle()
        print "Source Port address :", self.srcPort
        print "Destination Port address :", self.dstPort
        print "Sequence Number :", self.SEQ
        print "Acknowledgement Number :", self.ACK
        print "Header Length :", self.headerLength
        print "URG :", self.URG
        print "ACK :", self.ACK
        print "PSH :", self.PSH
        print "RST :", self.RST
        print "SYN :", self.SYN
        print "FIN :", self.FIN
        print "Window Size :", self.windowSize
        print "Checksum :", self.checksum
        print "Urgent Pointer :", self.urgentPointer

if __name__ == '__main__':
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    while True:
        packet = sock.recvfrom(4096)
        print "==========================="
        print 'Frame size: ', sys.getsizeof(packet[0])
        eth_header = EthernetFrame(packet)
        t = eth_header.dump()
        print "*****"
