import os
import socket
import sys
import time
from struct import *
import md5

UDP_IP = ""
UDP_PORT = 5005
WINDOW_SIZE = 4

class AckFrame(object):
   def __init__(self, *args, **kwargs):
      if 'ack' in kwargs:
         self.ack = kwargs['ack']

      if 'buf' in kwargs:
         fmt = "!I"
         data = unpack(fmt, buf)
         self.ack = data[0]

   def pack(self):
      fmt = "!I"
      p = pack(fmt, self.ack)
      return p
       
class FileFrame(object):

   def __init__(self, *args, **kwargs):
      if 'ack' in kwargs:
         self.ack = kwargs['ack']
      if 'checksum' in kwargs:
         self.checksum = kwargs['checksum']
      if 'data' in kwargs:
         d = kwargs['data']
         self.size = len(d)
         if len(d) < 1024:
            diff = 1024 - len(d)
            d += "\0" * diff
         self.data = d

      if 'buf' in kwargs:
         fmt = '!II32s1024s'
         buf = kwargs['buf']
         data = unpack(fmt, buf)
         self.ack = data[0]
         self.size = data[1]
         self.checksum = data[2]
         d= data[3]
         self.data = d[:self.size]

   def pack(self):
      fmt = '!II32s1024s'
      p = pack(fmt,self.ack, self.size,self.checksum ,self.data)
      return p


class FileInfoPacket(object):

   def __init__(self, *args, **kwargs):
      if 'totalSize' in kwargs:
         self.totalSize = kwargs['totalSize']

      if 'fileName' in kwargs:
         self.fileName = kwargs['fileName']

      if 'buf' in kwargs:
         fmt = '!I1024s'
         buf = kwargs['buf']
         data = unpack(fmt, buf)
         self.totalSize = data[0]
         self.fileName = data[1].replace('\x00','')


   def pack(self):
      fmt = '!I1024s'
      p = pack(fmt, self.totalSize, self.fileName)
      return p

def get_offset(idx):
   return idx*1024
if __name__ == "__main__":
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.bind((UDP_IP, UDP_PORT))

   print "ready for client... port", UDP_PORT
   packet, addr = sock.recvfrom(1024+4)
   packet = FileInfoPacket(buf =packet)
   print packet.totalSize, packet.fileName
   totalSize = packet.totalSize
   numberOfFrame = totalSize/1024
   endOfFrame = numberOfFrame%WINDOW_SIZE
   fullCompleted = False
   f = open('./'+packet.fileName , 'w')
   recv_buffer = dict()
   try:
      ack = 0 
      while True:
         data, addr = sock.recvfrom(1024+4+4 + 32)
         packet = FileFrame(buf = data)
         if md5.md5(packet.data).hexdigest() == packet.checksum:
            recv_buffer[packet.ack] = packet.data
         if packet.ack % WINDOW_SIZE == WINDOW_SIZE - 1:
            while(True):
               finish = True
               for idx in range(packet.ack - WINDOW_SIZE +1, packet.ack +1):
                  if idx not in recv_buffer:
                     finish = False
                     packet = AckFrame(ack = idx)
                     p = packet.pack()
                     sock.sendto(p, addr)
                     data, addr = sock.recvfrom(1024 + 4 + 4 +32)
                     packet = FileFrame(buf = data)
                     if md5.md5(packet.data).hexdigest() == packet.checksum:
                        recv_buffer[idx] = packet.data
                 
               if finish:
                  packet= AckFrame(ack = packet.ack + 1)
                  p = packet.pack()
                  sock.sendto(p, addr)
                  break
         elif packet.ack == numberOfFrame:
               while(True):
                  finish = True
                  for idx in range(packet.ack - endOfFrame, packet.ack + 1):
                     if idx not in recv_buffer:
                        finish = False
                        packet = AckFrame(ack = idx)
                        p = packet.pack()
                        sock.sendto(p, addr)
                        data, addr = sock.recvfrom(1024 + 4 + 4 + 32)
                        packet = FileFrame(buf = data)
                        if md5.md5(packet.data).hexdigest() == packet.checksum:
                           recv_buffer[idx] = packet.data
                  
                   
                  if finish:
                     packet= AckFrame(ack = packet.ack + 1)
                     p = packet.pack()
                     sock.sendto(p, addr)
                     fullCompleted = True
                     break
         if fullCompleted:
            recvSize = 0
            for idx in range(0, numberOfFrame+1):
               recvSize = recvSize + len(recv_buffer[idx])
               print recvSize, '/', totalSize, '(current size / total size)', float(recvSize) / float(totalSize) * 100 ,'%'

               f.write(recv_buffer[idx])
            break    
   except socket.error as e:
      print e
      f.close()
      sock.close()
      sys.exit()
   finally:
      f.close()
      sock.close()
