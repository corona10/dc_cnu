import os
import socket
import sys
import time
from struct import *

class AckFrame(object):
   def __init__(self, *args, **kwargs):
      if 'ack' in kwargs:
         self.ack = kwargs['ack']

      if 'buf' in kwargs:
         fmt = "!I"
         data = unpack(fmt, kwargs['buf'])
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
            d += "\0" * diff
         self.data = d

      if 'buf' in kwargs:
         fmt = '!II1024s'
         BUF = kwargs['buf']
         data = unpack(fmt, buf)
         self.ack = data[0]
         self.size = data[1]
         d= data[2]
         self.data = d[:self.size]

   def pack(self):
      fmt = '!II1024s'
      p = pack(fmt,self.ack, self.size ,self.data)
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
   
if __name__ == "__main__":
   if len(sys.argv) < 3:
      print "[Dest IP Addr] [Dest Port] [File Path]"
      sys.exit()
   
   buf = 1024
   ServerIP = sys.argv[1]
   ServerPort = int(sys.argv[2])
   filePath = sys.argv[3]

   try:
      f = open(filePath, "rb")
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.settimeout(0.001)
      addr = (ServerIP, ServerPort)
      

      f.seek(0, os.SEEK_END)
      fileSz = f.tell()
      total = fileSz / buf
      f.seek(0, 0)
      dt = f.read(buf)
      sendSize = 0

      fName = os.path.basename(filePath)
      packet = FileInfoPacket(totalSize = fileSz, fileName = fName)
      p = packet.pack()
      sock.sendto(p, addr)

      ak = 0
      packet = FileFrame(ack = ak ,data = dt)
      p = packet.pack()
      sendSize += len(dt)

      while (dt):
         try:
            if(sock.sendto(p, addr)):
               ack_buf , addr  = sock.recvfrom(4)
               packet = AckFrame(buf = ack_buf)
               recv_ack = packet.ack
               if recv_ack is ak ^ 1:
                  dt = f.read(buf)
                  ak = recv_ack
                  packet = FileFrame(ack = recv_ack, data = dt)
                  p = packet.pack()
                  sendSize += packet.size
                  print sendSize,' / ',fileSz, '(current size / total size)', float(sendSize) / float(fileSz) * 100 ,'%'
               else:
                  print "Ack Error!"

         except socket.timeout:
            print 'Timed out'

   finally:
      f.close()
      sock.close()
