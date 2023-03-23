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
    oasFile = 'Pixi/pixi.json'
    reportPath = 'Audit/report.rtf'
else: # Local
    x42confPath = '../42c-conf.yaml'
    apikey = config('42C_API_TOKEN')
    oasFile = '../Pixi/pixi.json'
    reportPath = 'report.rtf'

# Open 42c-conf.yaml
with open(x42confPath, 'r') as file:
    confYaml = yaml.safe_load(file)

# Get API uuid from 42c-conf.yaml
uuid = confYaml['audit']['branches']['main']['mapping']['Pixi/pixi.json']

# Set authentication header
headers = {'X-API-KEY': apikey}

# Prepare spec for upload
with open(oasFile,'r') as jsonFile:
    data = json.load(jsonFile)
    datastr = json.dumps(data)
    encodedSpec = base64.b64encode(datastr.encode('utf-8'))

body = {
    'name': data['info']['title'],
    'technicalName': data['info']['description'],
    'specfile': str(encodedSpec,'utf-8'),
    'yaml': False
    }

# Upload API
url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid
r = requests.put(url, data=json.dumps(body), headers=headers)

# Run audit
url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assess'
r = requests.get(url, headers=headers)
jsonResponse = r.json()

# Get taskId
taskId = jsonResponse['id']
time.sleep(2)

# Get audit report
url = 'https://demolabs.42crunch.cloud/api/v1/apis/'+uuid+'/assessmentreport'
r = requests.get(url, headers=headers)
jsonResponse = r.json()

# Decode response
decodedBytes = base64.b64decode(jsonResponse['data'])
decodedStr = decodedBytes.decode('ascii')

# Get audit scores
auditScore = json.loads(decodedStr)['score']
securityScore = json.loads(decodedStr)['security']['score']
dataScore = json.loads(decodedStr)['data']['score']

# Get SQG approval report using taskId
url = 'https://demolabs.42crunch.cloud/api/v2/sqgs/reportComplianceStatus?reportType=audit&taskId='+taskId
r = requests.get(url, headers=headers)
jsonResponse = r.json()
print(jsonResponse)

# Add 42c logo
fileString = '<img src=https://42crunch.com/wp-content/uploads/2022/02/LogoCr1.png width="200" height="57"/>'

# Parse response
if jsonResponse['acceptance'] == 'no':
    sqgPassed = False
    fileString += '\n# Audit SQGs - FAILED :red_circle:'
else:
    sqgPassed = True
    fileString += '\n# Audit SQGs - PASSED :green_circle:'

fileString += '\nTimestamp: '+str(datetime.fromtimestamp(int(jsonResponse['date'])))

fileString += '\n\nReport: https://demolabs.42crunch.cloud/apis/'+jsonResponse['api']+'/security-audit-report'

# Build summary report table
for sqgReport in jsonResponse['processingDetails']:
    # Get SQG by ID
    url = 'https://demolabs.42crunch.cloud/api/v2/sqgs/audit/'+sqgReport['blockingSqgId']
    r = requests.get(url, headers=headers)
    sqgIdJson = r.json()

    fileString += '\n\n## SQG - '+sqgIdJson['name']

    fileString += '\n\n### Minimum acceptable score:'

    # Assign SQG data
    sqgAuditScore = sqgIdJson['directives']['minimumAssessmentScores']['global']
    sqgSecurityScore = sqgIdJson['directives']['minimumAssessmentScores']['security']
    sqgDataScore = sqgIdJson['directives']['minimumAssessmentScores']['dataValidation']
    authenticationRule = sqgIdJson['directives']['subcategoryRules']['security']['authentication']
    authorizationRule = sqgIdJson['directives']['subcategoryRules']['security']['authorization']
    transportRule = sqgIdJson['directives']['subcategoryRules']['security']['transport']
    parametersRule = sqgIdJson['directives']['subcategoryRules']['dataValidation']['parameters']
    responseHeadersRule = sqgIdJson['directives']['subcategoryRules']['dataValidation']['responseHeaders']
    responseDefinitionRule = sqgIdJson['directives']['subcategoryRules']['dataValidation']['responseDefinition']
    schemaRule = sqgIdJson['directives']['subcategoryRules']['dataValidation']['schema']
    pathsRule = sqgIdJson['directives']['subcategoryRules']['dataValidation']['paths']
    issueRules =  sqgIdJson['directives']['issueRules']

    # Build audit score table
    scoreTable = []
    head = ['Score','Current','Minimum Acceptable']

    scoreRow = ['Global score', auditScore, sqgAuditScore]
    scoreTable.append(scoreRow)
    scoreRow = ['Security score', securityScore, sqgSecurityScore]
    scoreTable.append(scoreRow)
    scoreRow = ['Data validation score', dataScore, sqgDataScore]
    scoreTable.append(scoreRow)

    fileString += '\n'+tabulate(scoreTable, headers=head, tablefmt='github')
    fileString += '\n'

    severityTable = []
    head = ['Category','Threshold','Issues Found']

    issuesList = ''
    for count, sqgRule in enumerate(sqgReport['blockingRules']):
        if sqgRule not in issueRules:
            blockingRule = sqgRule.split('/')
            if len(blockingRule) > 1:
                categorySeverity = blockingRule[1].split(':')
                if len(categorySeverity) > 1:
                    category = categorySeverity[0]
                    severity = categorySeverity[1]
                    if category == 'authentication':
                        severityRow = ['Authentication', 'Issues less than '+authenticationRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'authorization':
                        severityRow = ['Authorization', 'Issues less than '+authorizationRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'transport':
                        severityRow = ['Transport', 'Issues less than '+transportRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'parameters':
                        severityRow = ['Parameters', 'Issues less than '+parametersRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'response_headers':
                        severityRow = ['Response Headers', 'Issues less than '+responseHeadersRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'response_definition':
                        severityRow = ['Response Definition', 'Issues less than '+responseDefinitionRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'schema':
                        severityRow = ['Schema', 'Issues less than '+schemaRule+' allowed', severity]
                        severityTable.append(severityRow)
                    elif category == 'paths':
                        severityRow = ['Paths', 'Issues less than '+pathsRule+' allowed', severity]
                        severityTable.append(severityRow)
                    else:
                        severityRow = []
        else:
            issuesList += '\n'+sqgRule

    if len(severityTable) > 0:
        fileString += '\n### Allowed issue security levels:'
        fileString += '\n'+tabulate(severityTable, headers=head, tablefmt='github')
    
    if issuesList != '':
        fileString += '\n### Forbidden issues with problem found:'
        fileString += issuesList

    fileString += '\n'

# Write to file
f = open(reportPath,'w')
f.write(fileString)