import base64
import json
import requests

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

# Write to file
f = open('Audit/report.json','w')
f.write(json.dumps(obj, indent=4))