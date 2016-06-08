import os
import socket
import sys
import time
from struct import *

WINDOW_SIZE = 4

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

def get_offset(idx):
   return idx*1024 
  
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

      send_buffer = dict()
      ak = 0

      while(True):
         finish = False
         f.seek(get_offset(ak))
         dt = f.read(buf)
         if dt:
            packet = FileFrame(ack = ak, data = dt)
            p = packet.pack()
            send_buffer[ak] = p
            print ak
            sock.sendto(p, addr)
         else:
            finish = True

         if ak % WINDOW_SIZE == WINDOW_SIZE - 1:
            while(True):
               try:
                  sock.settimeout(0.001)
                  p, addr = sock.recvfrom(4)
                  AckOrNack = AckFrame(buf = p)
                  if AckOrNack.ack == ak + 1:
                     break
                  else:
                     print "NACK ", AckOrNack.ack
                     sock.sendto(send_buffer[AckOrNack.ack], addr)

               except socket.timeout:
                  print "Time out ouccured Resend!"
                  ak = ak - WINDOW_SIZE 
                  break
         ak = ak + 1
         if finish:
            break

      
   finally:
      f.close()
      sock.close()