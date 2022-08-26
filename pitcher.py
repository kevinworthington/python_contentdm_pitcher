#!/usr/bin/python3
# The following script is used to updated existing item records in CONTENTdm through automation using the SOAP web service known as Catcher.


# To use: update the settings.py file with your username, password, contentdm licence and the base url for you CONTENTdm server
#   Then add rows to the CatcherUpload.csv for each item update, see below for a description of the csv file.
#   Call the pitcher.py file using 'python3 pitcher.py' from the terminal

# Once complete a log of the transations will be placed in a folder called 'Completed'
# A limitation of this program is that once a record edit is made, it becomes locked, preventing additionals edits to the same record
# Indexing of items allows the item change to take effect whihc unlocks the edited record 
#   Navigating to items>index>and clicking "index now" will trigger reindexing


# This script takes a csv file of updates with four fields: 
#   Alias: The CONTENTdm collection internal name for the item to be updateds. This can be found in the URL for the item. 
#   CDM_id: The item's intenal id. Can be pulled from an export of the collection. 
#   CDM_field: The metadata attribute/field name to be changed. Note these are truncated to 5-6 lowercase characters. 
#       Can be verified from the CONTENTdm Administration interface under: 
#       'Collection administration'>'Field Properties'>'edit'(next to the field to be updated)
#        Then on the 'edit field' page, take the string in the browser address after the '='
#            e.g https://....org/cgi-bin/admin/editfield.exe?CISODB=/p17393coll164&CISONICK=latitu
#            Should be 'latitu'
#   Value: the new value to be added
# Note: one value per row 
# Script set to iterate through the current directory and process any csv files beginning with "CatcherUpload"
# Transaction files are output to "Completed" directory with timestamp.

# Adapted from https://gist.github.com/saverkamp/9198310
# Original Author: Shawn Averkamp, 2014-02-24 


# Updated to Python 3 by: Kevin Worthington, Colroado State University

# OCLS Catcher Documentation: 
# https://help.oclc.org/@api/deki/pages/12875/pdf/Guide%2bto%2bthe%2bCONTENTdm%2bCatcher.pdf?stylesheet=default
# https://help.oclc.org/Metadata_Services/CONTENTdm/CONTENTdm_Catcher/Download_the_CONTENTdm_Catcher?sl=en 
# https://help.oclc.org/Metadata_Services/CONTENTdm/CONTENTdm_Catcher/Guide_to_the_CONTENTdm_Catcher


# Last modified: 2022-08-26 

import urllib
import urllib.request
from suds.client import Client
from suds.transport.https import HttpAuthenticated
from suds.transport import TransportError
import datetime
import csv
import os
import fnmatch
import socket

# set variables for SOAP connection--requires config.ini file

from settings import *

port = '8888'# was '81' you should not need to update
url = base + ":" + port
WSDL='https://www.oclc.org/content/dam/community/CONTENTdm/downloads-addons/CatcherService.xml'
#WSDL='https://worldcat.org/webservices/contentdm/catcher/6.0/CatcherService.wsdl'

# https://stackoverflow.com/questions/25083855/403-when-retrieving-a-wsdl-via-python-suds
class HttpHeaderModify(HttpAuthenticated):
    def open(self, request):
        try:
            url = request.url
            u2request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla'})
            self.proxy = self.options.proxy
            return self.u2open(u2request)
        except urllib.error.HTTPError as e:
            raise TransportError(str(e), e.code, e.fp)
        except socket.timeout as err:
            print(err)


class Catcher(object):
    """A CONTENTdm Catcher session."""
    def __init__(self, url=url, user=user, password=password, license=license):
        print("init...")
        self.transactions = []
        self.client = Client(WSDL, transport=HttpHeaderModify(), timeout=100)
        self.client.set_options(headers={'User-Agent': 'Mozilla'})
        print(self.client)
        self.url = url
        self.user = user
        self.password = password
        self.license = license
     
    def processCONTENTdm(self, action, user, password, license, alias, metadata):
    # function to connect to CatcherServices and process metadata updates
        transaction = self.client.service.processCONTENTdm(action, url, user, password, license, alias, metadata)
        self.transactions.append(transaction)
     
    def edit(self, alias, recordid, field, value):
    #function to edit metadata--call packageMetadata and processCONTENTdm
        metadata = self.packageMetadata('edit', recordid, field, value)
        self.processCONTENTdm('edit', self.user, self.password, self.license, alias, metadata)
     
    def packageMetadata(self, action, recordid, field, value):
    #function to package metadata in metadata wrapper
        action = action
        if action == 'edit':
            metadata = self.client.factory.create('metadataWrapper')
            metadata.metadataList = self.client.factory.create('metadataWrapper.metadataList')
            metadata1 = self.client.factory.create('metadata')
            metadata1.field = 'dmrecord'
            metadata1.value = recordid
            metadata2 = self.client.factory.create('metadata')
            metadata2.field = field
            metadata2.value = value
            metadata.metadataList.metadata = [metadata1, metadata2]
        return metadata

def UnicodeDictReader(str_data, encoding, **kwargs):
    return csv.DictReader(str_data, **kwargs)
    # # Decode the keys once
    # keymap = dict((k, k.decode(encoding)) for k in csv_reader.fieldnames)
    # for row in csv_reader:
    #     yield dict((keymap[k], v.decode(encoding)) for k, v in row.iteritems())

#iterate through current directory to find any files starting with 'CatcherUpload' and process
for file in os.listdir('.'):
    if fnmatch.fnmatch(file, 'CatcherUpload*.csv'):
        csvfile = open(file, 'r')
        c = UnicodeDictReader(csvfile, encoding='utf-8')

        # create directory for completed files and transaction logs if it doesn't exist
        newdir = 'Completed'
        if not os.path.isdir(newdir):
            os.mkdir(newdir)

        # create csv file for transactions
        today = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')
        fname = 'Completed/Transactions_' + file[0:-4] + '_' + today + '.csv'
        f = open(fname, 'w')
        fwtr = csv.writer(f)
        header = ['Alias', 'CDM_id', 'CDM_field', 'Transaction']
        fwtr.writerow(header)

        #initialize Catcher session
        session = Catcher({})

        #iterate through rows in csv and process through Catcher
        for row in c:
            # get values from row and package metadata for edits
            cdmid = row['CDM_page_id']
            alias = row['Alias']
            field = row['CDM_field']
            value = row['Value']
            # package metadata for Catcher and upload if value is not empty
            if value != '':
                print("Attempting",alias, cdmid, field, value)
                session.edit(alias, cdmid, field, value)     
                # write transaction message to file
                fRow = [alias, cdmid, field, session.transactions[-1]]
            else:
                fRow = [alias, cdmid, field, 'No content--not uploaded']
            fwtr.writerow(fRow)

        f.close()
        csvfile.close()
        # append timestamp to upload csv filename and move to Completed directory
        # newcsv = 'Completed/' + file[0:-4] + '_' + today + '.csv'
        # oldfile = file
        # os.rename(oldfile, newcsv)