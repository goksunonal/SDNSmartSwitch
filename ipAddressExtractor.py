
# importing the module
import re
  
# opening and reading the file 
with open('url-list.txt') as fh:
   fstring = fh.readlines()

# declaring the regex pattern for IP addresses
pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')


textfile = open("ipAddressesList.txt", "w")
  
# extracting the IP addresses
for line in fstring:
   ip = re.findall(pattern,line)
   if len(ip) != 0:
   	textfile.write(ip[0])
   	textfile.write('\n')  
