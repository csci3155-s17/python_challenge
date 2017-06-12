This program parses 5000 ip addresses from a text file list_of_ips.txt,
performs Geoip and RDAP lookups on the ip address, then offers the option to filter
the results by a given set of keys.
___________________________________________________________
To Run:
python main.py

OR

python main.py <max # of ips you wish to parse>
___________________________________________________________
Once executed the program allows the following interactions

p: show fully parsed ip list

a: show entire database

l: load saved database

s: save database

o: send query to text file
      a: send all to text file
      key1, key2, key3:  send custom query to text file

key1, key2, key3:     show only key1 : value1, key2 : value2, and key3 : value3 for each existing ip in database


q: quit
___________________________________________________________
