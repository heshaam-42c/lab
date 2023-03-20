import base64
import json
import requests
import sys

uuid = '9273b0fc-ab90-4325-9fcb-a6f504e07840'
apikey = 'api_59cc0133-9c5d-4301-8cd9-8e27c62edea1'

# Get audit report
url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assessmentreport'
headers = {'X-API-KEY': apikey}
r = requests.get(url, headers=headers)
jsonResponse = r.json()

# Decode response
decodedBytes = base64.b64decode(jsonResponse["data"])
decodedStr = decodedBytes.decode("ascii")

# Create Python object from JSON string data
obj = json.loads(decodedStr)["summary"]

if sys.argv[1] == 'local':
    f = open('report.json','w')
elif sys.argv[1] == 'github':
    f = open('Audit/report.json','w')

# Write to file
f.write("Summary")
f.write(json.dumps(obj, indent=4))