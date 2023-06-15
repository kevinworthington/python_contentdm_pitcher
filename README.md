# Python CONTENTdm Item Updating with Automation
This repository contains python scripts for use in automating updates to CONTENTdm items.
Any field can be updated, using the following approach, though the purpose of this project was to add geospatial coordinates to CONTENTdm items so they can be viewed on a clickable map.

## Instructions for use
Step 1. Export a CSV file of the metadata for the collection in CONTENTdm to be updated
1. Navigate to the CONTENTdm Administration webpage and log-in
1. *Click* the **collections** Tab from the top of the page
1. *Select* the collection to be exported from the **Current collection** dropdown and *click* **Change**
1. *Click* the **export** link
1. *Click* the **check-box** for "Return field names in first record" and then *Click* next
1. *Open* the CSV file in your favorite spreadsheet program, update the fields you desire, and *save*
    - Note: If you only need to update a subset of the collection items, remove the lines to be left unchanged

Step 2. Take the CSV file of updated CONTENTdm items and generate a new CSV file for use in automating the updates.
1. With git installed on your computer, *open* the command line and enter 'git clone https://github.com/kevinworthington/python_contentdm_pitcher.git'
2. Update the *settings.py* file 
   - Enter the same log-in information used to access the CONTENTdm Administration webpage
   - The License code can be retrieved from the CONTENTdm Administration webpage under the **server** tab, and then by *selecting* the **about** link
   - Replace the "{server_url}" text with the "server####" name taken from the URL of the CONTENTdm Administration webpage
3. Run the create_catcher_edit_csv.py to create the CatcherUpload_edits.csv file
   - Note: This file is formatted with one edit per line as required by the CONTENTdm SOAP webservice, known as Catcher, which allows us to make the updates
   - From within the command line, paste the following text between the single quotes and then *press* the **Enter** key: 'python3 create_catcher_edit_csv.py -source_file "{input.csv}" -alias {collection alias} -column_name {column_name} -value_column {value_column} -id "CONTENTdm number" -output "CatcherUpload_edits.csv"'
    - After replacing: 
        - {input.csv}: with the CSV file containing the updated metadata records
        - {collection alias}: this can be found by taking the characters between "/collection/" and "/id/" from the *Reference URL* column of any of the items in the exported CSV file 
        - {column_name}: with the string field to be updated
            - note these are a lowercase, 6 character truncations of the column name
            - If in doubt of the correct name:
                - You can confirm it within CONTENTdm Administration, with the collection selected
                - *click* **fields**
                - Then next to the field you'd like to have updated, *click* **edit**
                - Now, the address bar at the top of page end with this truncated representation of the field, which is everything after the "=" sign
        - {value_column} the column header name in the CSV file containing the value
Step 3. With the "CatcherUpload_edits.csv" file created, we're ready to call the file that actually updates the CONTENTdm records
1. From within the command line, paste the following text between the single quotes and then *press* the **Enter** key 'python3 pitcher.py'
*Note: once complete, a log of the transactions will be placed in a folder called 'Completed'*
- A limitation of this program is that once a record edit is made, it becomes locked, preventing additional edits to the same record 
  - Indexing of items allows the item change to take effect which unlocks the edited record
   - Navigating to items>index>and clicking "index now" will trigger reindexing    

Once reindexing has completed, your updates are now available online    

## Mapping CONTENTdm items
Here are instructions on how to create an interactive map within CONTENTdm once they have location information https://help.oclc.org/Metadata_Services/CONTENTdm/Advanced_website_customization/Customization_cookbook/Display_items_on_clickable_maps
It should be noted that this works for non-nested records. 

If items you'd like to map are part of a composite item, the *contentdm_collection_geojson.py* script is for you!
This script takes a CONTENTdm collection, looks for geolocations in items and sub items, then generates a GeoJSON file for visualization.

