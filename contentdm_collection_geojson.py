# The following takes a CONTENTdm collection alias and polls all the items and subitems (inside compund objects) looking for geolocations.
# All CONTENTdm json responses saved to minimize overloading server. 
# If CONTENTdm records are updated, local json files should be removed to ensure fresh requests are made
# All geolocations are then saved as a geojson file

# Steps to use:
# call the contentdm_collection_geojson.py passing the following arguments
# -end_point_url: the url to the collection collection name
# -lat: string field in item for the latitude
# -lng: string field in item for the longitude
# -retain_fields: comma separated list of fields to retain. Parent (compound object) fields are checked along with child fields.
# -item_ids: (optional) comma separated top level items list if only looking for specific ones
# -output: the name of the output file
# -org_name: the name of the folder to store the files within 'data/harvested/' and for the collection json response

# an example call might look like
# python3 contentdm_collection_geojson.py -end_point_url "https://archives.mountainscholar.org/digital/api/search/collection/p17393coll164/maxRecords/10000" -lat latitu -lng longit -retain_keys title,creato,coveraa,date -org_name goslin -output "output.geojson"

import argparse
import csv

from FileCollection import FileCollection
import os.path
from os import path
import json

parser = argparse.ArgumentParser()
parser.add_argument("-end_point_url", help="")
parser.add_argument("-lat", help="")
parser.add_argument("-lng", help="")
parser.add_argument("-retain_keys", help="")
parser.add_argument("-org_name", help="")
parser.add_argument("-output", help="")
parser.add_argument("-item_ids", help="")
parser.add_argument("-overwrite", help="")


args = parser.parse_args()


class ContentDMCollectionHarvest:
    def __init__(self,props):
        for p in props:
            setattr(self,p, props[p])

        self.features=[]
    def load(self,props):
        # start by creating a folder to store the data we are harvesting
        if not path.exists(self.path):
            os.mkdir(self.path)
        # create the storage folder if it doesn't exists
        if not path.exists(self.path + self.data_folder):
            os.mkdir(self.path + self.data_folder)

        file_collection = FileCollection(props)
    def create_feature(self,obj):
        self.features.append(obj)

    def warp_it_up(self):
       output_json={ "type": 'FeatureCollection', "features": []}
       keys=args.retain_keys+",thumb_url,info_page".split(",")

       for o in self.features:
           obj_props={}
           for k in keys:
               if k !='' and k in o:
                   obj_props[k]=o[k]
          
           output_json["features"].append({ "type": 'Feature', "properties": obj_props,
           "geometry":{"type": 'Point',"coordinates": [float(o["lng"]),float(o["lat"])]}})

       f = open(self.output, 'w')
       f.write(json.dumps(output_json, indent=4))
       f.close()


harvest_props = {
    "path":"data/",
    "data_folder":"harvested",
    "output":args.output
}
print (harvest_props)
harvester = ContentDMCollectionHarvest(harvest_props)

if args.item_ids:
    args.item_ids=args.item_ids.split(",")

if args.retain_keys:
    args.retain_keys=args.retain_keys.split(",")


load_props = {
    "end_point_url":args.end_point_url,
    "lat":args.lat,
    "lng":args.lng,
    "retain_keys":args.retain_keys,
    "org_name": args.org_name,
    "path":harvest_props["path"]+harvest_props["data_folder"]+"/",
    "resource_ids":args.item_ids,
    "overwrite":args.overwrite,
    "harvester":harvester
}
harvester.load(load_props)

