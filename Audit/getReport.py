import base64
import json
import requests
import sys
import time
import yaml

apikey = 'api_59cc0133-9c5d-4301-8cd9-8e27c62edea1'

if sys.argv[1] == 'github':
    x42confPath = '42c-conf.yaml'
else:
    x42confPath = '../42c-conf.yaml'

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

if sys.argv[1] == 'github':
    reportPath = 'Audit/report.txt'
else:
    reportPath = 'report.txt'

# Write to file
f = open(reportPath,'w')
f.write("Audit SQG report - Date: "+jsonResponse['date'])
f.write("\n\nAPI UUID: " + jsonResponse['api'])
f.write("\nPassed: " + jsonResponse['acceptance'])

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