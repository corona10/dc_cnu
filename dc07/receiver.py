import os
import socket
import sys
import time
from struct import *

UDP_IP = ""
UDP_PORT = 5005
BUFFER_SIZE = 1472
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
      if 'data' in kwargs:
         d = kwargs['data']
         self.size = len(d)
         if len(d) < 1024:
            diff = 1024 - len(d)
            d += '\0' * diff
         self.data = d

      if 'buf' in kwargs:
         fmt = '!II1024s'
         buf = kwargs['buf']
         data = unpack(fmt, buf)
         self.ack = data[0]
         self.size = data[1]
         d= data[2]
         self.data = d[:self.size]

   def pack(self):
      fmt = '!II1024s'
      p = pack(fmt, self.ack,self.size, self.data)
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
   f = open('./'+packet.fileName , 'w')
   recv_buffer = dict()
   try:
      recvSize = 0
      ack = 0 
      while True:
         data, addr = sock.recvfrom(1024+4+4)
         packet = FileFrame(buf = data) 
         print packet.ack, get_offset(packet.ack)
         recv_buffer[packet.ack] = packet.data
         print  packet.ack % WINDOW_SIZE, WINDOW_SIZE - 1
         if packet.ack % WINDOW_SIZE == WINDOW_SIZE - 1:
            while(True):
               finish = True
               for idx in range(packet.ack - WINDOW_SIZE +1, packet.ack+1):
                  if idx not in recv_buffer:
                     finish = False
                     packet = AckFrame(ack = idx)
                     p = packet.pack()
                     sock.sendto(p, addr)
                     data, addr = sock.recvfrom(1024 + 4 + 4)
                     packet = FileFrame(buf = data)
                     recv_buffer[ack] = packet.data
               if finish:
                  packet= AckFrame(ack = packet.ack + 1)
                  p = packet.pack()
                  sock.sendto(p, addr)
                  break

   except socket.error as e:
      print e
      f.close()
      sock.close()
      sys.exit()
   finally:
      f.close()
      sock.close()

   f.close()
