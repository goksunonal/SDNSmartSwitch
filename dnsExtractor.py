
# importing the module
import re
import socket
from threading import Thread
from queue import Queue
import threading, time

l=threading.Lock()
locked=False
textfile = open("dnsAdressesList.txt", "w+")

def function01(queue):  
   # declaring the regex pattern for IP addresses
   i = 0
   for site in iter(queue.get, None):
      try:
         addr=socket.gethostbyname(site)
         l.acquire()
         locked=True
         textfile.write(addr + '\n')
         textfile.flush()
         l.release()
         print("host writed:" + addr)
      except:
         print("host not found error:" + site)
         continue 

def test():
    while locked:
        time.sleep(1)
    #do something

def main():
   dnsLists=[]
   pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
   with open('url-list.txt') as fh:
      fstring = fh.readlines()
   i = 0
   # extracting the IP addresses
   for line in fstring:
      i = i + 1
      if i > 107935:
         ip = re.findall(pattern,line)
         i = i + 1   
         if len(ip) == 0:
            print("server address line:" + str(i))
            lineTrimmed=line.replace('\n','').strip()
            dnsLists.append(lineTrimmed)   

    # Spawn thread pool
   queue = Queue()
   threads = [Thread(target=function01, args=(queue,)) for _ in range(50)]
   for t in threads:
       t.daemon = True
       t.start()
    # Place work in queue
   for site in dnsLists: queue.put(site)
   # Put sentinel to signal the end
   for _ in threads: queue.put(None)
   # Wait for completion
   for t in threads: t.join()
   textfile.close()

        
main()
