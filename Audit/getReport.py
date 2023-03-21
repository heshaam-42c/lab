import base64
import json
import requests
import sys
import time
import yaml
import os
from decouple import config
from tabulate import tabulate
from datetime import datetime

# Set vars
if len(sys.argv) > 1: # Used for github actions env
    x42confPath = '42c-conf.yaml'
    apikey = sys.argv[2]
    reportPath = 'Audit/report.rtf'
else: # Local
    x42confPath = '../42c-conf.yaml'
    apikey = config('42C_API_TOKEN')
    reportPath = 'report.rtf'

# Set authentication header
headers = {'X-API-KEY': apikey}

# Open 42c-conf.yaml
with open(x42confPath, 'r') as file:
    confYaml = yaml.safe_load(file)

# Get API uuid from 42c-conf.yaml
uuid = confYaml['audit']['branches']['main']['mapping']['Pixi/pixi.json']

# Run audit
url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assess'
r = requests.get(url, headers=headers)
jsonResponse = r.json()

# Get taskId
taskId = jsonResponse['id']
time.sleep(2)

# Get SQG approval report using taskId
url = 'https://demolabs.42crunch.cloud/api/v2/sqgs/reportComplianceStatus?reportType=audit&taskId='+taskId
r = requests.get(url, headers=headers)
jsonResponse = r.json()
print(jsonResponse)

# Parse response
if jsonResponse['acceptance'] == 'no':
    fileString = 'Audit SQGs - FAILED :sad:'
else:
    fileString = 'Audit SQGs - PASSED :happy:'

fileString += '\nTimestamp: '+str(datetime.fromtimestamp(int(jsonResponse['date'])))

fileString += '\n\nReport: https://demolabs.42crunch.cloud/apis/'+jsonResponse['api']+'/security-audit-report'

fileString += '\n\n'+tabulate([], headers=['Failed SQGs'], tablefmt='github')

sqgTable = []
head = ['SQG Id', 'Blocking Rule']

# Build report table
for sqg in jsonResponse['processingDetails']:
    # Get SQG details
    url = 'https://demolabs.42crunch.cloud/api/v2/sqgs/audit/'+sqg['blockingSqgId']
    r = requests.get(url, headers=headers)
    sqgIdJson = r.json()

    for count, rule in enumerate(sqg['blockingRules']):
        if count == 0:
            appendRow = [sqgIdJson['name'], rule]
        else:
            appendRow = ['', rule]
        sqgTable.append(appendRow)
    fileString += '\n'

fileString += tabulate(sqgTable, headers=head, tablefmt='github')

# Write to file
f = open(reportPath,'w')
f.write(fileString)

# Get audit report
#url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assessmentreport'
#headers = {'X-API-KEY': apikey}
#r = requests.get(url, headers=headers)
#jsonResponse = r.json()

# Decode response
#decodedBytes = base64.b64decode(jsonResponse['data'])
#decodedStr = decodedBytes.decode('ascii')

# Create Python object from JSON string data
#obj = json.loads(decodedStr)['summary']

#...
#f.write(json.dumps(obj, indent=4))