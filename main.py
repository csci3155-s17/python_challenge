#!/usr/bin/env/python
#Requirements:
#Create a program that will read a given set of IPs, perform Geo IP and RDAP lookups, and accept a query to filter results.
#
#Objectives:
#This exercise is designed to test your ability to:
#  Take abstract requirements and run with them
#  Write isolated decoupled modules with strict input/output interfaces
#  Create a query language and algorithm for filtering
#  Reading, parsing, and extracting IP addresses from unstructured text in an efficient manner
#  Once you are done, please post your code on Github named something like:
#  https://github.com/*profileID*/python_challenge (do not include swimlane in the url)
#Technical:
#  Each component (GeoIP/RDAP/Filter/Parsing) should be as decoupled from the others as possible while still being easy to use.
#  The main function should parse a text file containing 5000 IP addresses spread throughout random text.
#  The filter component should provide a custom query language allowing the user to easily filter through the results provided.
#  Do not use 3rd party packages that provide complete solutions for GeoIP queries, RDAP queries, or filtering. Libraries simplifying HTTP requests, data manipulation, etc. are acceptable.
#  Bonus points for simple, clever, and performant solutions, and any extras like unit tests, docs, multiple output formats, result caching, web UI, cli, etc. Be creative.




import re
import requests
import sys
import numbers
import json
import ast
import pickle
import os
from requests.exceptions import ConnectionError

datafile="databse.txt"


#This function takes in a file to parse from and pulls out as many ip addresses
#that are found in the file using regex
def parse(filename, printout):
    regex = re.compile("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
    ips=[]
    with open(filename) as f:
        for line in f:
            result = regex.findall(line)
            if result:
                ips = ips + result


    #This part allows proof of concept for parsing the IPs
    if printout:
        print ips
        print "Num of ips = " + str(len(ips))
    f.close()
    return ips



# This function looks up an IP with the GEO or RDAP api as given by the api varaible
# the ip variable is a singe ip address to be looked up.
def iplookup(ip, api):
    if api == "RDAP":
        url = "https://rdap.arin.net/bootstrap/ip/" + ip
    if api == "GEO":
        url = "http://freegeoip.net/json/" + ip

    try:
        result = requests.get(url, timeout=8)
    except:
        print "ERROR FETCHING: Exception caught" + url
        result = "NONE"
        return result
    if result.status_code == 200:
        return result.json()
    else:
        print("ERROR FETCHING: bad status code " + url)
        return "NONE"



# This function allows parsing of the database as well as sending results to file
# command: the keys to search for
# database: the database to search in
# tofile: boolean that sets wether we are writing results to file
# filename: file to write to




def query(command, database, tofile, filename):
    filter=command.replace(" ","").split(",")
    if tofile:
        print "Sending query to "+filename
        try:
            os.remove(filename)
        except OSError:
            pass

    else:
        print "~~~~~~~~~~"
        print "~Database~"
        print "~~~~~~~~~~"
        print "Filters: " + command
        print "~~~~~~~~~~\n"

    found = False
    dictout = {}
    for item in database:
        if found == True:
            if not tofile:
                print "___+___+___+___+___+___+___\n"
        for key, value in item.iteritems():
            if key in filter:
                found = True
                if value == "":
                    value = "NONE"
                if tofile:
                    info = str(key) + " : " + str(value) + "\n"
                    with open(filename, 'a') as f:
                        f.write(info)
                else:
                    print str(key) + " : " + str(value)



# This funciton prints the database or sends it to a file
# database: is the database to print
# tofile: Boolean stating wether to send to file (True=send to file)
# filename: file to write to

def printdatabase(database, tofile, filename):
    if tofile:
        with open(filename, 'w') as f:
            f.write(json.dumps(database, sort_keys = True, indent=4))
    else:
        print "~~~~~~~~~~"
        print "~Database~"
        print "~~~~~~~~~~"
        print "Filters: NONE"
        print "~~~~~~~~~~\n"
        print json.dumps(database, sort_keys = True, indent=4)





# This function creates a database from parsed ips using command line argumet as the
# on the number of ips parsed (lookup can take a long time with 5000 ips)
#


def createDB(limit):
    IPAddresses = parse("list_of_ips.txt", False)
    if int(limit) > len(IPAddresses):
        limit = len(IPAddresses)
    infolist = []
    val = 0
    for ip in IPAddresses:
        georesult = iplookup(ip, "GEO")
        rdapresult = iplookup(ip, "RDAP")
        fullresult = {}
        if georesult != "NONE":
            fullresult.update(georesult)
        if rdapresult != "NONE":
            fullresult.update(rdapresult)
        infolist.append(fullresult)
        if int(val) == int(limit):
            break
        val+=1
    return infolist


# accepts database from file instead of parsing new database
#
#
def loadDB(filename):
    with open (filename, 'rb') as fp:
        itemlist = pickle.load(fp)
    return itemlist

def main():
    if len(sys.argv)>=2:
        try:
            limit = int(sys.argv[1])
        except:
            print "ERROR: The limit you entered was not an integer"
            print "USAGE: python main.py <integer>"
            return
    else:
        limit = 5000
    command = "none"
    while(command!="q"):
        print "_______________________________________________________"
        print "type 'p' to create database from list_of_ips.txt\ntype 'a' to show all\ntype 'l' to load last save\ntype 's' to save database\ntype 'o' to send query to text file\ntype 'q' to exit\nOR"
        command = raw_input("type your filters seperated by commas: ")
        print "_______________________________________________________"
        if command == "p":
            database = createDB(limit)
            print "Database Parsed from text file"
            continue

        if command == "l":
            try:
                database = loadDB(datafile)
                print "Database Loaded"
            except Exception,e:
                print str(e)
                print "Error: No saved database to load"
            continue

        try:
            database
        except:
            print "Database not loaded yet"
            continue

        if command == "a":
            printdatabase(database, False, "none")
            continue

        if command == "s":
            with open(datafile, 'wb') as f:
                pickle.dump(database, f)
            f.close
            print "Database Saved"
            continue

        if command == "o":
            cmd = raw_input("type 'a' to output whole database, type filters seperated by comma to output filtered results: \n")
            filen = raw_input("type desired file name: ")
            if cmd == "a":
                printdatabase(database, True, filen)

            else:
                query(cmd, database, True, filen)
            print "Output Written"
            continue

        if command!="q":
            query(command, database, False, "none")

    print "Goodbye!"



if __name__ == "__main__":
    main()
