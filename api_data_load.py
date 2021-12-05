import json
import requests

li = ['CVE-2018-13114', 'CVE-2018-18026']

url = 'https://services.nvd.nist.gov/rest/json/cve/1.0/'
apiKey = "9e124ed3-052e-490a-83e4-e453999d7432"
# cve id로 검색
params = {'apiKey': apiKey}
res = requests.get(url+li[1], params=params)

print(res)
a = res.json()
print(json.dumps(a,indent=2))
