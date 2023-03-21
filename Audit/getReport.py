import base64
import json
import requests
import sys
import time
import yaml
import os
from decouple import config

# Set vars
if len(sys.argv) > 1: # Used for github actions env
    x42confPath = '42c-conf.yaml'
    apikey = sys.argv[2]
    reportPath = 'Audit/report.txt'
else: # Local
    x42confPath = '../42c-conf.yaml'
    apikey = config('42C_API_TOKEN')
    reportPath = 'report.txt'

with open(x42confPath, 'r') as file:
    confYaml = yaml.safe_load(file)

uuid = confYaml['audit']['branches']['main']['mapping']['Pixi/pixi.json']

# Run audit
url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assess'
headers = {'X-API-KEY': apikey}
r = requests.get(url, headers=headers)
jsonResponse = r.json()

taskId = jsonResponse['id']
time.sleep(2)

# Get SQG approval report
url = 'https://demolabs.42crunch.cloud/api/v2/sqgs/reportComplianceStatus?reportType=audit&taskId='+taskId
r = requests.get(url, headers=headers)
jsonResponse = r.json()
print("SQG response: \n")
print(jsonResponse)

# Write to file
f = open(reportPath,'w')
f.write("Audit SQG report - Date: "+jsonResponse['date'])
f.write("\nPassed? " + jsonResponse['acceptance'])
f.write("\n\nAPI UUID: " + jsonResponse['api'])

f.write("\n\nFailed SQGs -")
for sqg in jsonResponse['processingDetails']:
    f.write("\n"+sqg['blockingSqgId'])
    for count, rule in enumerate(sqg['blockingRules']):
        f.write("\n"+str(count+1)+".) "+rule)
    f.write("\n")

# Get audit report
#url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assessmentreport'
#headers = {'X-API-KEY': apikey}
#r = requests.get(url, headers=headers)
#jsonResponse = r.json()

# Decode response
#decodedBytes = base64.b64decode(jsonResponse["data"])
#decodedStr = decodedBytes.decode("ascii")

# Create Python object from JSON string data
#obj = json.loads(decodedStr)["summary"]

#...
#f.write(json.dumps(obj, indent=4))