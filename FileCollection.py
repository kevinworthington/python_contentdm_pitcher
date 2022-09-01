"""
The super class FileCollection is used to handle json file loading/saving and database ingestion through Change Management System

"""

import urllib.request, json
import ssl
import os.path
from os import path

from datetime import datetime

class FileCollection:
    '''
    Control the REST requests and the passed params
    '''
    def __init__(self,props):
        # take the end point and start loading the data
        for p in props:
            setattr(self, p, props[p])

        self.start=1
        self.page = 1
        self.total=None
        self.folder = self.org_name
        self.loaded_resource_ids = []

        if not path.exists(self.path+self.folder):
            os.mkdir(self.path+self.folder)

        self.open_prefix = self.end_point_url[:self.end_point_url.index("/api")]

        self.load_results()

    def load_results(self):
        # declare the folder and file names
        folder_path=self.path+self.folder+"/"
        file=self.org_name+".json"
        _file = folder_path + file
        #check if the data exists
        url = self.end_point_url
        self.load_file_call_func( _file, url,'check_loaded')



    def check_loaded(self,data, parent_obj=False):
        """

        :param data:
        :param parent_obj:
        :return:
        """
        # scan the json looking for how many records have been downloaded
        # can setup the next request if there are more pages to be downloaded

        self.drill_loaded_data(data)

    def drill_loaded_data(self, data):
        """

        :param data:
        :return:
        """
        # start by making sure a 'layers' folder exists
        layers_path = self.path + self.folder + "/layers"
        if not path.exists(layers_path):
            os.mkdir(layers_path)



        for index, r in enumerate(data['items']):
            # todo  - remove when done testing
            # if index >1:
            #     break
            id = r['itemId']

            if self.resource_ids:
                # only load specified resource ids
                for r_id in self.resource_ids:
                    if r_id == id:
                        self.load_data(id, r, layers_path)

            else:
                self.load_data(id, r, layers_path)

    def load_file_call_func(self, _file, _url, _func, parent_obj=False):
        """

        :param _file: the name (w/ path) of the file to save
        :param _url: the absolute URL to the json
        :param _func: The function to call upon completion
        :param parent_obj: extra info to retain when loading
        :return: None
        """
        if not path.exists(_file) or self.overwrite:
            # setup the url to load each request
            print("loading file", _url)
            if _url.startswith("//"):
                _url="https:"+_url
            urllib.request.urlretrieve(_url, _file)
            try:
                context = ssl._create_unverified_context()
                response = urllib.request.urlopen(_url, context=context)
                with open(_file, 'w', encoding='utf-8') as outfile:
                    try:
                        outfile.write(json.dumps(json.loads(response.read().decode('utf-8')), indent=4, sort_keys=True))
                    except:
                        outfile.write(response.read().decode('utf-8'))
                self.load_file(_file, _func, parent_obj)

            except ssl.CertificateError as e:
                print("Data portal URL does not exist: " + _url)

        else:
            # load the file
            self.load_file(_file,_func, parent_obj)

    def load_data(self,id,r,layers_path):
        """
        :param id:
        :param r:
        :param layers_path:
        :return:
        """
        _file = layers_path + "/" + id + ".json"
        # use the 'thumbnailUri' excluding the end to consistently load metadata for both 'compoundobject' and 'singleitem'
        _url = self.open_prefix + r['thumbnailUri'][:r['thumbnailUri'].index("/thumbnail")]
        print(_url)
        self.load_file_call_func(_file, _url, 'check_sub_loaded', r)

    def check_sub_loaded(self,data,parent_obj):
        """
        We're going a level deeper here and looking at the layers associated with a record
        We'll create only parent records and associate the children (if they exist beneath).

        :param data: the sub information to be used in creating more informative compound records
        :param parent_obj:
        :return:
        """


        layers_path = self.path + self.folder + "/layers"
        if "page" in data['objectInfo'] or "node" in data['objectInfo'] :
            print("There are children here ---------------")

            # todo - associate the children - all details exist in the 'data'
            #generate urls for all children
            root_path = self.open_prefix+data['thumbnailUri'][:data['thumbnailUri'].index("/id/")+4]

            if "node" in data['objectInfo']:
                child_list = data['objectInfo']["node"]["page"]
            else:
                #make sure there are more than 1 pages
                if isinstance(data['objectInfo']["page"], list):
                    child_list=data['objectInfo']["page"]
                else:
                    child_list = [data['objectInfo']["page"]]

            for index, p in enumerate(child_list):

                # todo get the parent id
                # create a child resource with only new information - the ingest should take the parent info and combine it with the child
                parent_id = parent_obj["itemId"]
                item_id = p["pageptr"]
                _file = layers_path + "/" + parent_id + "_sub_"+item_id+".json"
                _url = root_path+item_id
                # todo - decide if we want to save the 3  metadata files
                print("About to load child url",_url)
                self.load_file_call_func(_file, _url, 'check_sub_sub_loaded', parent_obj)

        self.harvester.warp_it_up()


    def check_sub_sub_loaded(self,data, parent_obj):
        """

        :param data:
        :param parent_obj:
        :return:
        """
        # now that we've loaded the child information look for the lat and lng
        # start by creating a temp object to storethe data
        obj={
            "thumb_url":self.open_prefix+data["thumbnailUri"],
            "info_page": self.open_prefix + data["thumbnailUri"][data["thumbnailUri"].index("/collection"):data["thumbnailUri"].index("/thumbnail")],
            "lat":None,
            "lng":None
        }
        # start by looking for the keys in the parent to map onto the child
        for f in parent_obj['metadataFields']:
            for r in self.retain_keys:
                 if f['field'] == r:
                    obj[r]=f["value"]

        #now pull from the child
        for f in data["fields"]:
            if f["key"] == self.lat:
               obj["lat"]=f["value"]
            if f["key"] == self.lng:
               obj["lng"]=f["value"]
            for r in self.retain_keys:
                 if f["key"] == r:
                    obj[r]=f["value"]

        

        if obj["lat"] and obj["lng"]:
            self.harvester.create_feature(obj)

    def load_file(self,_file, _func, parent_obj=False):
        """

        :param _file: : The name (w/ path) of the file to save - relayed from "load_file_call_func"
        :param _func: _func: The function to call upon completion - relayed from "load_file_call_func"
        :param parent_obj: Extra info to retain when loading - relayed from "load_file_call_func"
        :return: None
        """
        try:
            _json = self.open_json(_file)
        except:

            _json = self.parse_json(_file)

        getattr(self, _func)(_json, parent_obj)

    def open_json(self,_file):
        """

        :param _file: The name (w/ path) of the local file to open
        :return: interprets text as JSON
        """
        try:
            outfile = open(_file)
            _json = json.load(outfile)
            outfile.close()
            return _json
        except:
            raise


    def parse_json(self,_file):
        """
        Extracts the JSON form malformed file
        :param _file: The name (w/ path) of the local file to open
        :return: A JSON file
        """
        outfile = open(_file)
        s = outfile.read()
        _json = s[s.find("(") + 1:s.rfind(")")]
        outfile.close()
        return json.loads(_json)

  