# The following script takes a CSV file of exported CONTENTdm item records and generates a new CSV file for use in 
# automating updates to each item in pitcher.

# Steps to use:
# call the create_catcher_edit_csv.py passing the following arguments
# -source_file, sf: the file to be used as input
# -alias: string for the internal collection name
# -column_name: string field in item to be updated
# -value_column: the column header name in the CSV file containing the value
# -id: the item id: the column header name in the CSV file containing the item id
# -output: output file, should start with 'CatcherUpload' for use in pitcher

# an example call might look like
# python3 create_catcher_edit_csv.py -source_file "goslin export.xlsx - filtered goslin export.csv" -alias p17393coll164 -column_name latitu -value_column lat -id "CONTENTdm number" -output "CatcherUpload_edits.csv"


import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("-source_file", help="")
parser.add_argument("-alias", help="")
parser.add_argument("-column_name", help="")
parser.add_argument("-value_column", help="")
parser.add_argument("-id", help="")
parser.add_argument("-output", help="")

args = parser.parse_args()

# create file with heading - Alias,CDM_page_id,CDM_field,Value
#Input
inpute_file=open( args.source_file, 'r' ) 
csv_reader = csv.DictReader(inpute_file)

#output
f = open(args.output, 'w')
fwtr = csv.writer(f)
header = ['Alias','CDM_page_id','CDM_field','Value']
fwtr.writerow(header)

for row in csv_reader:
        # get values from row and package metadata for edits
        fwtr.writerow([args.alias,row[args.id],args.column_name,row[args.value_column]])


f.close()
inpute_file.close()