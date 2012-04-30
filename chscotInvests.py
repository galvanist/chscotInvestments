import sys
import csv
import string
import re
import requests
import json
import time
from xml.sax.saxutils import escape

investsFile = open('investsCombined.csv','rU') #r = read, b = binary, U = universal (e.g. multilines)
invests = csv.DictReader(investsFile, delimiter=',', dialect='excel')

counter = {}
amounts = {}
validCount = 0
invalidCount = 0
valid = []
errors = []

for row in invests:
    #postcode = row[7]
    #amt = row[2]
    postcode = row['postcode'].upper().strip(' \t\n\r')
    amt = row['amount']
    name = row['applicant_name'].strip(' \t\n\r')
    postcodeSplit = postcode.split(" ")
    if len(amt) > 0 and amt > 0:
        if len(postcodeSplit) > 1 and re.match(r'^([A-PR-UWYZ0-9][A-HK-Y0-9][AEHMNPRTVXY0-9]?[ABEHMNPRVWXY0-9]? {1,2}[0-9][ABD-HJLN-UW-Z]{2}|GIR 0AA)$',postcode):
            postcodeArea = string.upper(postcodeSplit[0]+" "+postcodeSplit[1][:1])
            if not postcodeArea in counter:
                counter[postcodeArea] = 1
            else:
                counter[postcodeArea] += 1
            if not postcodeArea in amounts:
                amounts[postcodeArea] = float(amt)
            else:
                amounts[postcodeArea] += float(amt)
            validCount += 1
            row['postcode'] = postcode
            row['name'] = name
            valid.append(row)
        else:
            errors.append('postcode ['+postcode+'] invalid for '+name)
            invalidCount += 1
    else:
        errors.append('amount ['+amt+'] not acceptable for '+name)
        invalidCount += 1

assert len(counter) == len(amounts)
assert validCount == len(valid)

#for error in errors:
    #print error
#print
#print 'number of areas: '+str(len(counter))
#print 'valid names: '+str(validCount)
#print 'invalid names: '+str(invalidCount)
# Celtic Colours Festival Society [B1P 5T9] appears to be in Canada
#sys.exit(0)

# do this once and put it in a csv (do not hammer google every time)
#for row in valid:
    #r = requests.get('http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='+row['postcode'])
    #d = json.loads(r.text)
    #lat = d['results'][0]['geometry']['location']['lat']
    #lng = d['results'][0]['geometry']['location']['lng']
    #print row['postcode']+','+str(lat)+','+str(lng)
    #time.sleep(0.5)

# Google API thinks PA45 5TT in Germany, should have used 'UK' in search, manual overwrite with 55.86894220,-6.04611130

postcodesFile = open('latlngs.csv','r') #r = read, b = binary, U = universal (e.g. multilines)
postcodesCSV = csv.reader(postcodesFile, delimiter=',')

postcodes = {}

for postcodeRow in postcodesCSV:
    postcodes[postcodeRow[0]] = [postcodeRow[1],postcodeRow[2]]

print '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
    <name>Culture Hack Creative Scotland Investments</name>
    <description>Map of all the pinable (postcoded) investments made by Creative Scotland</description>
    <open>1</open>
'''

print '<Folder><name>Investments</name>'
for row in valid:
    if row['project_title'].strip() != '':
        name = row['applicant_name'].strip()+" - "+row['project_title'].strip()
    else:
        name = row['applicant_name'].strip()
    descr = row['description'].strip()+" (Value of "+row['amount'].strip()+" awarded "+row['decision_date'].strip()+")"
    print '<Placemark><name>'+escape(name)+'</name><description>'+escape(descr)+'</description><styleUrl>#BalloonStyle</styleUrl><Point><coordinates>'+postcodes[row['postcode']][1]+','+postcodes[row['postcode']][0]+',0</coordinates></Point></Placemark>'
print '</Folder>'

print '</Document></kml>'