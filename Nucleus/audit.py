import base64
import json
import requests
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

#load environment vars
apikey = os.getenv('42C_API_TOKEN')
uuid = os.getenv('API_UUID')
platformUrl = os.getenv('PLATFORM_URL')
reportPath = 'auditReport.rtf'

# Set authentication header
headers = {'X-API-KEY': apikey}

# Run audit
url = platformUrl+'/api/v1/apis/'+uuid+'/assess'
r = requests.get(url, headers=headers)
jsonResponse = r.json()

# Get audit report
url = platformUrl+'/api/v1/apis/'+uuid+'/assessmentreport'
r = requests.get(url, headers=headers)
jsonResponse = r.json()

# Decode response
decodedBytes = base64.b64decode(jsonResponse['data'])
decodedStr = decodedBytes.decode('ascii')

# Write to file
f = open(reportPath,'w')
f.write(decodedStr)
