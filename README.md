# python_contentdm_pitcher
This repository contains python scripts for use in automating updates to CONTENTdm items and exporting items for web-map vizualization through GeoJSON file generation.

# pitcher.py 
Used to updated existing item records in CONTENTdm through automation using the SOAP web service known as Catcher

# create_catcher_edit_csv.py
Takes a CSV file of exported CONTENTdm items and generates a new CSV file for use in automating updates to each item in pitcher.

# contentdm_collection_geojson.py
Takes a CONTENTdm collection, looks for geolocations in items and sub items, then generates a GeoJSON file for vizualization.